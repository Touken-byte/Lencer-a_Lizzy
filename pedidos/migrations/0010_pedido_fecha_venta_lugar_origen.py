from django.db import migrations, models
from django.db.models import F
import django.utils.timezone


def fecha_venta_igual_a_creado(apps, schema_editor):
    """Los pedidos que ya existían se vendieron cuando se crearon."""
    Pedido = apps.get_model('pedidos', 'Pedido')
    Pedido.objects.update(fecha_venta=F('creado'))


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0009_pedido_notificacion_entrega_pendiente'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='fecha_venta',
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text="Fecha y hora en que ocurrió la venta (puede ser anterior a 'creado' si se registró después)"),
        ),
        migrations.AddField(
            model_name='pedido',
            name='lugar_venta',
            field=models.CharField(
                choices=[('online', 'Tienda en línea'), ('mercado_lourdes', 'Mercado Lourdes'),
                         ('feria_barrio_nuevo', 'Feria Barrio Nuevo')],
                default='online', max_length=20),
        ),
        migrations.AddField(
            model_name='pedido',
            name='origen',
            field=models.CharField(
                choices=[('real', 'Registrada en el momento'), ('estimado', 'Estimada (reconstruida)'),
                         ('prueba', 'Pedido de prueba')],
                default='real', max_length=10,
                help_text='Real = registrada al vender. Estimada = reconstruida de memoria. Prueba = pedido de prueba.'),
        ),
        migrations.RunPython(fecha_venta_igual_a_creado, migrations.RunPython.noop),
    ]
