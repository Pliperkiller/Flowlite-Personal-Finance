-- Migration: 002_rename_userinfo_columns_to_english.sql
-- Description: Rename all UserInfo table columns from Spanish to English
-- Author: Claude
-- Date: 2025-11-06

-- This migration renames all columns in the UserInfo table from Spanish to English
-- It preserves all data by using ALTER TABLE CHANGE statements

-- Start transaction for safety
START TRANSACTION;

-- Rename columns from Spanish to English
-- Note: CHANGE COLUMN syntax: CHANGE old_name new_name definition

-- Basic personal information
ALTER TABLE UserInfo
    CHANGE COLUMN id_user user_id BINARY(16) NOT NULL UNIQUE,
    CHANGE COLUMN primerNombre first_name VARCHAR(50),
    CHANGE COLUMN segundoNombre middle_name VARCHAR(50),
    CHANGE COLUMN primerApellido last_name VARCHAR(50),
    CHANGE COLUMN segundoApellido second_last_name VARCHAR(50),
    CHANGE COLUMN telefono phone VARCHAR(15),
    CHANGE COLUMN direccion address VARCHAR(200),
    CHANGE COLUMN ciudad city VARCHAR(100),
    CHANGE COLUMN departamento state VARCHAR(100),
    CHANGE COLUMN pais country VARCHAR(100),
    CHANGE COLUMN fechaNacimiento birth_date DATE;

-- Identification information
ALTER TABLE UserInfo
    CHANGE COLUMN numeroIdentificacion identification_number VARCHAR(20) UNIQUE,
    CHANGE COLUMN tipoIdentificacion identification_type VARCHAR(10);

-- Additional information
ALTER TABLE UserInfo
    CHANGE COLUMN genero gender VARCHAR(20),
    CHANGE COLUMN estadoCivil marital_status VARCHAR(30),
    CHANGE COLUMN ocupacion occupation VARCHAR(100);

-- Metadata
ALTER TABLE UserInfo
    CHANGE COLUMN createdAt created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHANGE COLUMN updatedAt updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CHANGE COLUMN activo active BOOLEAN DEFAULT TRUE;

-- Update indexes if needed
-- Drop old indexes
DROP INDEX IF EXISTS idx_id_user ON UserInfo;
DROP INDEX IF EXISTS idx_numeroIdentificacion ON UserInfo;
DROP INDEX IF EXISTS idx_telefono ON UserInfo;

-- Create new indexes with English names
CREATE INDEX idx_user_id ON UserInfo(user_id);
CREATE INDEX idx_identification_number ON UserInfo(identification_number);
CREATE INDEX idx_phone ON UserInfo(phone);

COMMIT;
