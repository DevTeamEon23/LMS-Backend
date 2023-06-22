import sqlalchemy as sql
from sqlalchemy import MetaData, Table, Column, String, Integer, DECIMAL, VARCHAR, Index, UniqueConstraint, \
    func, BOOLEAN, create_engine, Date, BigInteger, event, DDL, Float, ForeignKey,Enum
from sqlalchemy.dialects.postgresql import JSONB, UUID, TIMESTAMP,BYTEA
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import declarative_base, configure_mappers
from .settings import settings
from enum import Enum as PythonEnum
engine_str = f'mysql+mysqlconnector://{settings.PG_USER}:{settings.PG_PASSWORD}@{settings.PG_HOST}:{settings.PG_PORT}/{settings.DBNAME}'
connection = sql.create_engine(engine_str)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class Role(PythonEnum):
    SUPERADMIN = 'Superadmin'
    ADMIN = 'Admin'
    INSTRUCTOR = 'Instructor'
    LEARNER = 'Learner'

class TimeZoneEnum(PythonEnum):
    IST = 'IST'
    NST = 'NST'
    AST = 'AST'
    ECT = 'ECT'
    GMT = 'GMT'
    ARABIC = 'ARABIC'

class LanguageEnum(PythonEnum):
    ENGLISH = 'English'
    HINDI = 'Hindi'
    MARATHI = 'Marathi'

n_table_user = 'users'
s_table_user = Table(
    n_table_user, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('eid', VARCHAR(100), unique=True),
    Column('sid', VARCHAR(150), nullable=True),
    Column('full_name', VARCHAR(200), nullable=True),
    Column('email', VARCHAR(150), nullable=False),
    Column('dept', VARCHAR(100), nullable=True),
    Column('adhr', BigInteger, nullable=True),
    Column('username', VARCHAR(150), nullable=False),
    Column('password', VARCHAR(150), nullable=False),
    Column('bio', VARCHAR(300), nullable=True),
    Column('file', LONGBLOB, nullable=False),
    Column('role', Enum(Role), server_default='Learner', nullable=False),
    Column('timezone', Enum(TimeZoneEnum), server_default='IST', nullable=True),
    Column('langtype', Enum(LanguageEnum), server_default='Hindi', nullable=True),
    Column('users_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),  # After Sign-in for 2FA
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('active', BOOLEAN, default=True, nullable=False),
    Column('deactive', BOOLEAN, default=False, nullable=True),
    Column('exclude_from_email', BOOLEAN, default=False, nullable=True),
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    UniqueConstraint('email', name=f'uq_{n_table_user}_xref'),
    UniqueConstraint('eid', name=f'uq_{n_table_user}_eid'),
    Index(f'idx_{n_table_user}_token', 'token'),
)

meta_engine = sql.create_engine(engine_str, isolation_level='AUTOCOMMIT')
metadata.create_all(meta_engine, checkfirst=True)
# Close the engine
meta_engine.dispose()


if __name__=="__main__":
   pass