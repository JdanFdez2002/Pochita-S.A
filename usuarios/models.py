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
    empresa_representante = models.CharField(max_length=255, blank=True, null=True)
    ROLE = Perfil.Roles.ADMINISTRADOR

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"


class Mascota(models.Model):
    class EstadoReproductivo(models.TextChoices):
        SIN_CASTRAR = "sin_castrar", "Sin castrar"
        ESTERILIZADO = "esterilizado", "Esterilizado"
        DESCONOCIDO = "desconocido", "Desconocido"

    class Tipo(models.TextChoices):
        PERRO = "perro", "Perro"
        GATO = "gato", "Gato"
        PEZ = "pez", "Pez"
        PAJARO = "pajaro", "Pajaro"
        REPTIL = "reptil", "Reptil"
        ANFIBIO = "anfibio", "Anfibio"
        CONEJO = "conejo", "Conejo"
        LIEBRE = "liebre", "Liebre"
        HAMSTER = "hamster", "Hamster"
        HURON = "huron", "Huron"
        ERIZO = "erizo", "Erizo"
        OTRO = "otro", "Otro"

    class Sexo(models.TextChoices):
        MACHO = "macho", "Macho"
        HEMBRA = "hembra", "Hembra"
        DESCONOCIDO = "desconocido", "Desconocido"

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="mascotas")
    nombre = models.CharField(max_length=120)
    tipo = models.CharField(max_length=20, choices=Tipo.choices)
    sexo = models.CharField(max_length=20, choices=Sexo.choices, default=Sexo.DESCONOCIDO)
    edad_aproximada = models.PositiveIntegerField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    senas_particulares = models.TextField(blank=True)
    raza = models.CharField(max_length=120, blank=True)
    foto = models.ImageField(upload_to="mascotas/", blank=True, null=True)
    estado_reproductivo = models.CharField(
        max_length=20,
        choices=EstadoReproductivo.choices,
        default=EstadoReproductivo.DESCONOCIDO,
    )
    microchip = models.CharField(max_length=50, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"

    @property
    def tiene_ficha_clinica(self):
        """
        Determina si existe una ficha clínica asociada. Evita dependencias
        circulares usando apps.get_model; si no existe el modelo retorna False.
        """
        from django.apps import apps

        try:
            FichaClinica = apps.get_model("veterinarios", "FichaClinica")
        except LookupError:
            return False
        return FichaClinica.objects.filter(mascota=self).exists()

    def delete(self, *args, **kwargs):
        # Elimina la foto asociada del almacenamiento al borrar la mascota
        if self.foto and self.foto.name:
            self.foto.delete(save=False)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"


class ServicioSeccion(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    orden = models.PositiveIntegerField(default=0)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Seccion de Servicio"
        verbose_name_plural = "Secciones de Servicios"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    seccion = models.ForeignKey(
        ServicioSeccion, on_delete=models.SET_NULL, null=True, blank=True, related_name="servicios"
    )
    precio_referencial = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    unidad_precio = models.CharField(
        max_length=50, blank=True, help_text="Ej: por visita, por dosis, por día"
    )
    duracion_minutos = models.PositiveIntegerField(blank=True, null=True)
    destacado = models.BooleanField(default=False)
    etiquetas = models.CharField(
        max_length=255, blank=True, help_text="Separar con comas (ej: incluye certificado, 24/7)"
    )
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"


@receiver(post_save, sender=User)
def crear_perfil_automatico(sender, instance, created, **kwargs):
    """
    Crea un Perfil por defecto (rol cliente) cuando se crea un usuario nuevo.
    Facilita que luego se asocie a Cliente o a un rol de personal sin crear el perfil a mano.
    """
    if not created:
        return
    Perfil.objects.get_or_create(user=instance, defaults={"rol": Perfil.Roles.CLIENTE})
