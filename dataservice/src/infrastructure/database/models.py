"""
Database models for DataService.

These models mirror the ones in infrastructureservice/models.py
to access the shared database.
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Integer, Boolean, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from .connection import Base


class User(Base):
    __tablename__ = "User"

    id_user = Column(CHAR(36), primary_key=True)
    username = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=True)
    role = Column(String(50), nullable=True)
    active = Column(Boolean, default=True)


class Bank(Base):
    __tablename__ = "Bank"

    id_bank = Column(CHAR(36), primary_key=True)
    bank_name = Column(String(255), nullable=False)


class TransactionCategory(Base):
    __tablename__ = "TransactionCategory"

    id_category = Column(CHAR(36), primary_key=True)
    description = Column(String(255), nullable=False)


class TransactionBatch(Base):
    __tablename__ = "TransactionBatch"

    id_batch = Column(CHAR(36), primary_key=True)
    process_status = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    batch_size = Column(Integer, nullable=True)


class Transaction(Base):
    __tablename__ = "Transaction"

    id_transaction = Column(CHAR(36), primary_key=True)
    id_user = Column(CHAR(36), nullable=False)
    id_category = Column(CHAR(36), ForeignKey("TransactionCategory.id_category"), nullable=False)
    id_bank = Column(CHAR(36), ForeignKey("Bank.id_bank"), nullable=True)
    id_batch = Column(CHAR(36), ForeignKey("TransactionBatch.id_batch"), nullable=True)
    transaction_name = Column(String(255), nullable=False)
    value = Column(Numeric(15, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    transaction_type = Column(String(50), nullable=False)

    # Relationships
    category = relationship("TransactionCategory")
    bank = relationship("Bank")


class InsightCategory(Base):
    __tablename__ = "InsightCategory"

    id_category = Column(CHAR(36), primary_key=True)
    description = Column(String(255), nullable=False)


class Insights(Base):
    __tablename__ = "Insights"

    id_insight = Column(CHAR(36), primary_key=True)
    id_user = Column(CHAR(36), ForeignKey("User.id_user"), nullable=False)
    id_category = Column(CHAR(36), ForeignKey("InsightCategory.id_category"), nullable=False)
    title = Column(String(255), nullable=False)
    text = Column(Text, nullable=False)
    relevance = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # Relationships
    category = relationship("InsightCategory")
