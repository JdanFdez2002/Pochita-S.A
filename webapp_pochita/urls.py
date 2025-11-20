<<<<<<< HEAD
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
    path("admin/", admin.site.urls),
] + (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + staticfiles_urlpatterns()
    if settings.DEBUG
    else []
)
=======
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),    
    path('', include('core.urls')),
]
>>>>>>> ec21c5c66944626218901d3105a8b9f6425b2f4d
