from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

from .forms import RegistroClienteForm
from .models import Perfil


class LoginSelectorView(TemplateView):
    template_name = "usuarios/login_selector.html"


class ClienteLoginView(LoginView):
    template_name = "usuarios/login_clientes.html"
    authentication_form = AuthenticationForm
    extra_context = {"perfil": "cliente"}
    redirect_authenticated_user = False

    def get_success_url(self):
        redirect_url = self.get_redirect_url()
        if redirect_url:
            return redirect_url
        return reverse_lazy("usuarios:dashboard_cliente")


class PersonalLoginView(LoginView):
    template_name = "usuarios/login_personal.html"
    authentication_form = AuthenticationForm
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


class DashboardClienteView(RolRequiredMixin, TemplateView):
    required_role = Perfil.Roles.CLIENTE
    login_url = reverse_lazy("usuarios:login_clientes")
    template_name = "usuarios/cliente/dashboard.html"


class DashboardRecepcionistaView(RolRequiredMixin, TemplateView):
    required_role = Perfil.Roles.RECEPCIONISTA
    login_url = reverse_lazy("usuarios:login_personal")
    template_name = "usuarios/recepcionista/dashboard.html"


class DashboardVeterinarioView(RolRequiredMixin, TemplateView):
    required_role = Perfil.Roles.VETERINARIO
    login_url = reverse_lazy("usuarios:login_personal")
    template_name = "usuarios/veterinario/dashboard.html"


class DashboardAdministradorView(RolRequiredMixin, TemplateView):
    required_role = Perfil.Roles.ADMINISTRADOR
    login_url = reverse_lazy("usuarios:login_personal")
    template_name = "usuarios/administrador/dashboard.html"


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


def csrf_failure(request, reason="", template_name=None):
    registro_url = reverse("usuarios:registro_clientes")
    if request.path.startswith(registro_url):
        form = RegistroClienteForm(request.POST or None)
        form.add_error(None, "Hubo un problema de seguridad, por favor intenta nuevamente.")
        context = {"form": form}
        return render(request, "usuarios/registro_clientes.html", context, status=403)
    return render(request, template_name or "403.html", {"reason": reason}, status=403)
