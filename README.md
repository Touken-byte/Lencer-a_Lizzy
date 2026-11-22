# Lencería Lizzy

Sistema web de catálogo, pedidos y control de ventas para el negocio de ropa **Lencería Lizzy**, de la ciudad de Yacuiba (Bolivia). Permite a las clientas ver el catálogo, armar su carrito, hacer pedidos y conversar con la vendedora, y a la vendedora gestionar productos, pedidos, pagos y ventas desde un panel de administración.

Proyecto académico del **Taller II** de la Carrera de Ingeniería Informática, Universidad Autónoma Juan Misael Saracho (Yacuiba, 2026). Docente: MSc. Ing. José Renzo Espinoza.

## Funcionalidades

**Para las clientas**
- Catálogo con categorías (Mujer, Hombre, Otros) y subcategorías, ofertas con descuento y temporada del producto.
- Filtros por categoría, subcategoría, talla y color. Cada talla y color tiene su propio stock (variantes), y se puede filtrar por "Mi talla" según el perfil.
- Registro e inicio de sesión con usuario o correo. Perfil con género y tallas, direcciones de entrega y lista de favoritos.
- Carrito que se guarda en la base de datos (sobrevive al cierre de sesión), con validación de stock.
- Pedidos con pago por QR (con referencia obligatoria), efectivo o coordinación por WhatsApp, y comprobante de pago en imagen.
- Seguimiento del pedido (en verificación, confirmado, en preparación, entregado, cancelado), con avisos cuando cambia el estado, la fecha o el pago.
- Chat con la vendedora (texto, imágenes y video).

**Para la administración** (`/admin/`, con tema Jazzmin claro/oscuro)
- Gestión de productos con variantes (talla, color, stock) e imágenes.
- Verificación de pagos y comprobantes, y cambio de estado de los pedidos.
- Bandeja de chats (`/admin/chats/`) con notificación masiva a las clientas.
- Resumen de ventas (`/admin/ventas/`) con selector de mes y desglose por lugar de venta y origen del registro.
- Contadores en el menú: chats sin leer y pagos con comprobante pendiente.

**Otras**
- API REST con autenticación JWT.
- Comando para cancelar los pedidos en efectivo vencidos y devolver el stock (se puede programar con cron).
- Seguridad: `DEBUG` desactivado por defecto, límite de intentos de inicio de sesión, validación de los archivos del chat, correos únicos y redirecciones seguras.

## Tecnologías

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.12 |
| Framework web | Django 6.0 |
| Base de datos | MySQL 8.0 (conector `mysqlclient` 2.2) |
| API | Django REST Framework 3.18, Simple JWT 5.5, django-filter 26.1 |
| Panel de administración | django-jazzmin 3.0 |
| Imágenes | Pillow 13.0 |
| Configuración | python-decouple 3.8 |
| Frontend | HTML y Django Templates, Bootstrap 5.3.3, Font Awesome 6.5.1, Google Fonts (Poppins), JavaScript propio |
| Contacto | Enlaces de WhatsApp (`wa.me`) |

## Requisitos

- Linux (probado en Ubuntu 24.04), Python 3.12 o superior, MySQL 8 y Git.
- Paquetes del sistema para compilar `mysqlclient`.

## Instalación

### 1. Paquetes del sistema (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install -y git python3-venv python3-dev build-essential pkg-config default-libmysqlclient-dev mysql-server
sudo systemctl start mysql
```

### 2. Descargar el proyecto

```bash
git clone https://github.com/Touken-byte/Lencer-a_Lizzy.git
cd Lencer-a_Lizzy
```

### 3. Crear la base de datos

Cambia `CAMBIA_ESTA_CLAVE` por una contraseña propia:

```bash
sudo mysql -e "CREATE DATABASE lenceria_lizzy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; CREATE USER 'lizzy'@'localhost' IDENTIFIED BY 'CAMBIA_ESTA_CLAVE'; GRANT ALL PRIVILEGES ON lenceria_lizzy.* TO 'lizzy'@'localhost'; FLUSH PRIVILEGES;"
```

### 4. Entorno virtual y dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Variables de entorno

Copia el archivo de ejemplo y genera una clave secreta:

```bash
cp .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Edita `.env` con tus valores:

```
SECRET_KEY=la-clave-que-acabas-de-generar
DEBUG=True
DB_NAME=lenceria_lizzy
DB_USER=lizzy
DB_PASSWORD=la-contraseña-del-paso-3
DB_HOST=localhost
DB_PORT=3306
```

> **Importante:** el archivo `.env` contiene secretos y nunca debe subirse al repositorio. Con `DEBUG=False` (el valor por defecto) el servidor de desarrollo no muestra los estilos ni las imágenes; para trabajar en local usa `DEBUG=True`.

| Variable | Descripción | Valor por defecto |
|---|---|---|
| `SECRET_KEY` | Clave secreta de Django (obligatoria) | — |
| `DEBUG` | Modo desarrollo | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos, separados por coma | `localhost,127.0.0.1` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Datos de la base de datos (obligatorios) | — |
| `DB_HOST`, `DB_PORT` | Servidor y puerto de MySQL | `localhost`, `3306` |
| `USE_HTTPS` | Activa cookies seguras y redirección a HTTPS (solo con HTTPS real) | `False` |

### 6. Crear las tablas, el administrador y los datos base

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py cargar_datos_iniciales
python manage.py configurar_tipos_talla
```

### 7. Ejecutar

```bash
python manage.py runserver
```

- Tienda: http://127.0.0.1:8000/
- Panel de administración: http://127.0.0.1:8000/admin/

Para empezar, entra al panel con el administrador, completa la **configuración del negocio** (WhatsApp, datos bancarios, QR de pago) y agrega productos con sus variantes e imágenes.

## Comandos propios

| Comando | Qué hace |
|---|---|
| `python manage.py cargar_datos_iniciales` | Crea las categorías y subcategorías base y la configuración inicial del negocio. |
| `python manage.py configurar_tipos_talla` | Asigna a cada subcategoría el tipo de talla (letra o brasier) según su nombre. |
| `python manage.py cancelar_pedidos_vencidos [--dias N] [--dry-run]` | Cancela los pedidos en línea con pago en efectivo sin pagar tras N días (2 por defecto) y devuelve el stock. Con `--dry-run` solo muestra lo que haría. |
| `python manage.py importar_ventas_estimadas ARCHIVO --usuario-lourdes U --usuario-barrio U [--dry-run]` | Importa las ventas estimadas descritas más abajo. |

## API REST

Rutas bajo `/api/`. La autenticación usa tokens JWT.

| Ruta | Descripción |
|---|---|
| `GET /api/catalogo/categorias/` | Lista de categorías |
| `GET /api/catalogo/productos/` y `/api/catalogo/productos/<id>/` | Lista y detalle de productos (con filtros) |
| `GET /api/catalogo/subcategorias/<categoria_id>/` | Subcategorías de una categoría |
| `GET /api/catalogo/whatsapp/` | Enlace de contacto por WhatsApp |
| `POST /api/clientas/registro/` | Registro de clienta |
| `POST /api/clientas/login/` y `/api/clientas/login/refresh/` | Obtener y renovar el token JWT (con límite de intentos) |
| `/api/clientas/perfil/` | Perfil de la clienta autenticada |
| `/api/clientas/favoritos/` y `/api/clientas/favoritos/<producto_id>/` | Favoritos |

## Estructura del proyecto

```
config/       Configuración de Django (settings, urls)
catalogo/     Categorías, subcategorías, productos, variantes, imágenes y configuración del negocio; API del catálogo
clientas/     Perfiles, direcciones de entrega, favoritos y carrito guardado; API de cuentas
pedidos/      Pedidos, ítems y pagos; señales y comandos propios
chat/         Mensajes entre la clienta y la vendedora
frontend/     Vistas, formularios y carrito de la tienda; vistas propias del panel
templates/    Plantillas del panel de administración
static/       CSS, JavaScript e imágenes
media/        Archivos subidos (no se versiona)
datos/        Archivo de ventas estimadas
```

## Datos de ventas: reales, estimadas y de prueba

Cada pedido guarda tres datos para saber de dónde viene:

- `fecha_venta`: cuándo ocurrió la venta (puede ser anterior a `creado`, que es el momento en que se guardó en la base).
- `lugar_venta`: `online`, `mercado_lourdes` o `feria_barrio_nuevo`.
- `origen`: `real` (registrada en el momento), `estimado` (reconstruida) o `prueba` (pedido de prueba o de demostración).

La vendedora no llevaba un registro de sus ventas y no las recuerda con exactitud. Por eso las ventas presenciales de **agosto a noviembre de 2026** (Mercado Lourdes y Feria de Barrio Nuevo) son una **reconstrucción estimada**, hecha a partir de datos reales del negocio (productos, precios, días y lugares de venta). No son registros tomados en el momento: se identifican con `origen = estimado` y se cargaron con un comando, no por la tienda. Los pedidos hechos para pruebas y demostraciones del sistema se marcan con `origen = prueba` y no se usan en el análisis.

El archivo `datos/ventas_estimadas.txt` contiene esas ventas, y se importa así (los usuarios y los productos deben existir en la base con esos nombres):

```bash
python manage.py importar_ventas_estimadas datos/ventas_estimadas.txt --usuario-lourdes NOMBRE --usuario-barrio NOMBRE --dry-run
```

Con `--dry-run` solo valida y simula. Sin esa opción guarda los pedidos como entregados y con el pago verificado, sin modificar el stock.

## Solución de problemas

- **`Can't connect to local MySQL server`**: MySQL no está encendido. Ejecuta `sudo systemctl start mysql`.
- **Error al instalar `mysqlclient`**: faltan los paquetes del sistema del paso 1.
- **El sitio se ve sin estilos ni imágenes**: usa `DEBUG=True` en el `.env` para desarrollo local.

## Autor

Touken-byte, estudiante de Ingeniería Informática (Taller II, 2026).

