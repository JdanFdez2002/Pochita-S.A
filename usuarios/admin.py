from django.contrib import admin

from .models import Administrador, Cliente, Perfil, Recepcionista, Veterinario


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "rol")
    search_fields = ("user__username", "user__email", "rol")
    list_filter = ("rol",)
    autocomplete_fields = ("user",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("perfil", "rut", "telefono", "recibe_noticias")
    search_fields = ("perfil__user__username", "perfil__user__email", "rut")
    list_filter = ("recibe_noticias",)
    autocomplete_fields = ("perfil",)


class BaseStaffAdmin(admin.ModelAdmin):
    list_display = ("perfil", "rut", "telefono", "especialidad", "turno")
    search_fields = ("perfil__user__username", "perfil__user__email", "rut", "especialidad", "turno", "permisos_extra")
    list_filter = ("perfil__rol", "turno")
    autocomplete_fields = ("perfil",)
    fieldsets = (
        ("Usuario", {"fields": ("perfil",)}),
        ("Datos personales", {"fields": ("rut", "telefono", "direccion")}),
        ("Rol y horario", {"fields": ("especialidad", "turno", "permisos_extra")}),
    )


@admin.register(Veterinario)
class VeterinarioAdmin(BaseStaffAdmin):
    pass


@admin.register(Recepcionista)
class RecepcionistaAdmin(BaseStaffAdmin):
    pass


@admin.register(Administrador)
class AdministradorAdmin(BaseStaffAdmin):
    pass
