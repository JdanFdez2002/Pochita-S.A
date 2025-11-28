from django.urls import path
from .views import (
    ClienteLoginView,
    DashboardClienteView,
    DashboardAdministradorView,
    DashboardRecepcionistaView,
    DashboardVeterinarioView,
    vet_disponibilidad_api,
    vet_disponibilidad_detail_api,
    vet_bloquear_dia_api,
    vet_citas_api,
    vet_cita_estado_api,
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
    # API Veterinario
    path("api/veterinario/disponibilidad/", vet_disponibilidad_api, name="vet_disponibilidad_api"),
    path("api/veterinario/disponibilidad/<int:pk>/", vet_disponibilidad_detail_api, name="vet_disponibilidad_detail_api"),
    path("api/veterinario/disponibilidad/bloquear-dia/", vet_bloquear_dia_api, name="vet_bloquear_dia_api"),
    path("api/veterinario/citas/", vet_citas_api, name="vet_citas_api"),
    path("api/veterinario/citas/<int:pk>/estado/", vet_cita_estado_api, name="vet_cita_estado_api"),
]
