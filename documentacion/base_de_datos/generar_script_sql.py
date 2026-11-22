"""Genera lenceria_lizzy.sql (respaldo y demo) desde la base local.

Ejecutar desde la raiz del proyecto, con el venv activo:
    python documentacion/base_de_datos/generar_script_sql.py

Incluye: estructura de las 16 tablas; catalogo (sin imagenes); pedidos con
origen='estimado' con sus items y pagos; 3 usuarios de ejemplo y una
configuracion del negocio ficticia. No incluye chat, perfiles, favoritos,
carritos, direcciones, los pedidos de prueba, hashes ni datos reales de contacto.
"""
import os
import subprocess

from decouple import config

SALIDA = 'documentacion/base_de_datos/lenceria_lizzy.sql'
os.environ['MYSQL_PWD'] = config('DB_PASSWORD')
BASE = config('DB_NAME')
CMD = ['mysqldump', '-u', config('DB_USER'),
       '-h', config('DB_HOST', default='localhost'),
       '--skip-comments', '--no-tablespaces', '--single-transaction']

TABLAS = [
    'auth_user', 'catalogo_categoria', 'catalogo_subcategoria',
    'catalogo_producto', 'catalogo_varianteproducto',
    'catalogo_imagenproducto', 'catalogo_configuracionnegocio',
    'clientas_perfilcliente', 'clientas_direccionentrega',
    'clientas_favorito', 'clientas_carritoguardado',
    'pedidos_pedido', 'pedidos_itempedido', 'pedidos_pago',
    'chat_mensaje', 'chat_imagenmensaje',
]
ESTIMADOS = "SELECT id FROM pedidos_pedido WHERE origen='estimado'"

CABECERA = """-- Lencería Lizzy: estructura y datos de demostración.
-- IMPORTANTE: los pedidos con origen='estimado' (agosto a noviembre de 2026)
-- son ESTIMADOS: se reconstruyeron de memoria y se importaron con un comando.
-- No son ventas registradas por el sistema en uso real.
-- Los usuarios y la configuración del negocio son datos de ejemplo.
-- Uso: mysql -u USUARIO -p < lenceria_lizzy.sql
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS lenceria_lizzy CHARACTER SET utf8mb4;
USE lenceria_lizzy;
SET FOREIGN_KEY_CHECKS=0;
"""

EJEMPLOS = """
-- Usuarios de ejemplo (contraseña inutilizable)
INSERT INTO auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) VALUES
(6, '!sin_contrasena', NULL, 1, 'administradora', '', '', '', 1, 1, '2026-08-01 00:00:00.000000'),
(74, '!sin_contrasena', NULL, 0, 'Usuario_BarrioNuevo', '', '', '', 0, 1, '2026-11-01 00:00:00.000000'),
(75, '!sin_contrasena', NULL, 0, 'usuario_lourdes', '', '', '', 0, 1, '2026-11-01 00:00:00.000000');

-- Configuración del negocio (datos ficticios)
INSERT INTO catalogo_configuracionnegocio (id, nombre_negocio, whatsapp_numero, banco_nombre, banco_titular, banco_numero_cuenta, qr_pago, actualizado, direccion_local, foto_local, mapa_url) VALUES
(1, 'Lencería Lizzy', '70000000', 'Banco de ejemplo', 'Titular de ejemplo', '000000000', NULL, '2026-11-22 00:00:00.000000', 'Dirección de ejemplo', '', '');
"""


def volcar(args, f):
    f.flush()
    subprocess.run(CMD + args, stdout=f, check=True)


def datos(f, tabla, where=None):
    args = ['--no-create-info', '--complete-insert']
    if where:
        args.append('--where=' + where)
    volcar(args + [BASE, tabla], f)


with open(SALIDA, 'w', encoding='utf-8') as f:
    f.write(CABECERA)
    volcar(['--no-data', '--skip-add-drop-table', BASE] + TABLAS, f)
    f.write('\n-- Datos\n')
    for t in ['catalogo_categoria', 'catalogo_subcategoria',
              'catalogo_producto', 'catalogo_varianteproducto']:
        datos(f, t)
    f.write(EJEMPLOS)
    datos(f, 'pedidos_pedido', "origen='estimado'")
    datos(f, 'pedidos_itempedido', 'pedido_id IN (' + ESTIMADOS + ')')
    datos(f, 'pedidos_pago', 'pedido_id IN (' + ESTIMADOS + ')')
    f.write('\nSET FOREIGN_KEY_CHECKS=1;\n')

print('Listo:', SALIDA)
