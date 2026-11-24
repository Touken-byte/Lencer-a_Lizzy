from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientas', '0004_carritoguardado'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfilcliente',
            name='consentimiento_fecha',
            field=models.DateTimeField(
                blank=True, null=True,
                help_text='Fecha y hora en que aceptó los Términos y la Política de Privacidad'),
        ),
    ]
