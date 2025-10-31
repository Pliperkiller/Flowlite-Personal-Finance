"""
Modelos de SQLAlchemy para la base de datos compartida de Flowlite.

Este archivo define TODOS los modelos que serán usados por:
- UploadService
- InsightService
- Cualquier otro servicio futuro

Las migraciones se generan a partir de estos modelos.
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Integer, Boolean, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a UUID as string"""
    return str(uuid.uuid4())


# ============================================================================
# USER TABLES
# ============================================================================

class User(Base):
    """
    Usuario del sistema (gestionado por IdentityService)
    """
    __tablename__ = "User"

    id_user = Column(CHAR(36), primary_key=True, default=generate_uuid)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=True)  # Puede ser NULL para autenticación externa (OAuth, SSO)
    role = Column(String(50), nullable=True)
    active = Column(Boolean, default=True)


class Role(Base):
    """
    Roles de usuarios
    """
    __tablename__ = "Role"

    id_role = Column(CHAR(36), primary_key=True, default=generate_uuid)
    role_name = Column(String(100), nullable=False)


class UserInfo(Base):
    """
    Información adicional del usuario (gestionado por IdentityService)
    """
    __tablename__ = "UserInfo"

    id_user = Column(CHAR(36), ForeignKey("User.id_user"), primary_key=True)
    primerNombre = Column(String(100), nullable=True)
    segundoNombre = Column(String(100), nullable=True)
    primerApellido = Column(String(100), nullable=True)
    segundoApellido = Column(String(100), nullable=True)
    telefono = Column(String(20), nullable=True)
    direccion = Column(String(255), nullable=True)
    ciudad = Column(String(100), nullable=True)
    departamento = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True)
    numeroIdentificacion = Column(String(50), nullable=True)
    numeroIdentificacoin = Column(String(50), nullable=True)  # Typo en el diagrama, mantenemos compatibilidad
    tipoIdentificacion = Column(String(50), nullable=True)


# ============================================================================
# BANK & TRANSACTION TABLES
# ============================================================================

class Bank(Base):
    """
    Bancos soportados por el sistema
    Usado por: UploadService, InsightService
    """
    __tablename__ = "Bank"

    id_bank = Column(CHAR(36), primary_key=True, default=generate_uuid)
    bank_name = Column(String(255), nullable=False)


class TransactionCategory(Base):
    """
    Categorías de transacciones
    Usado por: UploadService, InsightService
    """
    __tablename__ = "TransactionCategory"

    id_category = Column(CHAR(36), primary_key=True, default=generate_uuid)
    description = Column(String(255), nullable=False)


class TransactionBatch(Base):
    """
    Lotes de procesamiento de transacciones
    Usado por: UploadService, InsightService
    """
    __tablename__ = "TransactionBatch"

    id_batch = Column(CHAR(36), primary_key=True, default=generate_uuid)
    process_status = Column(String(50), nullable=False)  # pending, processing, completed, error
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    batch_size = Column(Integer, nullable=True)


class Transaction(Base):
    """
    Transacciones bancarias
    Usado por: UploadService, InsightService

    NOTA: id_user NO tiene foreign key constraint para permitir independencia
    entre microservicios. La validación de usuario se hace via IdentityService API.
    """
    __tablename__ = "Transaction"

    id_transaction = Column(CHAR(36), primary_key=True, default=generate_uuid)
    id_user = Column(CHAR(36), nullable=False)  # No FK - validación via API
    id_category = Column(CHAR(36), ForeignKey("TransactionCategory.id_category"), nullable=False)
    id_bank = Column(CHAR(36), ForeignKey("Bank.id_bank"), nullable=True)
    id_batch = Column(CHAR(36), ForeignKey("TransactionBatch.id_batch"), nullable=True)
    transaction_name = Column(String(255), nullable=False)
    value = Column(Numeric(15, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # income, expense


class FileUploadHistory(Base):
    """
    Historial de archivos cargados
    Usado por: UploadService para prevenir procesamiento duplicado de archivos

    Almacena el hash SHA256 del contenido del archivo para detectar duplicados
    """
    __tablename__ = "FileUploadHistory"

    id_file = Column(CHAR(36), primary_key=True, default=generate_uuid)
    id_user = Column(CHAR(36), nullable=False)  # No FK - validación via API
    file_hash = Column(CHAR(64), nullable=False)  # SHA256 hash
    file_name = Column(String(255), nullable=False)
    bank_code = Column(String(50), nullable=False)
    upload_date = Column(DateTime, nullable=False, server_default=func.now())
    id_batch = Column(CHAR(36), ForeignKey("TransactionBatch.id_batch"), nullable=False)
    file_size = Column(Integer, nullable=False)


# ============================================================================
# INSIGHTS TABLES
# ============================================================================

class InsightCategory(Base):
    """
    Categorías de insights
    Usado por: InsightService
    """
    __tablename__ = "InsightCategory"

    id_category = Column(CHAR(36), primary_key=True, default=generate_uuid)
    description = Column(String(255), nullable=False)


class Insights(Base):
    """
    Insights generados automáticamente
    Usado por: InsightService
    """
    __tablename__ = "Insights"

    id_insight = Column(CHAR(36), primary_key=True, default=generate_uuid)
    id_user = Column(CHAR(36), ForeignKey("User.id_user"), nullable=False)
    id_category = Column(CHAR(36), ForeignKey("InsightCategory.id_category"), nullable=False)
    title = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    relevance = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
