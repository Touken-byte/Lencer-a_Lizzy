from catalogo.models import Producto

CARRITO_SESSION_KEY = 'carrito'


class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get(CARRITO_SESSION_KEY)
        if not carrito:
            carrito = {}
        self.carrito = carrito

    def agregar(self, producto_id, talla, color='', cantidad=1):
        clave = f"{producto_id}_{talla}_{color}"
        if clave in self.carrito:
            self.carrito[clave]['cantidad'] += cantidad
        else:
            self.carrito[clave] = {
                'producto_id': producto_id,
                'talla': talla,
                'color': color,
                'cantidad': cantidad,
            }
        self.guardar()

    def actualizar_cantidad(self, clave, cantidad):
        if clave in self.carrito:
            if cantidad <= 0:
                del self.carrito[clave]
            else:
                self.carrito[clave]['cantidad'] = cantidad
            self.guardar()

    def eliminar(self, clave):
        if clave in self.carrito:
            del self.carrito[clave]
            self.guardar()

    def vaciar(self):
        self.session[CARRITO_SESSION_KEY] = {}
        self.session.modified = True

    def guardar(self):
        self.session[CARRITO_SESSION_KEY] = self.carrito
        self.session.modified = True

    def obtener_items(self):
        """Devuelve lista de dicts con producto real, talla, color, cantidad, subtotal"""
        items = []
        productos_ids = [v['producto_id'] for v in self.carrito.values()]
        productos = Producto.objects.filter(id__in=productos_ids).prefetch_related('imagenes', 'variantes')
        productos_dict = {p.id: p for p in productos}

        for clave, data in self.carrito.items():
            producto = productos_dict.get(data['producto_id'])
            if not producto:
                continue
            subtotal = producto.precio_final * data['cantidad']
            items.append({
                'clave': clave,
                'producto': producto,
                'talla': data['talla'],
                'color': data.get('color', ''),
                'cantidad': data['cantidad'],
                'subtotal': subtotal,
            })
        return items

    def total(self):
        return sum(item['subtotal'] for item in self.obtener_items())

    def cantidad_total(self):
        return sum(data['cantidad'] for data in self.carrito.values())

    def __len__(self):
        return len(self.carrito)