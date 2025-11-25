from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        # Importa señales para crear Perfil automático al crear usuarios.
        from . import models  # noqa: F401
