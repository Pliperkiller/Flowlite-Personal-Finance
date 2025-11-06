-- ==============================================================
-- Script de migración para arreglar la tabla UserInfo
-- Problema: id_user es la clave primaria, debería tener su propio ID
-- ==============================================================

-- Paso 1: Crear una nueva tabla con la estructura correcta
CREATE TABLE UserInfo_new (
    -- ID único de la información personal (clave primaria)
    id BINARY(16) NOT NULL PRIMARY KEY,

    -- Referencia al usuario (clave foránea)
    id_user BINARY(16) NOT NULL UNIQUE,

    -- Información personal básica
    primerNombre VARCHAR(50),
    segundoNombre VARCHAR(50),
    primerApellido VARCHAR(50),
    segundoApellido VARCHAR(50),
    telefono VARCHAR(15),
    direccion VARCHAR(200),
    ciudad VARCHAR(100),
    departamento VARCHAR(100),
    pais VARCHAR(100),
    fechaNacimiento DATE,

    -- Información de identificación
    numeroIdentificacion VARCHAR(20) UNIQUE,
    tipoIdentificacion VARCHAR(10),

    -- Información adicional
    genero VARCHAR(20),
    estadoCivil VARCHAR(30),
    ocupacion VARCHAR(100),

    -- Metadatos
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    activo BOOLEAN DEFAULT TRUE,

    -- Índices para mejorar el rendimiento
    INDEX idx_id_user (id_user),
    INDEX idx_numeroIdentificacion (numeroIdentificacion),
    INDEX idx_telefono (telefono)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Paso 2: Migrar datos existentes de UserInfo a UserInfo_new
-- IMPORTANTE: Ejecutar este INSERT solo si ya tienes datos en la tabla UserInfo
-- Si la tabla está vacía, puedes saltarte este paso
INSERT INTO UserInfo_new (id, id_user, primerNombre, segundoNombre, primerApellido,
                         segundoApellido, telefono, direccion, ciudad, departamento,
                         pais, numeroIdentificacion, tipoIdentificacion)
SELECT
    UUID_TO_BIN(UUID()) as id,  -- Generar nuevo UUID para el ID
    id_user,                     -- Mantener el id_user existente
    primerNombre,
    segundoNombre,
    primerApellido,
    segundoApellido,
    telefono,
    direccion,
    ciudad,
    departamento,
    pais,
    numeroIdentificacion,
    tipoIdentificacion
FROM UserInfo;

-- Paso 3: Eliminar la tabla antigua
DROP TABLE UserInfo;

-- Paso 4: Renombrar la nueva tabla
RENAME TABLE UserInfo_new TO UserInfo;

-- ==============================================================
-- ALTERNATIVA MÁS SEGURA: Si prefieres no perder datos
-- ==============================================================
-- En lugar de DROP, puedes renombrar la tabla vieja como backup:
-- RENAME TABLE UserInfo TO UserInfo_backup;
-- RENAME TABLE UserInfo_new TO UserInfo;
--
-- Luego, después de verificar que todo funciona:
-- DROP TABLE UserInfo_backup;
