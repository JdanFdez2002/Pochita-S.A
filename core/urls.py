from django.urls import path
from .views import ContactView, LandingView, ServicesView, TeamView

app_name = "core"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("servicios/", ServicesView.as_view(), name="servicios"),
    path("equipo/", TeamView.as_view(), name="equipo"),
    path("contacto/", ContactView.as_view(), name="contacto"),
]