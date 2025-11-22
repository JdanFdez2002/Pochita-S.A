from django.contrib.auth.forms import AuthenticationForm
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


class DashboardClienteView(TemplateView):
    template_name = "usuarios/dashboard_cliente.html"


class DashboardRecepcionistaView(TemplateView):
    template_name = "usuarios/dashboard_recepcionista.html"


class DashboardVeterinarioView(TemplateView):
    template_name = "usuarios/dashboard_veterinario.html"


class DashboardAdministradorView(TemplateView):
    template_name = "usuarios/dashboard_administrador.html"


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
