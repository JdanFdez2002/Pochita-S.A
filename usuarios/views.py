from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.generic import TemplateView

from .forms import RegistroClienteForm


class LoginSelectorView(TemplateView):
    template_name = "usuarios/login_selector.html"


class ClienteLoginView(LoginView):
    template_name = "usuarios/login_clientes.html"
    authentication_form = AuthenticationForm
    extra_context = {"perfil": "cliente"}
    redirect_authenticated_user = False


class PersonalLoginView(LoginView):
    template_name = "usuarios/login_personal.html"
    authentication_form = AuthenticationForm
    extra_context = {"perfil": "personal"}
    redirect_authenticated_user = False


def registro_clientes_view(request):
    if request.method == "POST":
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("usuarios:login_clientes")
    else:
        form = RegistroClienteForm()
    return render(request, "usuarios/registro_clientes.html", {"form": form})
