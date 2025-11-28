import json

from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.utils import timezone

from .forms import (
    ClienteAuthenticationForm,
    ClientePerfilForm,
    AdministradorPerfilForm,
    ServicioForm,
    ServicioSeccionForm,
    MascotaForm,
    PersonalAuthenticationForm,
    RegistroClienteForm,
    RecepcionistaPerfilForm,
    VeterinarioPerfilForm,
)
from .models import (
    Administrador,
    Cliente,
    Mascota,
    Perfil,
    Recepcionista,
    Servicio,
    ServicioSeccion,
    Veterinario,
)
from veterinarios.models import DisponibilidadVeterinario, DiaBloqueadoVeterinario
from agenda.models import Cita



class LoginSelectorView(TemplateView):
    template_name = "usuarios/login_selector.html"


def _require_veterinario(request):
    if not request.user.is_authenticated:
        return HttpResponseForbidden("No autenticado.")
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        return HttpResponseForbidden("Usuario sin perfil.")
    if perfil.rol != Perfil.Roles.VETERINARIO:
        return HttpResponseForbidden("Solo disponible para veterinarios.")
    try:
        return Veterinario.objects.get(perfil=perfil)
    except Veterinario.DoesNotExist:
        return HttpResponseForbidden("Veterinario no encontrado.")


class ClienteLoginView(LoginView):
    template_name = "usuarios/login_clientes.html"
    authentication_form = ClienteAuthenticationForm
    extra_context = {"perfil": "cliente"}
    redirect_authenticated_user = False

    def get_success_url(self):
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return redirect_url
        return reverse_lazy("usuarios:dashboard_cliente")


class PersonalLoginView(LoginView):
    template_name = "usuarios/login_personal.html"
    authentication_form = PersonalAuthenticationForm
    extra_context = {"perfil": "personal"}
    redirect_authenticated_user = False

    def get_success_url(self):
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return redirect_url
        user = self.request.user
        try:
            perfil = user.perfil
        except Perfil.DoesNotExist:
            perfil = None
        if perfil:
            if perfil.rol == "veterinario":
                return reverse_lazy("usuarios:dashboard_veterinario")
            if perfil.rol == "recepcionista":
                return reverse_lazy("usuarios:dashboard_recepcionista")
            if perfil.rol == "administrador":
                return reverse_lazy("usuarios:dashboard_administrador")
        return reverse_lazy("usuarios:login_selector")


class RolRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    required_role = None
    login_url = reverse_lazy("usuarios:login_selector")
    raise_exception = True

    def test_func(self):
        user = self.request.user
        try:
            perfil = user.perfil
        except Perfil.DoesNotExist:
            return False
        return perfil.rol == self.required_role


class PerfilDashboardMixin(RolRequiredMixin, TemplateView):
    """
    Mixin para dashboards que muestra y actualiza los datos del perfil logueado.
    """

    form_class = None
    model = None

    def get_instance(self):
        try:
            return (
                self.model.objects.select_related("perfil__user")
                .get(perfil__user=self.request.user)
            )
        except self.model.DoesNotExist:
            raise Http404("Perfil no encontrado para el usuario logueado.")

    def get_initial(self, instance):
        direccion = getattr(instance, "direccion", "") or ""
        return {
            "email": instance.perfil.user.email,
            "rut": instance.rut,
            "telefono": instance.telefono,
            "direccion": direccion,
        }

    def get_form(self, data=None):
        instance = self.get_instance()
        initial = self.get_initial(instance)
        form = self.form_class(
            user=self.request.user, instance=instance, data=data, initial=initial
        )
        if data is None:
            for field in form.fields.values():
                field.widget.attrs["disabled"] = True
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form" not in context:
            context["form"] = self.get_form()
        context["profile_saved"] = kwargs.get("profile_saved", False)
        context["form_has_errors"] = kwargs.get(
            "form_has_errors", bool(context["form"].errors)
        )
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST)
        if form.is_valid():
            form.save()
            # recargar valores actualizados y bloquear campos
            fresh_form = self.get_form()
            return self.render_to_response(
                self.get_context_data(form=fresh_form, profile_saved=True)
            )
        return self.render_to_response(
            self.get_context_data(form=form, form_has_errors=True)
        )


class DashboardClienteView(PerfilDashboardMixin):
    required_role = Perfil.Roles.CLIENTE
    login_url = reverse_lazy("usuarios:login_clientes")
    template_name = "usuarios/cliente/dashboard.html"
    model = Cliente
    form_class = ClientePerfilForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cliente = self.get_instance()
        context.setdefault(
            "mascotas",
            Mascota.objects.filter(cliente=cliente).order_by("nombre"),
        )
        context.setdefault("mascota_form", MascotaForm())
        context["servicio_secciones"] = (
            ServicioSeccion.objects.filter(activo=True)
            .prefetch_related("servicios")
            .order_by("orden", "nombre")
        )
        context["servicios"] = (
            Servicio.objects.filter(activo=True, seccion__activo=True)
            .select_related("seccion")
            .order_by("seccion__orden", "nombre")
        )
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("form_type") == "mascota":
            cliente = self.get_instance()
            form = MascotaForm(request.POST, request.FILES)
            if form.is_valid():
                mascota = form.save(commit=False)
                mascota.cliente = cliente
                mascota.save()
                return redirect(reverse("usuarios:dashboard_cliente") + "#sec-mascotas")
            context = self.get_context_data()
            context["mascota_form"] = form
            return self.render_to_response(context)
        if request.POST.get("form_type") == "delete_mascota":
            cliente = self.get_instance()
            mascota_id = request.POST.get("mascota_id")
            confirm_name = (request.POST.get("confirm_name") or "").strip().lower()
            mascota = Mascota.objects.filter(id=mascota_id, cliente=cliente).first()
            if mascota and confirm_name == (mascota.nombre or "").strip().lower():
                mascota.delete()
                return redirect(reverse("usuarios:dashboard_cliente") + "#sec-mascotas")
            context = self.get_context_data()
            if mascota:
                context["delete_error_id"] = mascota.id
            context["delete_error"] = "El nombre no coincide."
            return self.render_to_response(context)
        return super().post(request, *args, **kwargs)


class DashboardRecepcionistaView(PerfilDashboardMixin):
    required_role = Perfil.Roles.RECEPCIONISTA
    login_url = reverse_lazy("usuarios:login_personal")
    template_name = "usuarios/recepcionista/dashboard.html"
    model = Recepcionista
    form_class = RecepcionistaPerfilForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = (self.request.GET.get("q") or "").strip()
        clientes_qs = (
            Cliente.objects.select_related("perfil__user")
            .prefetch_related("mascotas")
            .order_by("perfil__user__last_name", "perfil__user__first_name", "perfil__user__username")
        )
        if query:
            clientes_qs = clientes_qs.filter(
                Q(perfil__user__first_name__icontains=query)
                | Q(perfil__user__last_name__icontains=query)
                | Q(perfil__user__username__icontains=query)
                | Q(perfil__user__email__icontains=query)
                | Q(rut__icontains=query)
                | Q(telefono__icontains=query)
                | Q(mascotas__nombre__icontains=query)
            ).distinct()
        paginator = Paginator(clientes_qs, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["clientes_page"] = page_obj
        context["query"] = query
        context["servicio_secciones"] = (
            ServicioSeccion.objects.filter(activo=True)
            .prefetch_related("servicios")
            .order_by("orden", "nombre")
        )
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get("form_type") == "editar_cliente":
            cliente_id = request.POST.get("cliente_id")
            try:
                cliente = Cliente.objects.select_related("perfil__user").get(id=cliente_id)
            except Cliente.DoesNotExist:
                return redirect(reverse("usuarios:dashboard_recepcionista") + "#sec-usuarios")
            user = cliente.perfil.user
            # Actualizar datos permitidos (rut no editable)
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            email = request.POST.get("email", user.email)
            if email:
                user.email = email
                user.username = email
            cliente.telefono = request.POST.get("telefono", cliente.telefono)
            cliente.direccion = request.POST.get("direccion", cliente.direccion)
            user.save(update_fields=["first_name", "last_name", "email", "username"])
            cliente.save(update_fields=["telefono", "direccion"])
            return redirect(reverse("usuarios:dashboard_recepcionista") + "#sec-usuarios")
        return super().post(request, *args, **kwargs)


class DashboardVeterinarioView(PerfilDashboardMixin):
    required_role = Perfil.Roles.VETERINARIO
    login_url = reverse_lazy("usuarios:login_personal")
    template_name = "usuarios/veterinario/dashboard.html"
    model = Veterinario
    form_class = VeterinarioPerfilForm

    def get_initial(self, instance):
        base = super().get_initial(instance)
        base.update(
            {
                "especialidad": instance.especialidad or "",
                "turno": instance.turno or "",
            }
        )
        return base

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vet = self.get_instance()
        bloques = (
            DisponibilidadVeterinario.objects.filter(veterinario=vet)
            .order_by("fecha", "hora_inicio")
        )
        dias_bloqueados = DiaBloqueadoVeterinario.objects.filter(veterinario=vet)
        citas = (
            Cita.objects.filter(veterinario=vet)
            .select_related(
                "cliente__perfil__user",
                "mascota",
                "servicio",
            )
            .order_by("fecha", "hora")
        )
        data = {
            "disponibilidad": [
                {
                    "id": b.id,
                    "fecha": b.fecha.isoformat(),
                    "inicio": b.hora_inicio.strftime("%H:%M"),
                    "fin": b.hora_fin.strftime("%H:%M"),
                    "estado": b.estado,
                }
                for b in bloques
            ],
            "dias_bloqueados": [d.fecha.isoformat() for d in dias_bloqueados],
            "citas": [
                {
                    "id": c.id,
                    "fecha": c.fecha.isoformat(),
                    "hora": c.hora.strftime("%H:%M"),
                    "cliente": c.cliente.perfil.user.get_full_name() or c.cliente.perfil.user.username,
                    "contacto": c.cliente.telefono,
                    "mascota": c.mascota.nombre,
                    "especie": c.mascota.tipo,
                    "edad": f"{c.mascota.edad_aproximada or ''}".strip(),
                    "servicio": c.servicio.nombre if c.servicio else "",
                    "estado": c.estado,
                    "notas": c.notas or "",
                }
                for c in citas
            ],
        }
        context["vet_data_json"] = json.dumps(data)
        return context


class DashboardAdministradorView(PerfilDashboardMixin):
    required_role = Perfil.Roles.ADMINISTRADOR
    login_url = reverse_lazy("usuarios:login_personal")
    template_name = "usuarios/administrador/dashboard.html"
    model = Administrador
    form_class = AdministradorPerfilForm

    def get_initial(self, instance):
        base = super().get_initial(instance)
        base["empresa_representante"] = instance.empresa_representante or ""
        return base

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["servicio_seccion_form"] = kwargs.get(
            "servicio_seccion_form", ServicioSeccionForm()
        )
        context["servicio_form"] = kwargs.get("servicio_form", ServicioForm())
        context["servicio_secciones"] = (
            ServicioSeccion.objects.all()
            .prefetch_related("servicios")
            .order_by("orden", "nombre")
        )
        context["servicios"] = Servicio.objects.select_related("seccion").all()
        context["servicios_sin_seccion"] = (
            Servicio.objects.filter(seccion__isnull=True)
            .select_related("seccion")
            .order_by("nombre")
        )
        return context

    def post(self, request, *args, **kwargs):
        form_type = request.POST.get("form_type")
        redirect_url = reverse("usuarios:dashboard_administrador") + "#sec-servicios"

        if form_type == "create_section":
            form = ServicioSeccionForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect(redirect_url)
            return self.render_to_response(
                self.get_context_data(servicio_seccion_form=form, servicio_form=ServicioForm())
            )

        if form_type == "delete_section":
            section_id = request.POST.get("section_id")
            ServicioSeccion.objects.filter(id=section_id).delete()
            return redirect(redirect_url)

        if form_type == "update_section":
            section_id = request.POST.get("section_id")
            instance = ServicioSeccion.objects.filter(id=section_id).first()
            if instance:
                form = ServicioSeccionForm(request.POST, instance=instance)
                if form.is_valid():
                    form.save()
                    return redirect(redirect_url)
            return self.render_to_response(self.get_context_data())

        if form_type == "reassign_service":
            service_id = request.POST.get("service_id")
            section_id = request.POST.get("seccion_id")
            servicio = Servicio.objects.filter(id=service_id).first()
            if servicio:
                seccion = (
                    ServicioSeccion.objects.filter(id=section_id).first()
                    if section_id
                    else None
                )
                servicio.seccion = seccion
                servicio.save(update_fields=["seccion"])
            return redirect(redirect_url)

        if form_type == "create_service" or form_type == "update_service":
            service_id = request.POST.get("service_id")
            instance = Servicio.objects.filter(id=service_id).first() if service_id else None
            form = ServicioForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                return redirect(redirect_url)
            return self.render_to_response(
                self.get_context_data(servicio_form=form, servicio_seccion_form=ServicioSeccionForm())
            )

        if form_type == "delete_service":
            service_id = request.POST.get("service_id")
            Servicio.objects.filter(id=service_id).delete()
            return redirect(redirect_url)

        return super().post(request, *args, **kwargs)


def registro_clientes_view(request):
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("usuarios:login_clientes")
    else:
        form = RegistroClienteForm()
    context = {"form": form}
    return render(request, "usuarios/registro_clientes.html", context)


def logout_view(request):
    """
    Cierra la sesión del usuario y lo envía al selector de inicio de sesión.
    Se usa para todos los roles desde los enlaces de "Cerrar sesión/turno".
    """
    logout(request)
    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("usuarios:login_selector")


def csrf_failure(request, reason="", template_name=None):
    registro_url = reverse("usuarios:registro_clientes")
    if request.path.startswith(registro_url):
        form = RegistroClienteForm(request.POST or None)
        form.add_error(None, "Hubo un problema de seguridad, por favor intenta nuevamente.")
        context = {"form": form}
        return render(request, "usuarios/registro_clientes.html", context, status=403)
    return render(request, template_name or "403.html", {"reason": reason}, status=403)


# === API Veterinario: Disponibilidad y Citas ===

def _parse_json(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return {}


def _serialize_bloque(b):
    return {
        "id": b.id,
        "fecha": b.fecha.isoformat(),
        "inicio": b.hora_inicio.strftime("%H:%M"),
        "fin": b.hora_fin.strftime("%H:%M"),
        "estado": b.estado,
    }


def _serialize_cita(c):
    return {
        "id": c.id,
        "fecha": c.fecha.isoformat(),
        "hora": c.hora.strftime("%H:%M"),
        "cliente": c.cliente.perfil.user.get_full_name()
        or c.cliente.perfil.user.username,
        "contacto": c.cliente.telefono,
        "mascota": c.mascota.nombre,
        "especie": c.mascota.tipo,
        "edad": f"{c.mascota.edad_aproximada or ''}".strip(),
        "servicio": c.servicio.nombre if c.servicio else "",
        "estado": c.estado,
        "notas": c.notas or "",
    }


@require_http_methods(["GET", "POST"])
def vet_disponibilidad_api(request):
    vet = _require_veterinario(request)
    if isinstance(vet, HttpResponseForbidden):
        return vet
    if request.method == "GET":
        bloques = DisponibilidadVeterinario.objects.filter(veterinario=vet).order_by(
            "fecha", "hora_inicio"
        )
        dias = DiaBloqueadoVeterinario.objects.filter(veterinario=vet).order_by("fecha")
        return JsonResponse(
            {
                "bloques": [_serialize_bloque(b) for b in bloques],
                "dias_bloqueados": [d.fecha.isoformat() for d in dias],
            }
        )

    data = _parse_json(request)
    fecha = data.get("fecha")
    inicio = data.get("inicio") or data.get("hora_inicio")
    fin = data.get("fin") or data.get("hora_fin")
    estado = data.get("estado") or DisponibilidadVeterinario.Estado.DISPONIBLE
    if not all([fecha, inicio, fin]):
        return HttpResponseBadRequest("Faltan datos obligatorios.")
    bloque = DisponibilidadVeterinario(
        veterinario=vet, fecha=fecha, hora_inicio=inicio, hora_fin=fin, estado=estado
    )
    try:
        bloque.save()
    except Exception as exc:
        return HttpResponseBadRequest(str(exc))
    return JsonResponse({"bloque": _serialize_bloque(bloque)}, status=201)


@require_http_methods(["PUT", "PATCH", "DELETE"])
def vet_disponibilidad_detail_api(request, pk):
    vet = _require_veterinario(request)
    if isinstance(vet, HttpResponseForbidden):
        return vet
    try:
        bloque = DisponibilidadVeterinario.objects.get(pk=pk, veterinario=vet)
    except DisponibilidadVeterinario.DoesNotExist:
        return HttpResponseBadRequest("Bloque no encontrado.")

    if request.method == "DELETE":
        bloque.delete()
        return JsonResponse({"deleted": True})

    data = _parse_json(request)
    if "fecha" in data:
        bloque.fecha = data["fecha"]
    if "inicio" in data or "hora_inicio" in data:
        bloque.hora_inicio = data.get("inicio") or data.get("hora_inicio")
    if "fin" in data or "hora_fin" in data:
        bloque.hora_fin = data.get("fin") or data.get("hora_fin")
    if "estado" in data:
        bloque.estado = data["estado"]
    try:
        bloque.save()
    except Exception as exc:
        return HttpResponseBadRequest(str(exc))
    return JsonResponse({"bloque": _serialize_bloque(bloque)})


@require_http_methods(["POST"])
def vet_bloquear_dia_api(request):
    vet = _require_veterinario(request)
    if isinstance(vet, HttpResponseForbidden):
        return vet
    data = _parse_json(request)
    fecha = data.get("fecha")
    accion = data.get("accion") or "toggle"
    if not fecha:
        return HttpResponseBadRequest("Fecha requerida.")
    if str(timezone.now().date()) > str(fecha):
        return HttpResponseBadRequest("No puedes modificar dias pasados.")

    try:
        bloqueo = DiaBloqueadoVeterinario.objects.get(veterinario=vet, fecha=fecha)
        if accion in ("desbloquear", "toggle"):
            bloqueo.delete()
            return JsonResponse({"bloqueado": False})
    except DiaBloqueadoVeterinario.DoesNotExist:
        bloqueo = None

    if bloqueo is None:
        DiaBloqueadoVeterinario.objects.get_or_create(veterinario=vet, fecha=fecha)
    return JsonResponse({"bloqueado": True})


@require_http_methods(["GET"])
def vet_citas_api(request):
    vet = _require_veterinario(request)
    if isinstance(vet, HttpResponseForbidden):
        return vet
    citas = (
        Cita.objects.filter(veterinario=vet)
        .select_related("cliente__perfil__user", "mascota", "servicio")
        .order_by("fecha", "hora")
    )
    return JsonResponse({"citas": [_serialize_cita(c) for c in citas]})


@require_http_methods(["POST"])
def vet_cita_estado_api(request, pk):
    vet = _require_veterinario(request)
    if isinstance(vet, HttpResponseForbidden):
        return vet
    try:
        cita = Cita.objects.get(pk=pk, veterinario=vet)
    except Cita.DoesNotExist:
        return HttpResponseBadRequest("Cita no encontrada.")
    data = _parse_json(request)
    estado = data.get("estado")
    if estado not in dict(Cita.Estado.choices):
        return HttpResponseBadRequest("Estado invalido.")
    cita.estado = estado
    cita.save(update_fields=["estado", "actualizado_en"])
    return JsonResponse({"cita": _serialize_cita(cita)})
