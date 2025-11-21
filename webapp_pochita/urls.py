
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("", include("core.urls")),
    path(
        "usuarios/",
        include(("usuarios.urls", "usuarios"), namespace="usuarios"),
    ),
    path("login/", RedirectView.as_view(pattern_name="usuarios:login_selector", permanent=False)),
    path("login/clientes/", RedirectView.as_view(pattern_name="usuarios:login_clientes", permanent=False)),
    path("login/personal/", RedirectView.as_view(pattern_name="usuarios:login_personal", permanent=False)),
    path("admin/", admin.site.urls),
] + (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + staticfiles_urlpatterns()
    if settings.DEBUG
    else []
)
