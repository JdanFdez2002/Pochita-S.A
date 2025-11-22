from django.contrib import admin

from .models import Cliente, Perfil, Personal


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "rol")
    search_fields = ("user__username", "user__email", "rol")
    list_filter = ("rol",)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("perfil", "rut", "telefono", "recibe_noticias")
    search_fields = ("perfil__user__username", "perfil__user__email", "rut")
    list_filter = ("recibe_noticias",)


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ("perfil", "rut", "telefono", "especialidad", "turno")
    search_fields = ("perfil__user__username", "perfil__user__email", "rut", "especialidad", "turno")
    list_filter = ("perfil__rol",)
