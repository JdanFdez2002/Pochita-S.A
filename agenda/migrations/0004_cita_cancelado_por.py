from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("agenda", "0003_cita_hora_fin"),
    ]

    operations = [
        migrations.AddField(
            model_name="cita",
            name="cancelado_por",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
