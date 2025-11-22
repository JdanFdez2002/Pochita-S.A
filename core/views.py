from django.views.generic import TemplateView
from django.shortcuts import render


class LandingView(TemplateView):
    template_name = "core/landing.html"


class ServicesView(TemplateView):
    template_name = "core/servicios.html"


class TeamView(TemplateView):
    template_name = "core/equipo.html"


class ContactView(TemplateView):
    template_name = "core/contacto.html"


def error_403(request, exception=None):
    return render(request, "403.html", status=403)
