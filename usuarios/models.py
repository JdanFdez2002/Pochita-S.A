from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


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


class PersonalBase(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE)
    rut = models.CharField(max_length=20)
    telefono = models.CharField(max_length=50)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    especialidad = models.CharField(max_length=255, blank=True, null=True)
    turno = models.CharField(max_length=255, blank=True, null=True)
    permisos_extra = models.CharField(max_length=255, blank=True, null=True)

    ROLE = None  # Debe definirse en cada subclase

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} {self.perfil.user.username}"

    def save(self, *args, **kwargs):
        if self.ROLE and self.perfil and self.perfil.rol != self.ROLE:
            self.perfil.rol = self.ROLE
            self.perfil.save(update_fields=["rol"])
        super().save(*args, **kwargs)


class Veterinario(PersonalBase):
    ROLE = Perfil.Roles.VETERINARIO

    class Meta:
        verbose_name = "Veterinario"
        verbose_name_plural = "Veterinarios"


class Recepcionista(PersonalBase):
    ROLE = Perfil.Roles.RECEPCIONISTA

    class Meta:
        verbose_name = "Recepcionista"
        verbose_name_plural = "Recepcionistas"


class Administrador(PersonalBase):
    ROLE = Perfil.Roles.ADMINISTRADOR

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"


@receiver(post_save, sender=User)
def crear_perfil_automatico(sender, instance, created, **kwargs):
    """
    Crea un Perfil por defecto (rol cliente) cuando se crea un usuario nuevo.
    Facilita que luego se asocie a Cliente o a un rol de personal sin crear el perfil a mano.
    """
    if not created:
        return
    Perfil.objects.get_or_create(user=instance, defaults={"rol": Perfil.Roles.CLIENTE})
