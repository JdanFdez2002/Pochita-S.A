import math
from datetime import date, datetime, timedelta

from django.db import migrations, models


def set_hora_fin(apps, schema_editor):
    Cita = apps.get_model("agenda", "Cita")
    Servicio = apps.get_model("usuarios", "Servicio")
    slot = 15

    def get_duracion(servicio):
        if not servicio:
            return slot
        return (
            getattr(servicio, "duracion_min", None)
            or getattr(servicio, "duracion_minutos", None)
            or slot
        )

    for cita in Cita.objects.all():
        if cita.hora_fin:
            continue
        minutos = math.ceil(get_duracion(cita.servicio) / slot) * slot
        inicio_dt = datetime.combine(date.today(), cita.hora)
        cita.hora_fin = (inicio_dt + timedelta(minutes=minutos)).time()
        cita.save(update_fields=["hora_fin"])


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0012_servicio_duracion_min"),
        ("agenda", "0002_cita_motivo_cancelacion"),
    ]

    operations = [
        migrations.AddField(
            model_name="cita",
            name="hora_fin",
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.RunPython(set_hora_fin, migrations.RunPython.noop),
    ]
