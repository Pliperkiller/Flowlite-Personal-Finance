from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate a UUID as string"""
    return str(uuid.uuid4())


class BankModel(Base):
    """Database model for banks - matches InsightService Bank table"""
    __tablename__ = "Bank"

    id_bank = Column(CHAR(36), primary_key=True, default=generate_uuid)
    bank_name = Column(String(255), nullable=False)


class CategoryModel(Base):
    """Database model for transaction categories - matches InsightService TransactionCategory table"""
    __tablename__ = "TransactionCategory"

    id_category = Column(CHAR(36), primary_key=True, default=generate_uuid)
    description = Column(String(255), nullable=False)


class TransactionBatchModel(Base):
    """Database model for transaction batches - matches InsightService TransactionBatch table"""
    __tablename__ = "TransactionBatch"

    id_batch = Column(CHAR(36), primary_key=True, default=generate_uuid)
    process_status = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    batch_size = Column(Integer, nullable=True)


class TransactionModel(Base):
    """Database model for transactions - matches InsightService Transaction table"""
    __tablename__ = "Transaction"

    id_transaction = Column(CHAR(36), primary_key=True, default=generate_uuid)
    # id_user references User table managed by IdentityService - no FK constraint
    id_user = Column(CHAR(36), nullable=False)
    id_category = Column(CHAR(36), ForeignKey("TransactionCategory.id_category"), nullable=False)
    id_bank = Column(CHAR(36), ForeignKey("Bank.id_bank"), nullable=True)
    id_batch = Column(CHAR(36), ForeignKey("TransactionBatch.id_batch"), nullable=True)
    transaction_name = Column(String(255), nullable=False)
    value = Column(Numeric(15, 2), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    transaction_type = Column(String(50), nullable=False)
