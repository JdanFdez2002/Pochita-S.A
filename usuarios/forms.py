from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from .models import Administrador, Cliente, Perfil, Recepcionista, Veterinario


class RegistroClienteForm(forms.Form):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    rut = forms.CharField(max_length=50)
    direccion = forms.CharField(max_length=255)
    telefono = forms.CharField(max_length=50)
    recibe_noticias = forms.BooleanField(required=False)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            msg = "Este correo ya esta registrado."
            self.add_error(None, msg)
            raise forms.ValidationError(msg)
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contrasenas no coinciden.")
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        with transaction.atomic():
            user = User(
                username=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
            )
            user.set_password(data["password1"])
            user.save()

            perfil, _ = Perfil.objects.get_or_create(
                user=user, defaults={"rol": Perfil.Roles.CLIENTE}
            )
            if perfil.rol != Perfil.Roles.CLIENTE:
                perfil.rol = Perfil.Roles.CLIENTE
                perfil.save(update_fields=["rol"])

            Cliente.objects.create(
                perfil=perfil,
                rut=data["rut"],
                direccion=data["direccion"],
                telefono=data["telefono"],
                recibe_noticias=data.get("recibe_noticias", False),
            )
        return user


class PersonalAuthenticationForm(AuthenticationForm):
    """
    Bloquea el acceso de cuentas que no tengan rol de personal y muestra
    un mensaje con link al login de clientes.
    """

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        try:
            perfil = user.perfil
        except Perfil.DoesNotExist:
            perfil = None

        allowed = {
            Perfil.Roles.VETERINARIO,
            Perfil.Roles.RECEPCIONISTA,
            Perfil.Roles.ADMINISTRADOR,
        }
        if not perfil or perfil.rol not in allowed:
            link = reverse_lazy("usuarios:login_clientes")
            msg = mark_safe(
                f'Tu usuario no es parte del personal. '
                f'<a href="{link}" style="color:#60a5fa;">Volver a login cliente</a>'
            )
            raise forms.ValidationError(msg, code="no_staff")


class ClienteAuthenticationForm(AuthenticationForm):
    """
    Bloquea el acceso de cuentas que no sean clientes y muestra mensaje simple.
    """

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        try:
            perfil = user.perfil
        except Perfil.DoesNotExist:
            perfil = None
        if not perfil or perfil.rol != Perfil.Roles.CLIENTE:
            msg = "Esta cuenta no esta registrada como cliente."
            raise forms.ValidationError(msg, code="no_cliente")


class BasePerfilForm(forms.Form):
    """
    Formulario base para editar datos propios del usuario desde el dashboard.
    Valida correo unico y centraliza la actualizacion del User.
    """

    email = forms.EmailField(label="Correo")
    rut = forms.CharField(max_length=20, label="RUT")
    telefono = forms.CharField(max_length=50, label="Telefono")
    direccion = forms.CharField(max_length=255, label="Direccion", required=False)
    locked_fields = ("email", "rut")

    def __init__(self, user, instance, *args, **kwargs):
        self.user = user
        self.instance = instance
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("data-editable", "1")
            field.widget.attrs.setdefault("autocomplete", "off")
        for name in self.locked_fields:
            if name in self.fields:
                self.fields[name].disabled = True
                self.fields[name].widget.attrs["data-locked"] = "1"

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            exists = User.objects.exclude(pk=self.user.pk).filter(email=email).exists()
            if exists:
                msg = "Este correo ya esta registrado."
                raise forms.ValidationError(msg)
        return email

    def clean(self):
        cleaned = super().clean()
        for name in self.locked_fields:
            if name in cleaned and name in self.initial:
                if cleaned.get(name) != self.initial.get(name):
                    self.add_error(name, "Este campo no se puede editar.")
                    cleaned[name] = self.initial.get(name)
        return cleaned

    def save_user(self, email):
        if email and (self.user.email != email or self.user.username != email):
            self.user.email = email
            self.user.username = email
            self.user.save(update_fields=["email", "username"])


class ClientePerfilForm(BasePerfilForm):
    direccion = forms.CharField(max_length=255, label="Direccion", required=True)

    def save(self):
        data = self.cleaned_data
        cliente = self.instance
        self.save_user(data["email"])
        cliente.rut = data["rut"]
        cliente.telefono = data["telefono"]
        cliente.direccion = data["direccion"]
        cliente.save(update_fields=["rut", "telefono", "direccion"])
        return cliente


class RecepcionistaPerfilForm(BasePerfilForm):
    def save(self):
        data = self.cleaned_data
        recepcionista = self.instance
        self.save_user(data["email"])
        recepcionista.rut = data["rut"]
        recepcionista.telefono = data["telefono"]
        recepcionista.direccion = data.get("direccion") or ""
        recepcionista.save(update_fields=["rut", "telefono", "direccion"])
        return recepcionista


class VeterinarioPerfilForm(BasePerfilForm):
    locked_fields = BasePerfilForm.locked_fields + ("especialidad", "turno")
    especialidad = forms.CharField(max_length=255, label="Especialidad", required=False)
    turno = forms.CharField(max_length=255, label="Turno", required=False)

    def save(self):
        data = self.cleaned_data
        veterinario = self.instance
        self.save_user(data["email"])
        veterinario.rut = data["rut"]
        veterinario.telefono = data["telefono"]
        veterinario.direccion = data.get("direccion") or ""
        veterinario.especialidad = data.get("especialidad") or ""
        veterinario.turno = data.get("turno") or ""
        veterinario.save(
            update_fields=["rut", "telefono", "direccion", "especialidad", "turno"]
        )
        return veterinario


class AdministradorPerfilForm(BasePerfilForm):
    locked_fields = BasePerfilForm.locked_fields + ("empresa_representante",)
    empresa_representante = forms.CharField(
        max_length=255, label="Empresa representante", required=False
    )

    def save(self):
        data = self.cleaned_data
        administrador = self.instance
        self.save_user(data["email"])
        administrador.rut = data["rut"]
        administrador.telefono = data["telefono"]
        administrador.direccion = data.get("direccion") or ""
        administrador.empresa_representante = data.get("empresa_representante") or ""
        administrador.save(
            update_fields=["rut", "telefono", "direccion", "empresa_representante"]
        )
        return administrador
