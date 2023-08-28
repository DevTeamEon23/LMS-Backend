from fastapi import HTTPException

from config.db_config import n_table_user, users_points
from ..db_ops import execute_query


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
        query = """ SELECT full_name as username , email ,active as status FROM users where role='Learner' ; """
        return execute_query(query).fetchall()

    @classmethod
    def change_password(cls, email, password):
        query = """ UPDATE users SET password = %(password)s WHERE email=%(email)s"""
        params = {"password": password, "email": email}
        return execute_query(query, params=params)

    @classmethod
    def flush_tokens(cls, token=None):
        if token is None:
            query = """UPDATE users SET token = '' WHERE role != 'app'; """
        else:
            query = """UPDATE users SET token = '' WHERE token = %(token)s; """
        return execute_query(query, params={'token': token})
    
    @classmethod
    def get_user_by_email(cls, email):
        query = f"SELECT * FROM {n_table_user} WHERE email = %(email)s"
        params = {"email": email}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="User not found")
        else:
            return data

    @classmethod    
    def get_user_points(cls):
        query = """ SELECT u.full_name, u.role,up.points, u.file FROM users u JOIN user_points up ON u.id = up.user_id; """
        return execute_query(query).fetchall()