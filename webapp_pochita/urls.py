from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

urlpatterns = [
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
] + (
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + staticfiles_urlpatterns()
    if settings.DEBUG
    else []
)
