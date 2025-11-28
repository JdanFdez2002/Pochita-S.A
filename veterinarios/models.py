from datetime import date
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from usuarios.models import Veterinario


class DisponibilidadVeterinario(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "disponible", "Disponible"
        NO_DISPONIBLE = "no_disponible", "No disponible"
        BLOQUEADO = "bloqueado", "Bloqueado"

    veterinario = models.ForeignKey(
        Veterinario, on_delete=models.CASCADE, related_name="disponibilidades"
    )
    fecha = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    estado = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.DISPONIBLE
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Disponibilidad de Veterinario"
        verbose_name_plural = "Disponibilidades de Veterinario"
        ordering = ["fecha", "hora_inicio"]

    def __str__(self):
        return f"{self.veterinario} {self.fecha} {self.hora_inicio}-{self.hora_fin} ({self.estado})"

    def clean(self):
        super().clean()
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError(_("La hora fin debe ser mayor que la hora inicio."))
        if self.fecha < date.today():
            raise ValidationError(_("No se puede crear disponibilidad en dias pasados."))
        # Validar traslapes
        qs = DisponibilidadVeterinario.objects.filter(
            veterinario=self.veterinario, fecha=self.fecha
        )
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        for other in qs:
            if self.hora_inicio < other.hora_fin and self.hora_fin > other.hora_inicio:
                raise ValidationError(
                    _("Existe otro bloque que se traslapa en la misma fecha.")
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class DiaBloqueadoVeterinario(models.Model):
    veterinario = models.ForeignKey(
        Veterinario, on_delete=models.CASCADE, related_name="dias_bloqueados"
    )
    fecha = models.DateField()
    razon = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dia bloqueado"
        verbose_name_plural = "Dias bloqueados"
        unique_together = ("veterinario", "fecha")
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.veterinario} bloqueado {self.fecha}"
