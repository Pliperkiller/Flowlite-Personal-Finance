from sqlalchemy import (
    Column, String, Integer, DateTime, Numeric, 
    ForeignKey, Boolean, Text, func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from src.infrastructure.config.database import Base


class UserModel(Base):
    """SQLAlchemy model for User table"""
    __tablename__ = "User"
    
    id_user = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role = Column(String(50))
    active = Column(Boolean, default=True)
    
    # Relationships
    transactions = relationship("TransactionModel", back_populates="user")
    insights = relationship("InsightModel", back_populates="user")


class TransactionCategoryModel(Base):
    """SQLAlchemy model for TransactionCategory table"""
    __tablename__ = "TransactionCategory"
    
    id_category = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(255), nullable=False)
    
    # Relationships
    transactions = relationship("TransactionModel", back_populates="category")


class BankModel(Base):
    """SQLAlchemy model for Bank table"""
    __tablename__ = "Bank"
    
    id_bank = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bank_name = Column(String(255), nullable=False)
    
    # Relationships
    transactions = relationship("TransactionModel", back_populates="bank")


class TransactionBatchModel(Base):
    """SQLAlchemy model for TransactionBatch table"""
    __tablename__ = "TransactionBatch"
    
    id_batch = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    process_status = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False, default=func.now())
    end_date = Column(DateTime)
    batch_size = Column(Integer)
    
    # Relationships
    transactions = relationship("TransactionModel", back_populates="batch")


class TransactionModel(Base):
    """SQLAlchemy model for Transaction table"""
    __tablename__ = "Transaction"
    
    id_transaction = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_user = Column(UUID(as_uuid=True), ForeignKey("User.id_user"), nullable=False)
    id_category = Column(UUID(as_uuid=True), ForeignKey("TransactionCategory.id_category"), nullable=False)
    id_bank = Column(UUID(as_uuid=True), ForeignKey("Bank.id_bank"))
    id_batch = Column(UUID(as_uuid=True), ForeignKey("TransactionBatch.id_batch"))
    transaction_name = Column(String(255), nullable=False)
    value = Column(Numeric(15, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    transaction_type = Column(String(50), nullable=False)  # 'income' or 'expense'
    
    # Relationships
    user = relationship("UserModel", back_populates="transactions")
    category = relationship("TransactionCategoryModel", back_populates="transactions")
    bank = relationship("BankModel", back_populates="transactions")
    batch = relationship("TransactionBatchModel", back_populates="transactions")


class InsightCategoryModel(Base):
    """SQLAlchemy model for InsightCategory table"""
    __tablename__ = "InsightCategory"
    
    id_category = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    description = Column(String(255), nullable=False)
    
    # Relationships
    insights = relationship("InsightModel", back_populates="category")


class InsightModel(Base):
    """SQLAlchemy model for Insights table"""
    __tablename__ = "Insights"
    
    id_insight = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_user = Column(UUID(as_uuid=True), ForeignKey("User.id_user"), nullable=False)
    id_category = Column(UUID(as_uuid=True), ForeignKey("InsightCategory.id_category"), nullable=False)
    title = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    relevance = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    user = relationship("UserModel", back_populates="insights")
    category = relationship("InsightCategoryModel", back_populates="insights")


class RoleModel(Base):
    """SQLAlchemy model for Role table"""
    __tablename__ = "Role"
    
    id_role = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_name = Column(String(100), nullable=False)
