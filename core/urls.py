from django.urls import path
<<<<<<< HEAD
from .views import ContactView, LandingView, ServicesView, TeamView

app_name = "core"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
    path("servicios/", ServicesView.as_view(), name="servicios"),
    path("equipo/", TeamView.as_view(), name="equipo"),
    path("contacto/", ContactView.as_view(), name="contacto"),
]
=======
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
]
>>>>>>> ec21c5c66944626218901d3105a8b9f6425b2f4d
