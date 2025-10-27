from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
from typing import Generator
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize database configuration
        
        Args:
            database_url: SQLAlchemy database URL
            echo: Whether to log SQL queries (useful for debugging)
        """
        self.engine = create_engine(
            database_url,
            echo=echo,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=10,
            max_overflow=20
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions
        
        Usage:
            with db_config.get_session() as session:
                # Use session here
                pass
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        finally:
            session.close()
    
    def create_all_tables(self):
        """Creates all tables (use only for development/testing)"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_all_tables(self):
        """Drops all tables (use only for development/testing)"""
        Base.metadata.drop_all(bind=self.engine)
