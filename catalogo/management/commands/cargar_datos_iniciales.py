from django.core.management.base import BaseCommand
from catalogo.models import Categoria, Subcategoria, ConfiguracionNegocio


class Command(BaseCommand):
    help = "Carga categorías, subcategorías y configuración inicial del negocio"

    def handle(self, *args, **kwargs):
        estructura = {
            'Mujer': ['Arriba', 'Abajo', 'Conjuntos', 'Accesorios'],
            'Hombre': ['Boxer', 'Calzoncillo', 'Medias', 'Accesorios'],
            'Otros': ['Medias', 'Pijamas', 'Accesorios'],
        }

        for idx, (nombre_cat, subcats) in enumerate(estructura.items()):
            categoria, creada = Categoria.objects.get_or_create(
                nombre=nombre_cat,
                defaults={'orden': idx}
            )
            if creada:
                self.stdout.write(self.style.SUCCESS(f"Categoría creada: {categoria.nombre}"))
            else:
                self.stdout.write(f"Categoría ya existía: {categoria.nombre}")

            for nombre_sub in subcats:
                subcategoria, sub_creada = Subcategoria.objects.get_or_create(
                    categoria=categoria,
                    nombre=nombre_sub
                )
                if sub_creada:
                    self.stdout.write(self.style.SUCCESS(f"  Subcategoría creada: {subcategoria}"))

        ConfiguracionNegocio.obtener()
        self.stdout.write(self.style.SUCCESS("Configuración del negocio inicializada (completar datos en el admin)."))

        self.stdout.write(self.style.SUCCESS("¡Datos iniciales cargados correctamente!"))