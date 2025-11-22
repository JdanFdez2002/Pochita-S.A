from django.urls import path
from .views import (
    ClienteLoginView,
    LoginSelectorView,
    PersonalLoginView,
    registro_clientes_view,
)

app_name = "usuarios"

urlpatterns = [
    path("login/", LoginSelectorView.as_view(), name="login_selector"),
    path("login/personal/", PersonalLoginView.as_view(), name="login_personal"),
    path("login/clientes/", ClienteLoginView.as_view(), name="login_clientes"),
    path("registro/clientes/", registro_clientes_view, name="registro_clientes"),
]
