-- Script SQL para crear el esquema de la base de datos
-- Este archivo es de referencia, Django maneja las migraciones automáticamente

-- Tabla de usuarios personalizados
CREATE TABLE IF NOT EXISTS inventory_customuser (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined DATETIME NOT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'employee',
    phone VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL,
    is_active_employee BOOLEAN NOT NULL DEFAULT 1
);

-- Tabla de marcas
CREATE TABLE IF NOT EXISTS inventory_brand (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL
);

-- Tabla de modelos de celulares
CREATE TABLE IF NOT EXISTS inventory_phonemodel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL,
    brand_id INTEGER NOT NULL,
    FOREIGN KEY (brand_id) REFERENCES inventory_brand (id)
);

-- Tabla de celulares
CREATE TABLE IF NOT EXISTS inventory_phone (
    id VARCHAR(36) PRIMARY KEY,
    imei VARCHAR(15) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'available',
    condition VARCHAR(20) NOT NULL DEFAULT 'new',
    price DECIMAL(10, 2) NOT NULL,
    storage_capacity VARCHAR(10) NOT NULL,
    color VARCHAR(30) NOT NULL,
    notes TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    added_by_id INTEGER,
    model_id INTEGER NOT NULL,
    FOREIGN KEY (added_by_id) REFERENCES inventory_customuser (id),
    FOREIGN KEY (model_id) REFERENCES inventory_phonemodel (id)
);

-- Tabla de clientes
CREATE TABLE IF NOT EXISTS inventory_customer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    dni VARCHAR(20) NOT NULL,
    created_at DATETIME NOT NULL
);

-- Tabla de ventas
CREATE TABLE IF NOT EXISTS inventory_sale (
    id VARCHAR(36) PRIMARY KEY,
    sale_price DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    is_picked_up BOOLEAN NOT NULL DEFAULT 0,
    pickup_date DATETIME,
    has_trade_in BOOLEAN NOT NULL DEFAULT 0,
    trade_in_value DECIMAL(10, 2),
    sale_date DATETIME NOT NULL,
    notes TEXT NOT NULL,
    customer_id INTEGER NOT NULL,
    phone_id VARCHAR(36) UNIQUE NOT NULL,
    sold_by_id INTEGER,
    trade_in_phone_id VARCHAR(36),
    FOREIGN KEY (customer_id) REFERENCES inventory_customer (id),
    FOREIGN KEY (phone_id) REFERENCES inventory_phone (id),
    FOREIGN KEY (sold_by_id) REFERENCES inventory_customuser (id),
    FOREIGN KEY (trade_in_phone_id) REFERENCES inventory_phone (id)
);

-- Tabla de comentarios
CREATE TABLE IF NOT EXISTS inventory_phonecomment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    phone_id VARCHAR(36) NOT NULL,
    user_id INTEGER NOT NULL,
    FOREIGN KEY (phone_id) REFERENCES inventory_phone (id),
    FOREIGN KEY (user_id) REFERENCES inventory_customuser (id)
);

-- Índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_phone_imei ON inventory_phone(imei);
CREATE INDEX IF NOT EXISTS idx_phone_status ON inventory_phone(status);
CREATE INDEX IF NOT EXISTS idx_phone_model ON inventory_phone(model_id);
CREATE INDEX IF NOT EXISTS idx_sale_date ON inventory_sale(sale_date);
CREATE INDEX IF NOT EXISTS idx_sale_customer ON inventory_sale(customer_id);
CREATE INDEX IF NOT EXISTS idx_comment_phone ON inventory_phonecomment(phone_id);
