from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0004_administrador_recepcionista_veterinario"),
    ]

    operations = [
        migrations.AddField(
            model_name="administrador",
            name="empresa_representante",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
