from django.contrib import admin

from .models import DiaBloqueadoVeterinario, DisponibilidadVeterinario


@admin.register(DisponibilidadVeterinario)
class DisponibilidadVeterinarioAdmin(admin.ModelAdmin):
    list_display = ("veterinario", "fecha", "hora_inicio", "hora_fin", "estado")
    list_filter = ("estado", "fecha", "veterinario")
    search_fields = (
        "veterinario__perfil__user__first_name",
        "veterinario__perfil__user__last_name",
        "veterinario__perfil__user__email",
    )
    autocomplete_fields = ("veterinario",)
    ordering = ("fecha", "hora_inicio")


@admin.register(DiaBloqueadoVeterinario)
class DiaBloqueadoVeterinarioAdmin(admin.ModelAdmin):
    list_display = ("veterinario", "fecha", "razon")
    list_filter = ("fecha", "veterinario")
    search_fields = (
        "veterinario__perfil__user__first_name",
        "veterinario__perfil__user__last_name",
        "veterinario__perfil__user__email",
        "razon",
    )
    autocomplete_fields = ("veterinario",)
    ordering = ("-fecha",)
