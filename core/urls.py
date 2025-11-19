from django.urls import path
from .views import LandingView

app_name = "core"

urlpatterns = [
    path("", LandingView.as_view(), name="landing"),
]

