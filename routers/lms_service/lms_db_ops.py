from fastapi import HTTPException

from config.db_config import n_table_user,table_course,table_lmsgroup,table_category,table_lmsevent,table_classroom,table_conference,table_virtualtraining,table_discussion,table_calender,course_enrollment
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

    @classmethod
    def add_users_excel(cls, params):
        query = f"""   INSERT into {n_table_user}(eid, sid, full_name, email,dept,adhr, username, password, bio, role, timezone, langtype, users_allowed, auth_token, request_token, token, active, deactive, exclude_from_email) VALUES 
                        (%(eid)s, %(sid)s, %(full_name)s, %(dept)s, %(adhr)s, %(username)s, %(email)s,%(password)s, %(bio)s, %(role)s, %(timezone)s, %(langtype)s, %(users_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(active)s, %(deactive)s, %(exclude_from_email)s)
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

###########################################################################################################################

    def get_user_course_enrollment_by_token(token):
        query = f"""SELECT * FROM {course_enrollment} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Get user_course_enrollment data by id for update fields Mapping
    def get_user_course_enrollment_by_id(id):
        query = f"""SELECT * FROM user_course_enrollment WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
        
#Add user_course_enrollment
    @classmethod
    def add_user_course_enrollment(cls, params):
        query = f"""   INSERT into {course_enrollment}(user_id, course_id, enrollment_allowed, auth_token, request_token, token) VALUES 
                        (%(user_id)s, %(course_id)s, %(enrollment_allowed)s, %(auth_token)s, %(request_token)s, %(token)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch Enrolled & UnEnrolled Users of courses
    @classmethod
    def get_all_user_course_enrollment(cls):
        query = """ SELECT u.*,c.* FROM user_course_enrollment e JOIN users u ON e.user_id = u.id JOIN course c ON e.course_id = c.id; """
        return execute_query(query).fetchall()
    
#Delete or Remove Enrolled User from Course
    @classmethod
    def delete_user_course_enrollment(cls, id):
        query = f""" DELETE FROM user_course_enrollment WHERE id = '{id}'; """
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

#Get Course data by id for update fields Mapping
    def get_course_by_id(id):
        query = f"""SELECT * FROM course WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

    def get_course_by_id_clone(id):
        query = f"""SELECT * FROM course WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            # Replace this with the appropriate method to get column names
            column_names = ['id', 'coursename', 'file', 'description', ...]  # List of all column names

            data_dict = dict(zip(column_names, data))
            return data_dict
    

# Add Courses 
    @classmethod
    def add_courses(cls, params):
        query = f"""   INSERT into {table_course}(coursename, file, description, coursecode,price,courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, course_allowed, auth_token, request_token, token, isActive, isHide) VALUES 
                        (%(coursename)s, %(file)s, %(description)s, %(coursecode)s, %(price)s, %(courselink)s, %(coursevideo)s,%(capacity)s, %(startdate)s, %(enddate)s, %(timelimit)s, %(certificate)s, %(level)s, %(category)s, %(course_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(isActive)s, %(isHide)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch All Courses for Superadmin Course Store page
    @classmethod
    def get_all_courses(cls):
        query = """ SELECT * FROM course; """
        return execute_query(query).fetchall()
    
#Fetch Only Active Courses for Admin Courses page
    @classmethod
    def get_active_courses(cls):
        query = """ SELECT * FROM course WHERE isActive = true; """
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

#Get Group data by id for update fields Mapping
    def get_group_by_id(id):
        query = f"""SELECT * FROM lmsgroup WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
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

#Get category data by id for update fields Mapping
    def get_category_by_id(id):
        query = f"""SELECT * FROM category WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
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

#Get event data by id for update fields Mapping
    def get_event_by_id(id):
        query = f"""SELECT * FROM lmsevent WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
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

######################################################################################################################

#Classroom CRUD
    def get_classroom_by_token(token):
        query = f"""SELECT * FROM {table_classroom} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Get classroom data by id for update fields Mapping
    def get_classroom_by_id(id):
        query = f"""SELECT * FROM classroom WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
        
#Add Classroom
    @classmethod
    def add_classroom(cls, params):
        query = f"""   INSERT into {table_classroom} (instname,classname,date,starttime,venue,messg,duration,classroom_allowed,auth_token,request_token,token) VALUES 
                        (%(instname)s, %(classname)s, %(date)s, %(starttime)s, %(venue)s, %(messg)s, %(duration)s, %(classroom_allowed)s, %(auth_token)s, %(request_token)s, %(token)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch Classroom
    @classmethod
    def get_all_classrooms(cls):
        query = """ SELECT * FROM classroom; """
        return execute_query(query).fetchall()

#Fetch Classname By Event Name
    @classmethod
    def get_classroom_by_classname(cls, classname):
        query = f"SELECT * FROM {table_classroom} WHERE classname = %(classname)s"
        params = {"classname": classname}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="Classname not found")
        else:
            return data
        
#Update Events
    @classmethod
    def update_classroom_to_db(cls, id, instname, classname, date, starttime, venue, messg, duration):
        query = f"""   
        UPDATE classroom SET
            instname = %(instname)s,
            classname = %(classname)s,
            date = %(date)s,
            starttime = %(starttime)s,
            venue = %(venue)s,
            messg = %(messg)s,
            duration = %(duration)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "instname": instname,
        "classname": classname,
        "date":date,
        "starttime": starttime,
        "venue": venue,
        "messg": messg,
        "duration": duration,
    }
        return execute_query(query, params=params)
    
#Delete Classroom
    @classmethod
    def delete_classroom(cls, id):
        query = f""" DELETE FROM classroom WHERE id = '{id}'; """
        return execute_query(query)

######################################################################################################################

#Conference CRUD
    def get_conference_by_token(token):
        query = f"""SELECT * FROM {table_conference} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Get conference data by id for update fields Mapping
    def get_conference_by_id(id):
        query = f"""SELECT * FROM conference WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
        
#Add Conference
    @classmethod
    def add_conference(cls, params):
        query = f"""   INSERT into {table_conference} (instname,confname,date,starttime,meetlink,messg,duration,conference_allowed,auth_token,request_token,token) VALUES 
                        (%(instname)s, %(confname)s, %(date)s, %(starttime)s, %(meetlink)s, %(messg)s, %(duration)s, %(conference_allowed)s, %(auth_token)s, %(request_token)s, %(token)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch Conference
    @classmethod
    def get_all_conferences(cls):
        query = """ SELECT * FROM conference; """
        return execute_query(query).fetchall()

#Fetch Conference By Event Name
    @classmethod
    def get_conference_by_confname(cls, confname):
        query = f"SELECT * FROM {table_conference} WHERE confname = %(confname)s"
        params = {"confname": confname}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="Conference not found")
        else:
            return data
        
#Update Conference
    @classmethod
    def update_conference_to_db(cls, id, instname, confname, date, starttime, meetlink, messg, duration):
        query = f"""   
        UPDATE conference SET
            instname = %(instname)s,
            confname = %(confname)s,
            date = %(date)s,
            starttime = %(starttime)s,
            meetlink = %(meetlink)s,
            messg = %(messg)s,
            duration = %(duration)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "instname": instname,
        "confname": confname,
        "date":date,
        "starttime": starttime,
        "meetlink": meetlink,
        "messg": messg,
        "duration": duration,
    }
        return execute_query(query, params=params)
    
#Delete Conference
    @classmethod
    def delete_conference(cls, id):
        query = f""" DELETE FROM conference WHERE id = '{id}'; """
        return execute_query(query)
    
######################################################################################################################

#Virtual Training CRUD
    def get_virtualtraining_by_token(token):
        query = f"""SELECT * FROM {table_virtualtraining} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Get Virtual Training data by id for update fields Mapping
    def get_virtualtraining_by_id(id):
        query = f"""SELECT * FROM virtualtraining WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
        
#Add Virtual Training
    @classmethod
    def add_virtualtraining(cls, params):
        query = f"""   INSERT into {table_virtualtraining} (instname,virtualname,date,starttime,meetlink,messg,duration,virtualtraining_allowed,auth_token,request_token,token) VALUES 
                        (%(instname)s, %(virtualname)s, %(date)s, %(starttime)s, %(meetlink)s, %(messg)s, %(duration)s, %(virtualtraining_allowed)s, %(auth_token)s, %(request_token)s, %(token)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch Virtual Training
    @classmethod
    def get_all_virtualtrainings(cls):
        query = """ SELECT * FROM virtualtraining; """
        return execute_query(query).fetchall()

#Fetch Virtual Training By virtualname
    @classmethod
    def get_virtualtraining_by_virtualname(cls, virtualname):
        query = f"SELECT * FROM {table_virtualtraining} WHERE virtualname = %(virtualname)s"
        params = {"virtualname": virtualname}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="Virtual Training not found")
        else:
            return data
        
#Update Virtual Training
    @classmethod
    def update_virtualtraining_to_db(cls, id, instname, virtualname, date, starttime, meetlink, messg, duration):
        query = f"""   
        UPDATE virtualtraining SET
            instname = %(instname)s,
            virtualname = %(virtualname)s,
            date = %(date)s,
            starttime = %(starttime)s,
            meetlink = %(meetlink)s,
            messg = %(messg)s,
            duration = %(duration)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "instname": instname,
        "virtualname": virtualname,
        "date":date,
        "starttime": starttime,
        "meetlink": meetlink,
        "messg": messg,
        "duration": duration,
    }
        return execute_query(query, params=params)
    
#Delete Virtual Training
    @classmethod
    def delete_virtualtraining(cls, id):
        query = f""" DELETE FROM virtualtraining WHERE id = '{id}'; """
        return execute_query(query)
    
######################################################################################################################

#Discussion CRUD
    def get_discussion_by_token(token):
        query = f"""SELECT * FROM {table_discussion} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Get Discussion data by id for update fields Mapping
    def get_discussion_by_id(id):
        query = f"""SELECT * FROM discussion WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
        
#Add Discussion
    @classmethod
    def add_discussion(cls, params):
        query = f"""   INSERT into {table_discussion} (topic,messg,file,access,discussion_allowed,auth_token,request_token,token) VALUES 
                        (%(topic)s, %(messg)s, %(file)s, %(access)s, %(discussion_allowed)s, %(auth_token)s, %(request_token)s, %(token)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch Discussion
    @classmethod
    def get_all_discussions(cls):
        query = """ SELECT * FROM discussion; """
        return execute_query(query).fetchall()

#Fetch Discussion By virtualname
    @classmethod
    def get_discussion_by_topic(cls, topic):
        query = f"SELECT * FROM {table_discussion} WHERE topic = %(topic)s"
        params = {"topic": topic}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="Discussion not found")
        else:
            return data
        
#Update Discussion
    @classmethod
    def update_discussion_to_db(cls, id, topic, messg, file, access):
        query = f"""   
        UPDATE discussion SET
            topic = %(topic)s,
            messg = %(messg)s,
            file = %(file)s,
            access = %(access)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "topic": topic,
        "messg": messg,
        "file":file,
        "access": access,
    }
        return execute_query(query, params=params)
    
#Delete Discussion
    @classmethod
    def delete_discussion(cls, id):
        query = f""" DELETE FROM discussion WHERE id = '{id}'; """
        return execute_query(query)
    
###############################################################################################################

#Calender CRUD
    def get_calender_by_token(token):
        query = f"""SELECT * FROM {table_calender} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Get Calender data by id for update fields Mapping
    def get_calender_by_id(id):
        query = f"""SELECT * FROM calender WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
        
#Add Calender
    @classmethod
    def add_calender(cls, params):
        query = f"""   INSERT into {table_calender} (cal_eventname,date,starttime,duration,audience,messg,calender_allowed,auth_token,request_token,token) VALUES 
                        (%(cal_eventname)s, %(date)s, %(starttime)s, %(duration)s, %(audience)s, %(messg)s, %(calender_allowed)s, %(auth_token)s, %(request_token)s, %(token)s)
                        ; 
                    """
        return execute_query(query, params=params)

#Fetch Calender
    @classmethod
    def get_all_calenders(cls):
        query = """ SELECT * FROM calender; """
        return execute_query(query).fetchall()

#Fetch Calender By cal_eventname
    @classmethod
    def get_calender_by_cal_eventname(cls, cal_eventname):
        query = f"SELECT * FROM {table_calender} WHERE cal_eventname = %(cal_eventname)s"
        params = {"cal_eventname": cal_eventname}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="calender not found")
        else:
            return data
        
#Update Calender
    @classmethod
    def update_calender_to_db(cls, id, cal_eventname,date,starttime,duration,audience,messg):
        query = f"""   
        UPDATE calender SET
            cal_eventname = %(cal_eventname)s,
            date = %(date)s,
            starttime = %(starttime)s,
            duration = %(duration)s,
            audience = %(audience)s,
            messg = %(messg)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "cal_eventname": cal_eventname,
        "date": date,
        "starttime":starttime,
        "duration": duration,
        "audience":audience,
        "messg": messg,
    }
        return execute_query(query, params=params)
    
#Delete Calender
    @classmethod
    def delete_calender(cls, id):
        query = f""" DELETE FROM calender WHERE id = '{id}'; """
        return execute_query(query)    
    



    