from django.db import models
from django.utils.translation import gettext_lazy as _

from usuarios.models import Cliente, Mascota, Servicio, Veterinario


class Cita(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADA = "confirmada", "Confirmada"
        ATENDIDA = "atendida", "Atendida"
        CANCELADA = "cancelada", "Cancelada"

    veterinario = models.ForeignKey(
        Veterinario, on_delete=models.CASCADE, related_name="citas"
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE, related_name="citas"
    )
    mascota = models.ForeignKey(
        Mascota, on_delete=models.CASCADE, related_name="citas"
    )
    servicio = models.ForeignKey(
        Servicio, on_delete=models.SET_NULL, null=True, blank=True, related_name="citas"
    )
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.PENDIENTE
    )
    notas = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ["fecha", "hora"]

    def __str__(self):
        return f"Cita {self.fecha} {self.hora} - {self.mascota} ({self.estado})"
