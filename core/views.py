from django.views.generic import TemplateView


class LandingView(TemplateView):
    template_name = "core/landing.html"


class ServicesView(TemplateView):
    template_name = "core/servicios.html"


class TeamView(TemplateView):
    template_name = "core/equipo.html"


class ContactView(TemplateView):
    template_name = "core/contacto.html"
