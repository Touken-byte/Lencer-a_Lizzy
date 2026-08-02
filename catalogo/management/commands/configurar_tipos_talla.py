from django.core.management.base import BaseCommand
from catalogo.models import Subcategoria

PALABRAS_BRASSIERE = ['arriba', 'sujetador', 'brasier', 'brassiere', 'corpiño', 'corpino', 'top']


class Command(BaseCommand):
    help = "Configura automáticamente el tipo_talla de cada subcategoría según su nombre"

    def handle(self, *args, **options):
        subcategorias = Subcategoria.objects.all()
        if not subcategorias.exists():
            self.stdout.write(self.style.WARNING("No hay subcategorías creadas todavía."))
            return

        for sub in subcategorias:
            nombre_lower = sub.nombre.lower()
            es_brassiere = any(palabra in nombre_lower for palabra in PALABRAS_BRASSIERE)
            nuevo_tipo = 'brassiere' if es_brassiere else 'letra'

            if sub.tipo_talla != nuevo_tipo:
                sub.tipo_talla = nuevo_tipo
                sub.save()
                self.stdout.write(self.style.SUCCESS(
                    f"✔ {sub.categoria.nombre} - {sub.nombre}: configurado como '{nuevo_tipo}'"
                ))
            else:
                self.stdout.write(f"— {sub.categoria.nombre} - {sub.nombre}: ya estaba en '{nuevo_tipo}'")

        self.stdout.write(self.style.SUCCESS("\nListo. Revisa /admin/catalogo/subcategoria/ para confirmar."))
