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


class Cliente(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    rut = models.CharField(max_length=20)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=50)
    recibe_noticias = models.BooleanField(default=False)

    def __str__(self):
        return f"Cliente {self.perfil.user.username}"
