from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

from .forms import (
    ClienteAuthenticationForm,
    ClientePerfilForm,
    AdministradorPerfilForm,
    MascotaForm,
    PersonalAuthenticationForm,
    RegistroClienteForm,
    RecepcionistaPerfilForm,
    VeterinarioPerfilForm,
)
from .models import Administrador, Cliente, Mascota, Perfil, Recepcionista, Veterinario



class LoginSelectorView(TemplateView):
    template_name = "usuarios/login_selector.html"


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
        return context


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
