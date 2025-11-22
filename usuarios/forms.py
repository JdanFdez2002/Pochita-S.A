from django import forms
from django.contrib.auth.models import User

from .models import Cliente, Perfil


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
            msg = "Este correo ya está registrado."
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
        user = User(
            username=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
        )
        user.set_password(data["password1"])
        user.save()

        perfil = Perfil.objects.create(user=user, rol=Perfil.Roles.CLIENTE)

        Cliente.objects.create(
            perfil=perfil,
            rut=data["rut"],
            direccion=data["direccion"],
            telefono=data["telefono"],
            recibe_noticias=data.get("recibe_noticias", False),
        )
        return user
