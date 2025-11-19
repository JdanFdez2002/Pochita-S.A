from django.urls import path
from .views import LoginSelectorView, PersonalLoginView, ClienteLoginView

app_name = "usuarios"

urlpatterns = [
    path("login/", LoginSelectorView.as_view(), name="login_selector"),
    path("login/personal/", PersonalLoginView.as_view(), name="login_personal"),
    path("login/clientes/", ClienteLoginView.as_view(), name="login_clientes"),
]
