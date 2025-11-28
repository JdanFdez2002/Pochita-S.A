from django.db import migrations, models


def sync_duracion_min(apps, schema_editor):
    Servicio = apps.get_model("usuarios", "Servicio")
    for servicio in Servicio.objects.all():
        duracion = getattr(servicio, "duracion_minutos", None) or servicio.duracion_min or 15
        servicio.duracion_min = duracion
        servicio.save(update_fields=["duracion_min"])


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0011_alter_mascota_estado_reproductivo"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicio",
            name="duracion_min",
            field=models.PositiveIntegerField(default=15),
        ),
        migrations.RunPython(sync_duracion_min, migrations.RunPython.noop),
    ]
