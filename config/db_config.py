import sqlalchemy as sql
from sqlalchemy import MetaData, Table, Column, String, Integer, DECIMAL, VARCHAR, Index, UniqueConstraint,ForeignKeyConstraint, \
    func, BOOLEAN, create_engine, Date, BigInteger, event, DDL, Float, ForeignKey,Enum,CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID, TIMESTAMP,BYTEA
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base, configure_mappers
from .settings import settings
import urllib.parse
from enum import Enum as PythonEnum
password = urllib.parse.quote_plus(settings.PG_PASSWORD)

engine_str = f'mysql+mysqlconnector://{settings.PG_USER}:{password}@{settings.PG_HOST}:{settings.PG_PORT}/{settings.DBNAME}'
connection = sql.create_engine(engine_str)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class Role(PythonEnum):
    Superadmin = 'Superadmin'
    Admin = 'Admin'
    Instructor = 'Instructor'
    Learner = 'Learner'
    

#Tables Codes Go Here --*
n_table_user = 'users'
s_table_user = Table(
    n_table_user, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('full_name', VARCHAR(200), nullable=True),
    Column('email', VARCHAR(150), nullable=False),
    Column('username', VARCHAR(150), nullable=False),
    Column('password', VARCHAR(150), nullable=False),
    Column('role', Enum(Role), server_default='Learner', nullable=False),
    Column('users_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),  # After Sign-in for 2FA
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('active', BOOLEAN, default=True, nullable=False),
    Column('deactive', BOOLEAN, default=False, nullable=True),
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    UniqueConstraint('email', name=f'uq_{n_table_user}_xref'),
    Index(f'idx_{n_table_user}_token', 'token'),
)

strategy_table = 'strategies'
s_table_startegies = Table(
    strategy_table, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('client_id', VARCHAR(25), nullable=True),
    Column('portfolio_name', VARCHAR(25), nullable=True),
    Column('strategy_type', VARCHAR(25), nullable=True),
    Column('strategy_mode', VARCHAR(25), nullable=True),
    Column('leg1', VARCHAR(25), nullable=True),
    Column('leg2', VARCHAR(25), nullable=True),
    Column('leg3', VARCHAR(25), nullable=True),
    Column('leg4', VARCHAR(25), nullable=True),
    Column('opt_type', VARCHAR(25), nullable=True),
    Column('symbol', VARCHAR(50), nullable=True),
    Column('expiry1', VARCHAR(25), nullable=True),
    Column('expiry2', VARCHAR(25), nullable=True),
    Column('strike_price1', VARCHAR(25), nullable=True),
    Column('strike_price2', VARCHAR(25), nullable=True),
    Column('strike_price3', VARCHAR(25), nullable=True),
    Column('strike_price4', VARCHAR(25), nullable=True),
    Column('ratio1', Integer, nullable=True),
    Column('ratio2', Integer, nullable=True),
    Column('ratio3', Integer, nullable=True),
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
)

meta_engine = sql.create_engine(engine_str, isolation_level='AUTOCOMMIT')
metadata.create_all(meta_engine, checkfirst=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=meta_engine)
# Close the engine
meta_engine.dispose()


if __name__=="__main__":
   pass