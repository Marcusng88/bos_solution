"""
Database type utilities for cross-database compatibility
"""

from sqlalchemy import JSON, TypeDecorator, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.engine import Dialect
import json


class DatabaseJSON(TypeDecorator):
    """A type that uses JSONB for PostgreSQL and JSON for other databases"""
    
    impl = JSON
    cache_ok = True
    
    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        else:
            return dialect.type_descriptor(JSON())


class DatabaseUUID(TypeDecorator):
    """A type that uses UUID for PostgreSQL and String for SQLite"""
    
    impl = String
    cache_ok = True
    
    def load_dialect_impl(self, dialect: Dialect):
        if dialect.name == 'postgresql':
            from sqlalchemy.dialects.postgresql import UUID
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(String(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if dialect.name == 'postgresql':
            return value
        else:
            import uuid
            return uuid.UUID(value)
