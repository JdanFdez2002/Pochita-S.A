from django.urls import path
from .views import (
    ClienteLoginView,
    DashboardClienteView,
    DashboardAdministradorView,
    DashboardRecepcionistaView,
    DashboardVeterinarioView,
    LoginSelectorView,
    PersonalLoginView,
    logout_view,
    registro_clientes_view,
)

app_name = "usuarios"

urlpatterns = [
    path("login/", LoginSelectorView.as_view(), name="login_selector"),
    path("login/personal/", PersonalLoginView.as_view(), name="login_personal"),
    path("login/clientes/", ClienteLoginView.as_view(), name="login_clientes"),
    path("registro/clientes/", registro_clientes_view, name="registro_clientes"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/cliente/", DashboardClienteView.as_view(), name="dashboard_cliente"),
    path("dashboard/recepcionista/", DashboardRecepcionistaView.as_view(), name="dashboard_recepcionista"),
    path("dashboard/veterinario/", DashboardVeterinarioView.as_view(), name="dashboard_veterinario"),
    path("dashboard/administrador/", DashboardAdministradorView.as_view(), name="dashboard_administrador"),
]
