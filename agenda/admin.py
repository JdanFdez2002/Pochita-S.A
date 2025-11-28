from django.contrib import admin

from .models import Cita


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "mascota", "cliente", "veterinario", "servicio", "estado")
    list_filter = ("estado", "fecha", "veterinario", "servicio")
    search_fields = (
        "mascota__nombre",
        "cliente__perfil__user__first_name",
        "cliente__perfil__user__last_name",
        "cliente__perfil__user__email",
        "cliente__rut",
    )
    autocomplete_fields = ("cliente", "mascota", "servicio", "veterinario")
