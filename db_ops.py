from time import sleep, time

import pandas as pd
import sqlalchemy as sql
import sqlalchemy.exc as sql_exec
from fastapi import HTTPException

from config.db_config import engine_str, n_table_user
from config.logconfig import logger

execute_retry = True
pool = sql.create_engine(engine_str, pool_size=3, max_overflow=20, pool_recycle=67, pool_timeout=30, echo=None)


def insert_data(table, dict_data, engine_address=None, multi=False, ignore=False, truncate=False, retry=1, wait_period=5):
    """
    This is used to insert the data in dict format into the table
    :param table: SQLAlchemy Table Object
    :param dict_data: Data to be inserted
    :param engine_address: Define a custom engine string. Use default if None provided.
    :param multi: Whether to use multi query or not
    :param ignore: Use Insert Ignore while insertion
    :param truncate: Truncate table before insertion
    :param retry: Insert Retry Number
    :param wait_period: Time in seconds for retry
    :return: None
    """
    st = time()
    logger.debug(f'Data Insertion started for {table.name}')
    # engine_con_str = engine_address if engine_address is not None else engine_str
    # engine = sql.create_engine(engine_con_str)
    ins = table.insert()

    with pool.connect() as conn:
        if truncate:
            conn.execute(f'TRUNCATE TABLE {table.name}')
        try:
            conn.execute(ins, dict_data, multi=multi)

        except sql_exec.OperationalError as e:
            if retry > 0:
                logger.info(f"Error for {table.name}: {e}")
                logger.info(
                    f'Retrying to insert data in {table.name} after {wait_period} seconds')
                sleep(wait_period)
                insert_data(table=table, dict_data=dict_data, engine_address=engine_address, multi=multi, ignore=ignore,
                            truncate=truncate, retry=retry - 1, wait_period=wait_period)
            else:
                logger.error(
                    f"Error for {table.name} insertion: {e}", escalate=True)
        conn.close()

    logger.debug(f"Data Inserted in {table.name} in: {time() - st} secs")


def insert_data_df(table, data: pd.DataFrame, truncate=False):
    conn = pool.connect()
    if truncate:
        conn.execute(f'TRUNCATE TABLE {table.name}')
    response = data.to_sql(table.name, con=conn,
                           if_exists='append', index=False, method='multi')
    conn.close()
    return response


def execute_query(query, params=None, commit=False):
    if params is None:
        params = {}
    if execute_retry:
        return execute_query_v1(query, params=params, commit=commit)
    else:
        return execute_query_old(query, params=params, commit=commit)


def execute_query_old(query, params=None, commit=False):
    if params is None:
        params = {}
    st = time()
    # logger.debug(f'Executing query...{query[:int(len(query)*0.25)]}...')
    # engine = sql.create_engine(engine_str)
    with pool.connect() as conn:
        result = conn.execute(query, params=params)
        if commit:
            conn.execute("commit;")
        conn.close()

    # logger.debug(f"Time taken to execute query: {time() - st} secs")
    return result.mappings()


def execute_query_v1(query, retry=2, wait_period=5, params=None, commit=False):
    if params is None:
        params = {}
    st = time()
    short_query = query[: int(len(query) * 0.25)]
    # logger.debug(f'Executing query...{short_query}...')
    # engine = sql.create_engine(engine_str)
    with pool.connect() as conn:
        try:

            result = conn.execute(query, params).mappings()
            # conn.execute(ins, dict_data, multi=multi)
            if commit:
                conn.execute("commit;")
        except sql_exec.OperationalError as e:
            if retry > 0:
                logger.info(f"Error for Query {short_query}: {e}")
                logger.info(
                    f'Retrying to execute query {short_query} after {wait_period} seconds')
                sleep(wait_period)
                result = execute_query_v1(
                    query=query, retry=retry - 1, wait_period=wait_period)
            else:
                logger.error(
                    f"Error for Query {short_query}: {e}", escalate=True)
        conn.close()

    # logger.debug(f"Time taken to execute query: {time() - st} secs")
    return result


def read_sql_df(query, params=None, commit=False):
    st = time()
    # logger.debug(f"Reading query..{query[:int(len(query)*0.25)]}...")
    # engine = sql.create_engine(engine_str)
    conn = pool.connect()
    df = pd.read_sql(query, conn, params=params)
    if commit:
        conn.execute('commit')
    conn.close()
    # engine.dispose()
    # logger.debug(f'Data read in {time() - st} secs')
    return df


def build_list_params(key, values: list):
    values_in = {f"{key}_{_i}": _u for _i, _u in enumerate(values)}
    params_in = ",".join([f"%({i})s" for i in values_in.keys()])
    return values_in, params_in


class UserDBHandler:

    def get_user_by_token(token):
        query = f"""SELECT * FROM {n_table_user} where token=%(token)s and active=%(active)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token, 'active': True})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

    @classmethod
    def add_user_to_db(cls, params):
        query = f"""   INSERT into {n_table_user}(full_name, username, email,password, role, users_allowed, auth_token, request_token, token, active) VALUES 
                        (%(full_name)s, %(username)s, %(email)s,%(password)s, %(role)s, %(users_allowed)s,  %(auth_token)s, %(request_token)s, %(token)s, %(active)s)
                        ; 
                    """
        return execute_query(query, params=params)

    @classmethod
    def get_users_list(cls):
        query = """ SELECT full_name as username , email ,active as status FROM users where role='user' ; """
        return execute_query(query).fetchall()

    @classmethod
    def change_password(cls, email, password,user):
        query = """ UPDATE users SET password = %(password)s WHERE email=%(email)s and id = %(user_id)s"""
        params = {"password": password, "email": email,"user_id":user['id']}
        return execute_query(query, params=params)

    @classmethod
    def flush_tokens(cls, token=None):
        if token is None:
            query = """UPDATE users SET token = '' WHERE role != 'app'; """
        else:
            query = """UPDATE users SET token = '' WHERE token = %(token)s; """
        return execute_query(query, params={'token': token})
