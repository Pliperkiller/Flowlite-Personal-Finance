-- ===========================================
-- SCRIPT DE INICIALIZACIÓN DE BASES DE DATOS
-- ===========================================

-- Crear base de datos para el servicio de identificación
CREATE DATABASE IF NOT EXISTS `identifyservice` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Crear base de datos para futuros servicios
CREATE DATABASE IF NOT EXISTS `userservice` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS `transactionservice` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

CREATE DATABASE IF NOT EXISTS `notificationservice` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Crear usuario específico para cada servicio
CREATE USER IF NOT EXISTS 'identifyservice_user'@'%' IDENTIFIED BY 'identifyservice_pass';
CREATE USER IF NOT EXISTS 'userservice_user'@'%' IDENTIFIED BY 'userservice_pass';
CREATE USER IF NOT EXISTS 'transactionservice_user'@'%' IDENTIFIED BY 'transactionservice_pass';
CREATE USER IF NOT EXISTS 'notificationservice_user'@'%' IDENTIFIED BY 'notificationservice_pass';

-- Otorgar permisos a cada usuario en su respectiva base de datos
GRANT ALL PRIVILEGES ON `identifyservice`.* TO 'identifyservice_user'@'%';
GRANT ALL PRIVILEGES ON `userservice`.* TO 'userservice_user'@'%';
GRANT ALL PRIVILEGES ON `transactionservice`.* TO 'transactionservice_user'@'%';
GRANT ALL PRIVILEGES ON `notificationservice`.* TO 'notificationservice_user'@'%';

-- Aplicar cambios
FLUSH PRIVILEGES;

-- Mostrar bases de datos creadas
SHOW DATABASES;
