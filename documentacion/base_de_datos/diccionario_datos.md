# Capítulo II: material de la base de datos (borrador)

Fuente: `information_schema` de la base `ropainterior_db` (MySQL 8) y los modelos de Django. Los tipos son los reales de MySQL. Todas las tablas usan el motor InnoDB con codificación utf8mb4.

## Tabla de entidades (para la Tabla 8)

| Entidad (tabla) | Qué guarda |
|---|---|
| auth_user | Las personas que ingresan al sistema (clientas y la vendedora) y si son administradoras |
| catalogo_categoria | Las secciones del catálogo: Mujer, Hombre y Otros |
| catalogo_subcategoria | Los grupos dentro de cada categoría y el tipo de talla que usan |
| catalogo_producto | Los productos con su precio, oferta y temporada |
| catalogo_varianteproducto | Cada combinación de talla y color de un producto con su stock |
| catalogo_imagenproducto | Las fotos de cada producto y cuál es la portada |
| catalogo_configuracionnegocio | Los datos del negocio: WhatsApp, cuenta bancaria y QR de pago |
| clientas_perfilcliente | Teléfono, género y tallas de cada clienta |
| clientas_direccionentrega | Las direcciones de entrega que guarda cada clienta |
| clientas_favorito | Los productos que cada clienta marca como favoritos |
| clientas_carritoguardado | El carrito de cada clienta, guardado entre sesiones |
| pedidos_pedido | Los pedidos y ventas, con su fecha, lugar, origen y estado |
| pedidos_itempedido | Las líneas de cada pedido: producto, talla, color, cantidad y precio cobrado |
| pedidos_pago | El pago de cada pedido: método, estado y comprobante |
| chat_mensaje | Los mensajes entre la clienta y la vendedora |
| chat_imagenmensaje | Las imágenes y videos adicionales de un mensaje |

## Relaciones y cardinalidades (para el modelo entidad-relación)

| Relación | Cardinalidad | Cómo se resuelve |
|---|---|---|
| Categoría - Subcategoría | 1:N | `catalogo_subcategoria.categoria_id` |
| Categoría - Producto | 1:N | `catalogo_producto.categoria_id` |
| Subcategoría - Producto | 1:N | `catalogo_producto.subcategoria_id` |
| Producto - Variante | 1:N | `catalogo_varianteproducto.producto_id` |
| Producto - Imagen | 1:N | `catalogo_imagenproducto.producto_id` |
| Usuario - Perfil de clienta | 1:1 | `clientas_perfilcliente.usuario_id` (único) |
| Usuario - Carrito guardado | 1:1 | `clientas_carritoguardado.usuario_id` (único) |
| Usuario - Dirección de entrega | 1:N | `clientas_direccionentrega.usuario_id` |
| Usuario - Producto (favoritos) | N:M | tabla intermedia `clientas_favorito` |
| Usuario - Pedido | 1:N | `pedidos_pedido.clienta_id` |
| Dirección - Pedido | 1:N (opcional) | `pedidos_pedido.direccion_id` (puede ser nulo) |
| Pedido - Producto | N:M | tabla intermedia `pedidos_itempedido` (con talla, color, cantidad y precio) |
| Pedido - Pago | 1:1 | `pedidos_pago.pedido_id` (único) |
| Usuario - Mensaje | 1:N | `chat_mensaje.usuario_id` (la clienta dueña de la conversación) |
| Mensaje - Imagen de mensaje | 1:N | `chat_imagenmensaje.mensaje_id` |

`catalogo_configuracionnegocio` no tiene relaciones: guarda un solo registro con los datos del negocio.

---

## Diccionario de datos

### auth_user

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | INT | PK | Identificador único del usuario |
| password | VARCHAR(128) | | Contraseña guardada como hash, nunca en texto |
| last_login | DATETIME(6) | | Fecha del último inicio de sesión (puede ser nula) |
| is_superuser | TINYINT(1) | | 1 si tiene todos los permisos |
| username | VARCHAR(150) | UNIQUE | Nombre de usuario |
| first_name | VARCHAR(150) | | Nombre |
| last_name | VARCHAR(150) | | Apellido |
| email | VARCHAR(254) | | Correo electrónico |
| is_staff | TINYINT(1) | | 1 si puede entrar al panel de administración (la vendedora) |
| is_active | TINYINT(1) | | 1 si la cuenta está activa |
| date_joined | DATETIME(6) | | Fecha de registro |

### catalogo_categoria

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador de la categoría |
| nombre | VARCHAR(50) | UNIQUE | Nombre: Mujer, Hombre u Otros |
| orden | SMALLINT UNSIGNED | | Posición en que se muestra en el catálogo |

### catalogo_subcategoria

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador de la subcategoría |
| categoria_id | BIGINT | FK | Categoría a la que pertenece (catalogo_categoria) |
| nombre | VARCHAR(50) | | Nombre de la subcategoría. Es único dentro de su categoría |
| tipo_talla | VARCHAR(10) | | Tipo de talla que usa: letra, brassiere o sin_talla |

### catalogo_producto

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador del producto |
| categoria_id | BIGINT | FK | Categoría del producto (catalogo_categoria) |
| subcategoria_id | BIGINT | FK | Subcategoría del producto (catalogo_subcategoria) |
| nombre | VARCHAR(150) | | Nombre del producto |
| descripcion | LONGTEXT | | Descripción (puede estar vacía) |
| precio | DECIMAL(8,2) | | Precio de lista en bolivianos |
| activo | TINYINT(1) | | 1 si se muestra en el catálogo. Es una baja lógica: no se borra |
| en_oferta | TINYINT(1) | | 1 si está en oferta |
| porcentaje_descuento | SMALLINT UNSIGNED | | Descuento de 0 a 90 % cuando está en oferta |
| temporada | VARCHAR(15) | | todo_el_anio, invierno o verano |
| creado | DATETIME(6) | | Fecha de creación |
| actualizado | DATETIME(6) | | Fecha de la última modificación |

### catalogo_varianteproducto

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador de la variante |
| producto_id | BIGINT | FK | Producto al que pertenece (catalogo_producto) |
| talla | VARCHAR(10) | | Talla: de XS a XXL, Única o brasier (por ejemplo 75B) |
| color | VARCHAR(50) | | Color (vacío si el producto no maneja color) |
| stock | INT UNSIGNED | | Unidades disponibles de esa talla y color |

### catalogo_imagenproducto

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador de la imagen |
| producto_id | BIGINT | FK | Producto al que pertenece (catalogo_producto) |
| imagen | VARCHAR(100) | | Ruta del archivo de imagen |
| orden | SMALLINT UNSIGNED | | Posición dentro de la galería del producto |
| es_portada | TINYINT(1) | | 1 si es la imagen principal que se muestra en el catálogo |

### catalogo_configuracionnegocio

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador (hay un solo registro) |
| nombre_negocio | VARCHAR(100) | | Nombre del negocio |
| whatsapp_numero | VARCHAR(20) | | Número de WhatsApp con código de país |
| banco_nombre | VARCHAR(100) | | Banco para pagos por transferencia |
| banco_titular | VARCHAR(100) | | Titular de la cuenta |
| banco_numero_cuenta | VARCHAR(50) | | Número de cuenta |
| qr_pago | VARCHAR(100) | | Ruta de la imagen del QR de pago (puede ser nula) |
| direccion_local | VARCHAR(255) | | Dirección del puesto o local |
| foto_local | VARCHAR(100) | | Ruta de la foto del local (puede ser nula) |
| mapa_url | VARCHAR(200) | | Enlace del mapa con la ubicación |
| actualizado | DATETIME(6) | | Fecha de la última modificación |

### clientas_perfilcliente

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador del perfil |
| usuario_id | INT | FK, UNIQUE | Usuario dueño del perfil (auth_user). Cada usuario tiene un solo perfil |
| telefono | VARCHAR(20) | | Teléfono de contacto |
| genero | VARCHAR(10) | | mujer, hombre u otro |
| talla_brassiere | VARCHAR(5) | | Talla de brasier de la clienta, de 70A a 85C |
| talla_calzon | VARCHAR(5) | | Talla de calzón de la clienta, de XS a XXL |
| creado | DATETIME(6) | | Fecha de creación |
| actualizado | DATETIME(6) | | Fecha de la última modificación |

### clientas_direccionentrega

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador de la dirección |
| usuario_id | INT | FK | Clienta dueña de la dirección (auth_user) |
| nombre_referencia | VARCHAR(50) | | Nombre corto, por ejemplo Casa o Trabajo |
| calle | VARCHAR(200) | | Calle y número |
| barrio | VARCHAR(100) | | Barrio |
| referencias | LONGTEXT | | Puntos de referencia adicionales |
| es_predeterminada | TINYINT(1) | | 1 si es la dirección que se propone por defecto |
| creado | DATETIME(6) | | Fecha de creación |

### clientas_favorito

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador del favorito |
| usuario_id | INT | FK | Clienta que lo marcó (auth_user) |
| producto_id | BIGINT | FK | Producto marcado (catalogo_producto) |
| creado | DATETIME(6) | | Fecha en que se marcó |

La combinación (usuario_id, producto_id) es única: una clienta no puede marcar dos veces el mismo producto.

### clientas_carritoguardado

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador del carrito |
| usuario_id | INT | FK, UNIQUE | Clienta dueña del carrito (auth_user). Tiene uno solo |
| datos | JSON | | Líneas del carrito: producto, talla, color y cantidad |
| actualizado | DATETIME(6) | | Fecha de la última modificación |

### pedidos_pedido

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Número del pedido |
| clienta_id | INT | FK | Clienta que hizo el pedido (auth_user) |
| direccion_id | BIGINT | FK | Dirección de entrega (clientas_direccionentrega). Puede ser nula |
| tipo_entrega | VARCHAR(15) | | recogida (en punto físico) o tienda |
| fecha_venta | DATETIME(6) | | Cuándo ocurrió la venta (puede ser anterior a `creado`) |
| lugar_venta | VARCHAR(20) | | online, mercado_lourdes o feria_barrio_nuevo |
| origen | VARCHAR(10) | | real, estimado (reconstruida) o prueba |
| nota | VARCHAR(300) | | Nota de la clienta para la vendedora. En las ventas estimadas guarda la referencia VE-xxxx |
| estado | VARCHAR(20) | | en_verificacion, confirmado, preparacion, entregado o cancelado |
| fecha_estimada_entrega | DATE | | Fecha estimada de entrega (puede ser nula) |
| notificacion_entrega_pendiente | TINYINT(1) | | 1 si falta avisar a la clienta que se entregó |
| total | DECIMAL(10,2) | | Total del pedido en bolivianos |
| creado | DATETIME(6) | | Fecha en que se guardó en la base |
| actualizado | DATETIME(6) | | Fecha de la última modificación |

### pedidos_itempedido

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador de la línea |
| pedido_id | BIGINT | FK | Pedido al que pertenece (pedidos_pedido) |
| producto_id | BIGINT | FK | Producto vendido (catalogo_producto) |
| talla | VARCHAR(10) | | Talla vendida |
| color | VARCHAR(50) | | Color vendido |
| cantidad | INT UNSIGNED | | Unidades (mínimo 1) |
| precio_unitario | DECIMAL(8,2) | | Precio cobrado por unidad al momento de la venta |

### pedidos_pago

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador del pago |
| pedido_id | BIGINT | FK, UNIQUE | Pedido que se paga (pedidos_pedido). Cada pedido tiene un solo pago |
| metodo | VARCHAR(15) | | qr, efectivo o whatsapp |
| estado | VARCHAR(15) | | pendiente, verificado o rechazado |
| comprobante | VARCHAR(100) | | Ruta de la foto del comprobante (puede ser nula) |
| nombre_referencia | VARCHAR(100) | | Nombre con el que la clienta hizo el pago |
| creado | DATETIME(6) | | Fecha de creación |
| actualizado | DATETIME(6) | | Fecha de la última modificación |

### chat_mensaje

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador del mensaje |
| usuario_id | INT | FK | Clienta dueña de la conversación (auth_user) |
| emisor | VARCHAR(10) | | Quién lo envió: clienta o vendedora |
| texto | VARCHAR(1000) | | Texto del mensaje (puede estar vacío) |
| imagen | VARCHAR(100) | | Ruta de una imagen adjunta (puede ser nula) |
| video | VARCHAR(100) | | Ruta de un video adjunto (puede ser nula) |
| automatico | TINYINT(1) | | 1 si lo generó el sistema, por ejemplo al cambiar el estado de un pedido |
| leido | TINYINT(1) | | 1 si ya fue leído |
| creado | DATETIME(6) | | Fecha y hora de envío |

### chat_imagenmensaje

| Columna | Tipo de dato | Clave | Descripción |
|---|---|---|---|
| id | BIGINT | PK | Identificador del adjunto |
| mensaje_id | BIGINT | FK | Mensaje al que pertenece (chat_mensaje) |
| imagen | VARCHAR(100) | | Ruta de la imagen |
| video | VARCHAR(100) | | Ruta de un video (puede ser nula) |
