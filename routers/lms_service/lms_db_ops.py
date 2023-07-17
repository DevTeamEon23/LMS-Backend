from fastapi import HTTPException

from config.db_config import n_table_user,table_course,table_lmsgroup,table_category,table_lmsevent
from ..db_ops import execute_query

class LmsHandler:
# Users CRUD
    def get_user_by_token(token):
        query = f"""SELECT * FROM {n_table_user} where token=%(token)s and active=%(active)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token, 'active': True})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Get User data by id for update fields Mapping
    def get_user_by_id(id):
        query = f"""SELECT * FROM users WHERE id = %(id)s AND active = %(active)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id, 'active': True})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
        
#Add Users
    @classmethod
    def add_users(cls, params):
        query = f"""   INSERT into {n_table_user}(eid, sid, full_name, email,dept,adhr, username, password, bio, file, role, timezone, langtype, users_allowed, auth_token, request_token, token, active, deactive, exclude_from_email) VALUES 
                        (%(eid)s, %(sid)s, %(full_name)s, %(dept)s, %(adhr)s, %(username)s, %(email)s,%(password)s, %(bio)s, %(file)s, %(role)s, %(timezone)s, %(langtype)s, %(users_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(active)s, %(deactive)s, %(exclude_from_email)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Update Users
    @classmethod
    def update_user_to_db(cls,id, eid, sid, full_name, dept, adhr, username, email, password, bio, file, role, timezone, langtype, active, deactive, exclude_from_email):
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
        "active": active,
        "deactive": deactive,
        "exclude_from_email": exclude_from_email,
    }
        return execute_query(query, params=params)

#Fetch Users
    @classmethod
    def get_all_users(cls):
        query = """ SELECT * FROM users; """
        return execute_query(query).fetchall()
    
#Delete Users
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

#Fetch Courses
    @classmethod
    def get_all_courses(cls):
        query = """ SELECT * FROM course; """
        return execute_query(query).fetchall()
    
#Fetch Course by Course Name
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
        
#Update Courses
    @classmethod
    def update_course_to_db(cls,id, coursename, file, description, coursecode, price, courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, isActive, isHide):
        query = f"""   
        UPDATE course SET
            coursename = %(coursename)s,
            file = %(file)s,
            description = %(description)s,
            coursecode = %(coursecode)s,
            price = %(price)s,
            courselink = %(courselink)s,
            coursevideo = %(coursevideo)s,
            capacity = %(capacity)s,
            startdate = %(startdate)s,
            enddate = %(enddate)s,
            timelimit = %(timelimit)s,
            certificate = %(certificate)s,
            level = %(level)s,
            category = %(category)s,
            isActive = %(isActive)s,
            isHide = %(isHide)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "coursename": coursename,
        "file": file,
        "description": description,
        "coursecode": coursecode,
        "price": price,
        "courselink": courselink,
        "coursevideo": coursevideo,
        "capacity": capacity,
        "startdate": startdate,
        "enddate": enddate,
        "timelimit": timelimit,
        "certificate": certificate,
        "level": level,
        "category": category,
        "isActive": isActive,
        "isHide": isHide,
    }
        return execute_query(query, params=params)

#Delete Courses
    @classmethod
    def delete_courses(cls, id):
        query = f""" DELETE FROM course WHERE id = '{id}'; """
        return execute_query(query)
    

########################################################################################

#Groups CRUD
    def get_group_by_token(token):
        query = f"""SELECT * FROM {table_lmsgroup} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Add Groups
    @classmethod
    def add_groups(cls, params):
        query = f"""   INSERT into {table_lmsgroup} (groupname,groupdesc,groupkey, group_allowed, auth_token, request_token, token, isActive) VALUES 
                        (%(groupname)s, %(groupdesc)s, %(groupkey)s, %(group_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(isActive)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch Groups
    @classmethod
    def get_all_groups(cls):
        query = """ SELECT * FROM lmsgroup; """
        return execute_query(query).fetchall()

#Fetch Groups By Group Name
    @classmethod
    def get_group_by_groupname(cls, groupname):
        query = f"SELECT * FROM {table_lmsgroup} WHERE groupname = %(groupname)s"
        params = {"groupname": groupname}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="Group not found")
        else:
            return data
        
#Update Courses
    @classmethod
    def update_group_to_db(cls, id, groupname, groupdesc, groupkey):
        query = f"""   
        UPDATE lmsgroup SET
            groupname = %(groupname)s,
            groupdesc = %(groupdesc)s,
            groupkey = %(groupkey)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "groupname": groupname,
        "groupdesc": groupdesc,
        "groupkey": groupkey,
    }
        return execute_query(query, params=params)
    
#Delete Group
    @classmethod
    def delete_groups(cls, id):
        query = f""" DELETE FROM lmsgroup WHERE id = '{id}'; """
        return execute_query(query)

######################################################################################################################

#Groups CRUD
    def get_category_by_token(token):
        query = f"""SELECT * FROM {table_category} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Add Groups
    @classmethod
    def add_category(cls, params):
        query = f"""   INSERT into {table_category} (name,price,category_allowed, auth_token, request_token, token) VALUES 
                        (%(name)s, %(price)s, %(category_allowed)s, %(auth_token)s, %(request_token)s, %(token)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch Groups
    @classmethod
    def get_all_categories(cls):
        query = """ SELECT * FROM category; """
        return execute_query(query).fetchall()

#Fetch Groups By Group Name
    @classmethod
    def get_category_by_name(cls, name):
        query = f"SELECT * FROM {table_category} WHERE name = %(name)s"
        params = {"name": name}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="Category not found")
        else:
            return data
        
#Update Courses
    @classmethod
    def update_category_to_db(cls, id, name, price):
        query = f"""   
        UPDATE category SET
            name = %(name)s,
            price = %(price)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "name": name,
        "price": price,
    }
        return execute_query(query, params=params)
    
#Delete Group
    @classmethod
    def delete_category(cls, id):
        query = f""" DELETE FROM category WHERE id = '{id}'; """
        return execute_query(query)
    
######################################################################################################################

#Events CRUD
    def get_event_by_token(token):
        query = f"""SELECT * FROM {table_lmsevent} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Add Events
    @classmethod
    def add_event(cls, params):
        query = f"""   INSERT into {table_lmsevent} (ename,eventtype,recipienttype,descp,isActive,event_allowed, auth_token, request_token, token) VALUES 
                        (%(ename)s, %(eventtype)s, %(recipienttype)s, %(descp)s, %(isActive)s, %(event_allowed)s, %(auth_token)s, %(request_token)s, %(token)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch Events
    @classmethod
    def get_all_events(cls):
        query = """ SELECT * FROM lmsevent; """
        return execute_query(query).fetchall()

#Fetch Events By Event Name
    @classmethod
    def get_event_by_ename(cls, ename):
        query = f"SELECT * FROM {table_lmsevent} WHERE ename = %(ename)s"
        params = {"ename": ename}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="Event not found")
        else:
            return data
        
#Update Events
    @classmethod
    def update_event_to_db(cls, id, ename, eventtype,recipienttype,descp):
        query = f"""   
        UPDATE lmsevent SET
            ename = %(ename)s,
            eventtype = %(eventtype)s,
            recipienttype = %(recipienttype)s,
            descp = %(descp)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "ename": ename,
        "eventtype": eventtype,
        "recipienttype":recipienttype,
        "descp": descp,
    }
        return execute_query(query, params=params)
    
#Delete Event
    @classmethod
    def delete_event(cls, id):
        query = f""" DELETE FROM lmsevent WHERE id = '{id}'; """
        return execute_query(query)

