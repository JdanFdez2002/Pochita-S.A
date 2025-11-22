from django.contrib.auth.models import User
from django.db import models


class Perfil(models.Model):
    class Roles(models.TextChoices):
        CLIENTE = "cliente", "cliente"
        VETERINARIO = "veterinario", "veterinario"
        RECEPCIONISTA = "recepcionista", "recepcionista"
        ADMINISTRADOR = "administrador", "administrador"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=Roles.choices)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"


class Cliente(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    rut = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=50)
    recibe_noticias = models.BooleanField(default=False)

    def __str__(self):
        return f"Cliente {self.perfil.user.username}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"


class Personal(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    rut = models.CharField(max_length=20)
    telefono = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    especialidad = models.CharField(max_length=255, blank=True, null=True)
    turno = models.CharField(max_length=255, blank=True, null=True)
    permisos_extra = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Personal {self.perfil.user.username}"

    class Meta:
        verbose_name = "Personal"
        verbose_name_plural = "Personal"
