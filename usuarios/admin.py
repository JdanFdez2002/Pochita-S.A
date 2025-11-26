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
    search_fields = ("perfil__user__username", "perfil__user__email", "rut", "especialidad", "turno")
    fieldsets = (
        ("Usuario", {"fields": ("perfil",)}),
        ("Datos personales", {"fields": ("rut", "telefono", "direccion")}),
        ("Rol y horario", {"fields": ("especialidad", "turno")}),
    )
    exclude = ("permisos_extra",)


@admin.register(Recepcionista)
class RecepcionistaAdmin(admin.ModelAdmin):
    list_display = ("perfil", "rut", "telefono")
    search_fields = ("perfil__user__username", "perfil__user__email", "rut")
    list_filter = ("perfil__rol",)
    autocomplete_fields = ("perfil",)
    fieldsets = (
        ("Usuario", {"fields": ("perfil",)}),
        ("Datos personales", {"fields": ("rut", "telefono", "direccion")}),
    )
    exclude = ("especialidad", "turno", "permisos_extra")


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ("perfil", "rut", "telefono", "empresa_representante")
    search_fields = (
        "perfil__user__username",
        "perfil__user__email",
        "rut",
        "empresa_representante",
    )
    list_filter = ("perfil__rol",)
    autocomplete_fields = ("perfil",)
    fieldsets = (
        ("Usuario", {"fields": ("perfil",)}),
        ("Datos personales", {"fields": ("rut", "telefono", "direccion", "empresa_representante")}),
    )
    exclude = ("especialidad", "turno", "permisos_extra")
