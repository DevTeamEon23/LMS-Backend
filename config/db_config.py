import sqlalchemy as sql
import enum
from sqlalchemy import MetaData, Table, Column, Integer, DECIMAL, VARCHAR, Index, UniqueConstraint,Enum, \
    func, BOOLEAN, create_engine, Date, BigInteger, event, DDL, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID, TIMESTAMP, ENUM
from sqlalchemy.orm import declarative_base, configure_mappers

from .settings import settings

engine_str = f'mysql+mysqlconnector://{settings.PG_USER}:{settings.PG_PASSWORD}@{settings.PG_HOST}:{settings.PG_PORT}/{settings.DBNAME}'
connection = sql.create_engine(engine_str)


metadata = MetaData()
Base = declarative_base(metadata=metadata)

class MyEnum(enum.Enum):
    Superadmin = 'Superadmin'
    Admin = 'Admin'
    Instructor = 'Instructor'
    Learner = 'Learner'

n_table_user = 'users'
s_table_user = Table(
    n_table_user, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('full_name', VARCHAR(200), nullable=True),
    Column('username', VARCHAR(150), nullable=False),
    Column('email', VARCHAR(150), nullable=False),
    Column('password', VARCHAR(150), nullable=False),
    Column('role', Enum(MyEnum), server_default='Learner'),
    Column('users_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),  # After Sign-in for 2FA
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('active', BOOLEAN, nullable=False),
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    UniqueConstraint('email', name=f'uq_{n_table_user}_xref'),
    Index(f'idx_{n_table_user}_token', 'token'),
)


meta_engine = sql.create_engine(engine_str)
metadata.create_all(meta_engine, checkfirst=True)
# Close the engine
meta_engine.dispose()


if __name__=="__main__":
   pass