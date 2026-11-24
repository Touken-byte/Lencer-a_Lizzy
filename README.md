# Lencería Lizzy

Sistema web de catálogo, pedidos y control de ventas para el negocio de ropa **Lencería Lizzy**, de la ciudad de Yacuiba (Bolivia). Permite a las clientas ver el catálogo, armar su carrito, hacer pedidos y conversar con la vendedora, y a la vendedora gestionar productos, pedidos, pagos y ventas desde un panel de administración. Incluye un modelo de regresión (ciencia de datos) que predice las unidades vendidas por día, lugar y tipo de prenda.

Proyecto académico del **Taller II** de la Carrera de Ingeniería Informática, Universidad Autónoma Juan Misael Saracho (Yacuiba, 2026). Docente: MSc. Ing. José Renzo Espinoza.

## Contenido

1. [Funcionalidades](#funcionalidades)
2. [Tecnologías](#tecnologías)
3. [Requisitos](#requisitos)
4. [Instalación](#instalación)
5. [Ejecución diaria](#ejecución-diaria)
6. [Estructura del proyecto](#estructura-del-proyecto)
7. [Rutas del sistema](#rutas-del-sistema)
8. [Cómo funciona por dentro](#cómo-funciona-por-dentro)
9. [Modelo de datos](#modelo-de-datos)
10. [API REST](#api-rest)
11. [Comandos propios](#comandos-propios)
12. [Datos de ventas: reales, estimadas y de prueba](#datos-de-ventas-reales-estimadas-y-de-prueba)
13. [Ciencia de datos](#ciencia-de-datos)
14. [Solución de problemas](#solución-de-problemas)
15. [Limitaciones conocidas](#limitaciones-conocidas)

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
- Verificación de pagos y comprobantes, y cambio de estado de los pedidos. El total del pedido se calcula solo al guardar.
- Bandeja de chats (`/admin/chats/`) con notificación masiva a las clientas.
- Resumen de ventas (`/admin/ventas/`) con selector de mes y desglose por lugar de venta y origen del registro.
- Contadores en el menú: chats sin leer y pagos con comprobante pendiente.
- Filtros de pedidos por origen y lugar de venta.

**Otras**
- API REST con autenticación JWT.
- Comandos propios para cancelar pedidos vencidos, importar ventas estimadas y exportar los datasets para ciencia de datos.
- Seguridad: `DEBUG` desactivado por defecto, límite de intentos de inicio de sesión, validación de los archivos del chat, correos únicos y redirecciones seguras.

## Tecnologías

| Capa | Tecnología | Para qué se usa |
|---|---|---|
| Lenguaje | Python 3.12 o superior | Todo el sistema y los notebooks |
| Framework web | Django 6.0 | Modelos, vistas, formularios, autenticación, admin, señales |
| Base de datos | MySQL 8.0 con `mysqlclient` 2.2 | Productos, pedidos, pagos, usuarios, chat |
| API | Django REST Framework 3.18, Simple JWT 5.5, django-filter 26.1 | Catálogo y cuentas por API con tokens |
| Panel de administración | django-jazzmin 3.0 | Tema del admin, menú personalizado y modo claro/oscuro |
| Imágenes | Pillow 13.0 | Fotos de productos, comprobantes y chat |
| Configuración | python-decouple 3.8 | Lee las variables del archivo `.env` |
| Frontend | HTML y plantillas de Django, Bootstrap 5.3.3, Font Awesome 6.5.1, Google Fonts (Poppins), JavaScript propio | Tienda y paneles |
| Contacto | Enlaces de WhatsApp (`wa.me`) | Consultas y coordinación de pago |
| Ciencia de datos | pandas, numpy, scikit-learn, matplotlib, seaborn, joblib, JupyterLab | Notebooks de entrenamiento e inferencia (ver [Ciencia de datos](#ciencia-de-datos)) |
| Control de versiones | Git y GitHub | Repositorio |

Las dependencias del sistema web están en `requirements.txt` (11 paquetes) y las de ciencia de datos en `ciencia_de_datos/requirements.txt`. Son dos entornos separados.

## Requisitos

- Linux (probado en Ubuntu 24.04), Python 3.12 o superior, MySQL 8 y Git.
- Paquetes del sistema para compilar `mysqlclient`.
- Un navegador web.

## Instalación

### 1. Paquetes del sistema (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install -y git python3-venv python3-dev build-essential pkg-config default-libmysqlclient-dev mysql-server
sudo systemctl start mysql
```

### 2. Descargar el proyecto

La versión entregada está en la rama `feature/ventas-estimadas`:

```bash
git clone -b feature/ventas-estimadas --single-branch https://github.com/Touken-byte/Lencer-a_Lizzy.git
cd Lencer-a_Lizzy
```

> Cuando el trabajo se pase a la rama `main`, bastará con `git clone https://github.com/Touken-byte/Lencer-a_Lizzy.git`.

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

## Ejecución diaria

Una vez instalado, cada vez que quieras usar el sistema, desde la carpeta del proyecto:

```bash
source venv/bin/activate
sudo systemctl start mysql
python manage.py runserver
```

1. `source venv/bin/activate` activa el entorno virtual (el prompt muestra `(venv)`). Sin él, el comando `python` no existe en Ubuntu y solo funciona `python3`.
2. `sudo systemctl start mysql` enciende MySQL. Si no está encendido, el servidor falla con `Can't connect to local MySQL server`.
3. `python manage.py runserver` levanta el servidor de desarrollo en el puerto 8000.

## Estructura del proyecto

```
config/            Configuración de Django (settings.py, urls.py, wsgi.py, asgi.py)
catalogo/          Categorías, subcategorías, productos, variantes, imágenes y configuración del negocio; API del catálogo
clientas/          Perfiles, direcciones de entrega, favoritos y carrito guardado; API de cuentas
pedidos/           Pedidos, ítems y pagos; señales y comandos propios (importar, exportar, cancelar)
chat/              Mensajes entre la clienta y la vendedora; bandeja de chats del admin
frontend/          Vistas, formularios y carrito de la tienda; vistas propias del panel; backend de autenticación
templates/         Plantillas del panel de administración (resumen de ventas, chats, lista de pedidos)
static/            CSS, JavaScript e imágenes
media/             Archivos subidos (no se versiona)
imagen/            Fotos de ejemplo de productos
datos/             Ventas estimadas (txt) y datasets exportados (CSV): v1 en datos/ y v2 en datos/v2/
ciencia_de_datos/  Notebooks, modelo exportado (.joblib) y tablas de salida
```

## Rutas del sistema

**Tienda** (`frontend/urls.py`)

| Ruta | Qué hace |
|---|---|
| `/` | Inicio |
| `/catalogo/` y `/catalogo/<id>/` | Catálogo con filtros y detalle de producto |
| `/registro/`, `/login/`, `/logout/` | Cuenta de la clienta |
| `/perfil/`, `/direcciones/`, `/favoritos/` | Perfil, direcciones y favoritos |
| `/carrito/`, `/checkout/` | Carrito y confirmación del pedido |
| `/mis-pedidos/` y `/mis-pedidos/<id>/` | Lista y detalle de pedidos, con carga de comprobante |
| `/notificaciones/` | Avisos de cambios del pedido sin recargar la página |
| `/chat/` | Chat con la vendedora |

**Administración**

| Ruta | Qué hace |
|---|---|
| `/admin/` | Panel de Django con tema Jazzmin |
| `/admin/ventas/` | Resumen de ventas por mes, lugar y origen |
| `/admin/chats/` y `/admin/chats/<usuario_id>/` | Bandeja de chats y conversación |
| `/admin/chats/notificar/` | Notificación masiva a las clientas |
| `/admin/avisos/` | Contadores del menú (chats sin leer y pagos pendientes) |

## Cómo funciona por dentro

- **Checkout** (`frontend/views.py`, función `checkout`): dentro de una transacción bloquea las variantes con `select_for_update`, verifica el stock de cada una, crea el `Pedido` con sus `ItemPedido` al precio final del momento, descuenta el stock, calcula el total, crea el `Pago` y vacía el carrito. Si algún producto no alcanza, no se guarda nada.
- **Carrito** (`frontend/carrito.py`): la clase `Carrito` guarda las líneas por producto, talla y color, y se limita al stock disponible. Se persiste en `CarritoGuardado` para que sobreviva al cierre de sesión.
- **Señales de pedidos** (`pedidos/signals.py`): al verificarse un pago, el pedido pasa de "en verificación" a "confirmado" y se asigna una fecha estimada de entrega (5 días). Al pasar a "entregado", se marca una notificación pendiente para la clienta.
- **Señales del chat** (`chat/signals.py`): cada cambio de estado de un pedido crea un mensaje automático de la vendedora en el chat de la clienta.
- **Autenticación** (`frontend/backends.py`): `EmailOUsernameBackend` permite iniciar sesión con usuario o con correo.
- **Validación de archivos del chat** (`chat/forms.py`): comprueba el tipo y el tamaño de imágenes y videos antes de guardarlos.
- **Precio final** (`catalogo/models.py`): `Producto.precio_final` aplica el porcentaje de descuento cuando el producto está en oferta.
- **Panel de administración** (`pedidos/admin.py`, `catalogo/admin.py`): acciones masivas para verificar o rechazar pagos y marcar pedidos como entregados; variantes e imágenes se editan dentro del formulario del producto.

## Modelo de datos

Son 16 tablas (15 propias y `auth_user` de Django):

| App | Tablas | Qué guardan |
|---|---|---|
| `catalogo` | `Categoria`, `Subcategoria` | Clasificación de productos; la subcategoría define el tipo de talla (letra, brasier o sin talla) |
| `catalogo` | `Producto`, `VarianteProducto`, `ImagenProducto` | Productos, su stock por talla y color, y sus fotos |
| `catalogo` | `ConfiguracionNegocio` | Datos del negocio: WhatsApp, cuenta bancaria, QR de pago (un solo registro) |
| `clientas` | `PerfilCliente`, `DireccionEntrega`, `Favorito`, `CarritoGuardado` | Datos de la clienta, direcciones, favoritos y carrito |
| `pedidos` | `Pedido`, `ItemPedido`, `Pago` | Pedidos, sus líneas y el pago de cada uno |
| `chat` | `Mensaje`, `ImagenMensaje` | Conversación con la vendedora y sus adjuntos |
| `auth` | `auth_user` | Usuarios (clientas y administradora) |

`Pedido` guarda además tres campos para el análisis de ventas: `fecha_venta`, `lugar_venta` y `origen` (ver más abajo). Estados de un pedido: en verificación, confirmado, en preparación, entregado y cancelado. Métodos de pago: QR, efectivo y coordinación por WhatsApp.

## API REST

Rutas bajo `/api/`. La autenticación usa tokens JWT; las rutas de lectura del catálogo son públicas y el resto requiere token.

| Ruta | Descripción |
|---|---|
| `GET /api/catalogo/categorias/` | Lista de categorías |
| `GET /api/catalogo/productos/` y `/api/catalogo/productos/<id>/` | Lista y detalle de productos (con filtros) |
| `GET /api/catalogo/subcategorias/<categoria_id>/` | Subcategorías de una categoría |
| `GET /api/catalogo/whatsapp/` | Enlace de contacto por WhatsApp |
| `POST /api/clientas/registro/` | Registro de clienta (límite: 5 por hora) |
| `POST /api/clientas/login/` y `/api/clientas/login/refresh/` | Obtener y renovar el token JWT (límite: 10 por minuto) |
| `/api/clientas/perfil/` | Perfil de la clienta autenticada |
| `/api/clientas/favoritos/` y `/api/clientas/favoritos/<producto_id>/` | Favoritos |

## Comandos propios

Se ejecutan con `python manage.py <comando>` y el entorno virtual activo.

| Comando | Qué hace |
|---|---|
| `cargar_datos_iniciales` | Crea las categorías y subcategorías base y la configuración inicial del negocio. |
| `configurar_tipos_talla` | Asigna a cada subcategoría el tipo de talla (letra o brasier) según su nombre. |
| `cancelar_pedidos_vencidos [--dias N] [--dry-run]` | Cancela los pedidos en línea con pago en efectivo sin pagar tras N días (2 por defecto) y devuelve el stock. Con `--dry-run` solo muestra lo que haría. Se puede programar con cron. |
| `importar_ventas_estimadas ARCHIVO --usuario-lourdes U --usuario-barrio U [--dry-run]` | Importa las ventas estimadas descritas más abajo. |
| `exportar_dataset_ventas [--salida RUTA] [--incluir-pruebas]` | Exporta una fila por línea de pedido a `datos/ventas_lineas.csv` (versión 1). |
| `exportar_dataset_v2 [--carpeta RUTA] [--incluir-pruebas]` | Exporta a `datos/v2/` las líneas de venta, los pedidos, el catálogo y un JSON de metadatos (versión 2). |

Las exportaciones excluyen los pedidos de prueba y los cancelados, y no incluyen ningún dato de las clientas.

## Datos de ventas: reales, estimadas y de prueba

Cada pedido guarda tres datos para saber de dónde viene:

- `fecha_venta`: cuándo ocurrió la venta (puede ser anterior a `creado`, que es el momento en que se guardó en la base).
- `lugar_venta`: `online`, `mercado_lourdes` o `feria_barrio_nuevo`.
- `origen`: `real` (registrada en el momento), `estimado` (reconstruida) o `prueba` (pedido de prueba o de demostración).

La vendedora no llevaba un registro de sus ventas y no las recuerda con exactitud. Por eso las ventas presenciales de **agosto a noviembre de 2026** (Mercado Lourdes y Feria de Barrio Nuevo) son una **reconstrucción estimada**, hecha a partir de datos reales del negocio (productos, precios, días y lugares de venta). No son registros tomados en el momento: se identifican con `origen = estimado` y se cargaron con un comando, no por la tienda. Los pedidos hechos para pruebas y demostraciones del sistema se marcan con `origen = prueba` y no se usan en el análisis.

El archivo `datos/ventas_estimadas.txt` contiene esas ventas (249 pedidos en 29 jornadas) y se importa así (los usuarios y los productos deben existir en la base con esos nombres):

```bash
python manage.py importar_ventas_estimadas datos/ventas_estimadas.txt --usuario-lourdes NOMBRE --usuario-barrio NOMBRE --dry-run
```

Con `--dry-run` solo valida y simula. Sin esa opción guarda los pedidos como entregados y con el pago verificado, sin modificar el stock. El comando es idempotente: cada venta lleva una referencia `VE-xxxx` en el campo `nota`, y no se repite si ya existe.

**Flujo de los datos:** `ventas_estimadas.txt` → `importar_ventas_estimadas` → MySQL → `exportar_dataset_v2` → CSV en `datos/v2/` → notebook. El notebook nunca lee el archivo de texto ni genera los CSV de ventas: solo lee lo que se exportó de la base.

## Ciencia de datos

El modelo es un problema de **regresión supervisada**: predice las **unidades vendidas** por **día**, **lugar de venta** y **tipo de prenda** (ropa interior de mujer, cacheteros, hombre, niño, ropa usada, ropa de baño y medias), para apoyar la decisión de qué mercadería comprar en cada temporada.

> **Advertencia:** el modelo se entrenó con ventas **estimadas** (ver la sección anterior). Aprende las reglas con las que se reconstruyeron los datos, no el comportamiento real del negocio. Demuestra que el flujo completo funciona (datos → variables → modelos → optimización → exportación → inferencia). Con ventas registradas por el sistema, se vuelve a entrenar con los mismos notebooks.

### Archivos

```
datos/v2/
  ventas_lineas.csv            Una fila por línea de pedido (25 columnas)
  pedidos.csv                  Una fila por pedido
  catalogo_productos.csv       Una fila por producto del catálogo
  metadatos_exportacion.json   Cifras declaradas por el exportador, para verificar los CSV
ciencia_de_datos/
  Proyecto_Final_Ventas_Lizzy_v2.ipynb   Entrenamiento: datos, diccionario, análisis, modelos, optimización, exportación
  Inferencia_Ventas_Lizzy_v2.ipynb       Carga el modelo y predice sin reentrenar
  modelo_ventas_v2.joblib                Pipeline completo guardado (lo genera el notebook de entrenamiento)
  salidas_extra_v2/                      Tablas CSV de apoyo (las generan los notebooks)
  requirements.txt                       Dependencias del entorno de ciencia de datos
```

### Qué hace cada notebook

- **Entrenamiento:** lee `datos/v2/` y verifica que las cifras coincidan con el JSON de metadatos (si no coinciden, se detiene). Documenta las 25 columnas y por qué se usa o se descarta cada una, arma la tabla diaria (una fila por día, lugar y tipo), hace el análisis exploratorio, divide por días para evitar fuga de datos, compara cuatro modelos con validación cruzada por grupos (referencia, Ridge, Random Forest y Gradient Boosting), optimiza con `GridSearchCV`, evalúa en días nunca vistos con RMSE, MAE y R², calcula la importancia por permutación y exporta el pipeline a `modelo_ventas_v2.joblib`.
- **Inferencia:** carga el `.joblib`, muestra su ficha técnica y define `predecir(fecha, lugar, tipo)`, que devuelve las unidades estimadas, una banda orientativa, el promedio y el máximo históricos del tipo y un aviso cuando la fecha está fuera del rango entrenado. Permite consultas puntuales, el pronóstico de una jornada completa y de varias fechas desde `salidas_extra_v2/plantilla_pronostico_v2.csv`.

### Cómo ejecutarlos

No se necesita MySQL ni Django: los CSV ya están en `datos/v2/`. Desde la raíz del repositorio:

```bash
python3 -m venv venv_ds
source venv_ds/bin/activate
pip install -r ciencia_de_datos/requirements.txt
```

Después, ejecuta primero el de entrenamiento (genera el modelo) y luego el de inferencia:

```bash
cd ciencia_de_datos
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 Proyecto_Final_Ventas_Lizzy_v2.ipynb
jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=1800 Inferencia_Ventas_Lizzy_v2.ipynb
jupyter lab Proyecto_Final_Ventas_Lizzy_v2.ipynb
```

También puedes abrirlos con `jupyter lab` y usar *Kernel → Restart Kernel and Run All Cells*. Los notebooks buscan los datos en `datos/v2` o `../datos/v2`, por lo que deben ejecutarse dentro de `ciencia_de_datos/` o en la raíz.

El formulario interactivo de la inferencia usa `ipywidgets`, que es opcional: si no está instalado, esa sección se omite y el resto funciona igual. Para verlo: `pip install ipywidgets`.

### Regenerar los datos desde la base

Solo es necesario en el equipo que tiene MySQL y los pedidos:

```bash
source venv/bin/activate
sudo systemctl start mysql
python manage.py exportar_dataset_v2
```

Si MySQL está apagado, el comando falla sin dejar archivos vacíos. Después se sube con git y se baja con `git pull` en el equipo donde se ejecutan los notebooks.

## Solución de problemas

- **`python: command not found`**: falta activar el entorno virtual (`source venv/bin/activate`). Sin él solo existe `python3`.
- **`Can't connect to local MySQL server`**: MySQL no está encendido. Ejecuta `sudo systemctl start mysql`.
- **Error al instalar `mysqlclient`**: faltan los paquetes del sistema del paso 1 de la instalación.
- **`error: externally-managed-environment` al usar pip**: no instales con pip fuera de un entorno virtual; crea y activa uno (`python3 -m venv ...`).
- **`No queda espacio en el dispositivo` al instalar paquetes**: libera espacio en disco (`df -h /` para revisarlo) e instala con `pip install --no-cache-dir -r requirements.txt`.
- **El sitio se ve sin estilos ni imágenes**: usa `DEBUG=True` en el `.env` para desarrollo local.
- **Un notebook dice que no encuentra `datos/v2/`**: ejecuta `git pull` y comprueba que existan los cuatro archivos con `ls datos/v2`.

## Limitaciones conocidas

- Las ventas de agosto a noviembre de 2026 son **estimadas**; el sistema no estuvo en uso real esos meses.
- El modelo tiene pocos datos (163 filas en la tabla diaria) y fuera del rango de fechas entrenado repite el último patrón aprendido.
- Las pruebas automáticas (`tests.py`) todavía no están escritas.
- El proyecto está pensado para ejecutarse en local; para publicarlo hay que servir los archivos estáticos con un servidor web y usar `DEBUG=False` y `USE_HTTPS=True`.

## Autor

Lizzy Leyla Baron Barrero (Touken-byte), estudiante de Ingeniería Informática, UAJMS, Taller II, 2026.

## Requisitos de la Nube Universitaria (legal y demo)

- Páginas públicas: `/terminos/`, `/privacidad/` y `/cookies/`, con enlaces en el pie de página de todo el sitio.
- Banner de cookies en la primera visita; casilla de consentimiento obligatoria en el registro y el checkout.
  La fecha y hora de aceptación se guarda en `PerfilCliente.consentimiento_fecha` (ejecutar `python manage.py migrate`).
- En el `.env` define `CONTACTO_PRIVACIDAD_EMAIL` (correo real de contacto).
- Cuenta demo con datos ficticios: `python manage.py crear_demo` (usa `--reiniciar` para restaurar sus datos).
  Sus credenciales aparecen en el bloque «Acceso Demo» de la pantalla de inicio de sesión. No puede cambiar su correo.
