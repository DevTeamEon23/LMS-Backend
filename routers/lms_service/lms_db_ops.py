from fastapi import HTTPException

from config.db_config import n_table_user,table_course
from ..db_ops import execute_query

class LmsHandler:

    def get_user_by_token(token):
        query = f"""SELECT * FROM {n_table_user} where token=%(token)s and active=%(active)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token, 'active': True})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
# Users CRUD
    @classmethod
    def add_users(cls, params):
        query = f"""   INSERT into {n_table_user}(eid, sid, full_name, email,dept,adhr, username, password, bio, file, role, timezone, langtype, users_allowed, auth_token, request_token, token, active, deactive, exclude_from_email) VALUES 
                        (%(eid)s, %(sid)s, %(full_name)s, %(dept)s, %(adhr)s, %(username)s, %(email)s,%(password)s, %(bio)s, %(file)s, %(role)s, %(timezone)s, %(langtype)s, %(users_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(active)s, %(deactive)s, %(exclude_from_email)s)
                        ; 
                    """
        return execute_query(query, params=params)
    
    @classmethod
    def update_user_to_db(cls,id, eid, sid, full_name, dept, adhr, username, email, password, bio, file, role, timezone, langtype, users_allowed, auth_token, request_token, token, active, deactive, exclude_from_email, user):
        query = f"""   
        UPDATE users SET
            eid = %(eid)s,
            sid = %(sid)s,
            full_name = %(full_name)s,
            dept = %(dept)s,
            adhr = %(adhr)s,
            username = %(username)s,
            email = %(email)s,
            password = %(password)s,
            bio = %(bio)s,
            file = %(file)s,
            role = %(role)s,
            timezone = %(timezone)s,
            langtype = %(langtype)s,
            users_allowed = %(users_allowed)s,
            auth_token = %(auth_token)s,
            request_token = %(request_token)s,
            token = %(token)s,
            active = %(active)s,
            deactive = %(deactive)s,
            exclude_from_email = %(exclude_from_email)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "eid": eid,
        "sid": sid,
        "full_name": full_name,
        "dept": dept,
        "adhr": adhr,
        "username": username,
        "email": email,
        "password": password,
        "bio": bio,
        "file": file,
        "role": role,
        "timezone": timezone,
        "langtype": langtype,
        "users_allowed": users_allowed,
        "auth_token": auth_token,
        "request_token": request_token,
        "token": token,
        "active": active,
        "deactive": deactive,
        "exclude_from_email": exclude_from_email,
    }
        return execute_query(query, params=params)
    
    @classmethod
    def get_all_users(cls):
        query = """ SELECT * FROM users; """
        return execute_query(query).fetchall()
    
    @classmethod
    def delete_users(cls, id):
        query = f""" DELETE FROM users WHERE id = '{id}'; """
        return execute_query(query)
    

############################################################################################################################


# Courses CRUD
    def get_course_by_token(token):
        query = f"""SELECT * FROM {table_course} where token=%(token)s and isActive=%(isActive)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token, 'active': True})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
# Add Courses 
    @classmethod
    def add_courses(cls, params):
        query = f"""   INSERT into {table_course}(coursename, file, description, coursecode,price,courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, course_allowed, auth_token, request_token, token, isActive, isHide) VALUES 
                        (%(coursename)s, %(file)s, %(description)s, %(coursecode)s, %(price)s, %(courselink)s, %(coursevideo)s,%(capacity)s, %(startdate)s, %(enddate)s, %(timelimit)s, %(certificate)s, %(level)s, %(category)s, %(course_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(isActive)s, %(isHide)s)
                        ; 
                    """
        return execute_query(query, params=params)
    
    @classmethod
    def get_all_courses(cls):
        query = """ SELECT * FROM course; """
        return execute_query(query).fetchall()
    
    @classmethod
    def get_course_by_coursename(cls, coursename):
        query = f"SELECT * FROM {table_course} WHERE coursename = %(coursename)s"
        params = {"coursename": coursename}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="Course not found")
        else:
            return data
        
    @classmethod
    def delete_courses(cls, id):
        query = f""" DELETE FROM course WHERE id = '{id}'; """
        return execute_query(query)
