from django.views.generic import TemplateView

<<<<<<< HEAD

class LandingView(TemplateView):
    template_name = "core/landing.html"


class ServicesView(TemplateView):
    template_name = "core/servicios.html"


class TeamView(TemplateView):
    template_name = "core/equipo.html"


class ContactView(TemplateView):
    template_name = "core/contacto.html"
=======
def home(request):
    return render(request, 'core/home.html')
>>>>>>> ec21c5c66944626218901d3105a8b9f6425b2f4d
