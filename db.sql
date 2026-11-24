-- =====================================================
-- PROYECTO: PARNET INGENIERIA
-- MOTOR: MySQL
-- =====================================================

CREATE DATABASE IF NOT EXISTS parnet_ingenieria
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE parnet_ingenieria;

-- =====================================================
-- 1. TABLA ADMINISTRADORES
-- =====================================================

CREATE TABLE IF NOT EXISTS administradores (
    id_administrador INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    correo VARCHAR(150) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- =====================================================
-- 2. TABLA CATEGORIAS DE PRODUCTOS
-- =====================================================

CREATE TABLE IF NOT EXISTS categorias_productos (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- =====================================================
-- 3. TABLA PRODUCTOS
-- =====================================================

CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    precio DECIMAL(12,2) NOT NULL DEFAULT 0,
    stock INT NOT NULL DEFAULT 0,
    imagen VARCHAR(255),
    ficha_tecnica TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME
        DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT chk_producto_precio
        CHECK (precio >= 0),

    CONSTRAINT chk_producto_stock
        CHECK (stock >= 0),

    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria)
        REFERENCES categorias_productos(id_categoria)
        ON DELETE RESTRICT,

    INDEX idx_producto_nombre (nombre)
) ENGINE=InnoDB;

-- =====================================================
-- 4. TABLA AREAS DE SERVICIOS
-- =====================================================

CREATE TABLE IF NOT EXISTS areas_servicios (
    id_area INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- =====================================================
-- 5. TABLA SOLICITUDES DE SERVICIOS
-- =====================================================

CREATE TABLE IF NOT EXISTS solicitudes_servicios (
    id_solicitud INT AUTO_INCREMENT PRIMARY KEY,
    id_area INT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    empresa VARCHAR(150),
    correo VARCHAR(150) NOT NULL,
    telefono VARCHAR(20),
    detalle TEXT NOT NULL,
    estatus ENUM(
        'Pendiente',
        'En proceso',
        'Atendida',
        'Cancelada'
    ) NOT NULL DEFAULT 'Pendiente',
    fecha_solicitud DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_solicitud_area
        FOREIGN KEY (id_area)
        REFERENCES areas_servicios(id_area)
        ON DELETE RESTRICT,

    INDEX idx_solicitud_fecha (fecha_solicitud)
) ENGINE=InnoDB;

-- =====================================================
-- 6. TABLA SUGERENCIAS
-- =====================================================

CREATE TABLE IF NOT EXISTS sugerencias (
    id_sugerencia INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    mensaje TEXT NOT NULL,
    leida BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_sugerencia_fecha (fecha_registro)
) ENGINE=InnoDB;

-- =====================================================
-- 7. TABLA NOTICIAS
-- =====================================================

CREATE TABLE IF NOT EXISTS noticias (
    id_noticia INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    resumen VARCHAR(500),
    contenido TEXT NOT NULL,
    imagen VARCHAR(255),
    fecha_publicacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- =====================================================
-- 8. TABLA CLIENTES
-- =====================================================

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    logo VARCHAR(255) NOT NULL,
    sitio_web VARCHAR(500),
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- =====================================================
-- 9. TABLA SLIDER
-- =====================================================

CREATE TABLE IF NOT EXISTS slider (
    id_slider INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150),
    descripcion VARCHAR(300),
    imagen VARCHAR(255) NOT NULL,
    enlace VARCHAR(500),
    orden INT NOT NULL DEFAULT 0,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- =====================================================
-- 10. TABLA VISITAS
-- =====================================================

CREATE TABLE IF NOT EXISTS visitas (
    id_visita BIGINT AUTO_INCREMENT PRIMARY KEY,
    pagina VARCHAR(255) NOT NULL,
    fecha_visita DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_visita_fecha (fecha_visita)
) ENGINE=InnoDB;

-- =====================================================
-- 11. TABLA USUARIOS CONECTADOS
-- =====================================================

CREATE TABLE IF NOT EXISTS usuarios_conectados (
    id_sesion VARCHAR(64) PRIMARY KEY,
    ultima_actividad DATETIME DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_actividad (ultima_actividad)
) ENGINE=InnoDB;

-- =====================================================
-- DATOS DE PRUEBA
-- Ejecutar esta seccion una sola vez
-- =====================================================

-- CATEGORIAS

INSERT INTO categorias_productos
(nombre, descripcion)
VALUES
('Material eléctrico', 'Componentes eléctricos industriales'),
('Automatización', 'Equipos de automatización industrial'),
('Herramientas', 'Herramientas industriales'),
('Seguridad industrial', 'Equipos de protección personal'),
('Instrumentación', 'Equipos de medición y control');

-- PRODUCTOS
-- Los identificadores corresponden a una base nueva.

INSERT INTO productos
(id_categoria, codigo, nombre, descripcion,
 marca, modelo, precio, stock, imagen, ficha_tecnica)
VALUES
(
    1,
    'PROD-001',
    'Interruptor termomagnético',
    'Interruptor para protección eléctrica',
    'Siemens',
    'MOD-001',
    450.00,
    25,
    'productos/interruptor.jpg',
    'Ficha técnica de demostración'
),
(
    2,
    'PROD-002',
    'Controlador PLC',
    'Controlador lógico programable',
    'Siemens',
    'MOD-002',
    8500.00,
    8,
    'productos/plc.jpg',
    'Ficha técnica de demostración'
),
(
    3,
    'PROD-003',
    'Taladro industrial',
    'Taladro para trabajos industriales',
    'Bosch',
    'MOD-003',
    2300.00,
    15,
    'productos/taladro.jpg',
    'Ficha técnica de demostración'
),
(
    4,
    'PROD-004',
    'Casco de seguridad',
    'Casco de protección industrial',
    '3M',
    'MOD-004',
    350.00,
    0,
    'productos/casco.jpg',
    'Ficha técnica de demostración'
),
(
    5,
    'PROD-005',
    'Multímetro digital',
    'Instrumento de medición eléctrica',
    'Fluke',
    'MOD-005',
    3200.00,
    12,
    'productos/multimetro.jpg',
    'Ficha técnica de demostración'
);

-- AREAS DE SERVICIOS

INSERT INTO areas_servicios
(nombre, descripcion)
VALUES
(
    'Ingeniería eléctrica',
    'Instalaciones y proyectos eléctricos'
),
(
    'Automatización industrial',
    'Automatización de procesos'
),
(
    'Mantenimiento industrial',
    'Mantenimiento preventivo y correctivo'
),
(
    'Consultoría',
    'Asesoría técnica especializada'
);

-- SOLICITUDES DE SERVICIOS

INSERT INTO solicitudes_servicios
(id_area, nombre, empresa, correo, telefono, detalle)
VALUES
(
    1,
    'Juan Pérez',
    'Empresa A',
    'juan@example.com',
    '0000000001',
    'Solicitud de instalación eléctrica'
),
(
    2,
    'María López',
    'Empresa B',
    'maria@example.com',
    '0000000002',
    'Automatización de maquinaria'
),
(
    2,
    'Pedro García',
    'Empresa C',
    'pedro@example.com',
    '0000000003',
    'Programación de PLC'
),
(
    3,
    'Ana Torres',
    'Empresa D',
    'ana@example.com',
    '0000000004',
    'Mantenimiento preventivo'
);

-- SUGERENCIAS

INSERT INTO sugerencias
(nombre, correo, mensaje)
VALUES
(
    'Usuario de prueba',
    'usuario@example.com',
    'Agregar más información de los productos'
),
(
    'Cliente de prueba',
    'cliente@example.com',
    'Ampliar el catálogo de herramientas'
);

-- NOTICIAS

INSERT INTO noticias
(titulo, resumen, contenido, imagen)
VALUES
(
    'Bienvenidos a ParNet Ingeniería',
    'Conoce nuestros servicios',
    'Ofrecemos soluciones de ingeniería industrial.',
    'noticias/bienvenida.jpg'
),
(
    'Nuevos productos disponibles',
    'Actualización del catálogo',
    'Consulta los nuevos productos de automatización.',
    'noticias/productos.jpg'
);

-- CLIENTES

INSERT INTO clientes
(nombre, logo, sitio_web, descripcion)
VALUES
(
    'Grupo Industrial Saltillo',
    'clientes/gis.png',
    'https://gis.com.mx',
    'Empresa del sector manufacturero.'
),
(
    'FEMSA',
    'clientes/femsa.webp',
    'https://femsa.com',
    'Comercio y distribución'
);

-- SLIDER

INSERT INTO slider
(titulo, descripcion, imagen, enlace, orden)
VALUES
(
    'Soluciones de ingeniería',
    'Conoce nuestros servicios profesionales',
    'slider/ingenieria.jpg',
    '/servicios/',
    1
),
(
    'Productos industriales',
    'Consulta nuestro catálogo de productos',
    'slider/productos.jpg',
    '/productos/',
    2
),
(
    'Automatización industrial',
    'Mejora tus procesos industriales',
    'slider/automatizacion.jpg',
    '/servicios/',
    3
);

-- =====================================================
-- VISTA 1: REPORTE DE INVENTARIO
-- =====================================================

CREATE OR REPLACE VIEW vw_inventario AS
SELECT
    p.id_producto,
    p.codigo,
    p.nombre,
    c.nombre AS categoria,
    p.marca,
    p.modelo,
    p.precio,
    p.stock,
    p.activo,
    CASE
        WHEN p.stock > 0 THEN 'Existencia'
        ELSE 'Agotado'
    END AS estatus
FROM productos p
INNER JOIN categorias_productos c
    ON p.id_categoria = c.id_categoria;

-- =====================================================
-- VISTA 2: DASHBOARD DE SERVICIOS
-- =====================================================

CREATE OR REPLACE VIEW vw_dashboard_servicios AS
SELECT
    a.id_area,
    a.nombre AS servicio,
    COUNT(s.id_solicitud) AS total
FROM areas_servicios a
LEFT JOIN solicitudes_servicios s
    ON a.id_area = s.id_area
GROUP BY a.id_area, a.nombre;

-- =====================================================
-- VISTA 3: DASHBOARD DE PRODUCTOS
-- =====================================================

CREATE OR REPLACE VIEW vw_dashboard_productos AS
SELECT
    c.id_categoria,
    c.nombre AS categoria,
    COUNT(p.id_producto) AS total
FROM categorias_productos c
LEFT JOIN productos p
    ON c.id_categoria = p.id_categoria
    AND p.activo = TRUE
GROUP BY c.id_categoria, c.nombre;

-- =====================================================
-- CONSULTAS DE PRUEBA
-- =====================================================

-- Mostrar tablas y vistas

SHOW TABLES;

-- Mostrar productos

SELECT * FROM productos;

-- Buscar productos por nombre

SELECT *
FROM productos
WHERE nombre LIKE '%taladro%'
AND activo = TRUE;

-- Consultar ficha tecnica de un producto

SELECT
    codigo,
    nombre,
    descripcion,
    marca,
    modelo,
    precio,
    ficha_tecnica
FROM productos
WHERE id_producto = 1
AND activo = TRUE;

-- Consultar inventario

SELECT * FROM vw_inventario;

-- Consultar dashboard de servicios

SELECT * FROM vw_dashboard_servicios;

-- Consultar dashboard de productos

SELECT * FROM vw_dashboard_productos;

-- Consultar sugerencias con paginacion

SELECT *
FROM sugerencias
ORDER BY fecha_registro DESC, id_sugerencia DESC
LIMIT 10 OFFSET 0;

-- Consultar noticias activas

SELECT *
FROM noticias
WHERE activo = TRUE
ORDER BY fecha_publicacion DESC;

-- Consultar imagenes del slider

SELECT *
FROM slider
WHERE activo = TRUE
ORDER BY orden ASC;

-- Consultar clientes

SELECT *
FROM clientes
WHERE activo = TRUE;

-- Contador de visitas

SELECT COUNT(*) AS total_visitas
FROM visitas;

-- Contador de usuarios conectados
-- Considera sesiones activas en los ultimos 5 minutos.

SELECT COUNT(*) AS usuarios_activos
FROM usuarios_conectados
WHERE ultima_actividad >= NOW() - INTERVAL 5 MINUTE;

-- =====================================================
-- FIN DEL SCRIPT
-- =====================================================