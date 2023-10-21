from fastapi import HTTPException

from datetime import datetime
from config.db_config import n_table_user,table_course,table_lmsgroup,table_category,table_lmsevent,table_classroom,table_conference,table_virtualtraining,table_discussion,table_calender,users_courses_enrollment,users_groups_enrollment,courses_groups_enrollment,n_table_user_files,n_table_course_content
from ..db_ops import execute_query

class LmsHandler:
# Users CRUD
    def get_user_by_token(token):
        query = f"""SELECT * FROM {n_table_user} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data

#Get User data by id for update fields Mapping
    def get_user_by_id(id):
        query = f"""SELECT * FROM users WHERE id = %(id)s AND id IS NOT NULL AND id != '';"""
        resp = execute_query(query=query, params={'id': id})
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
    
    @classmethod
    def update_user_fields(cls, id, update_params):
        # Check if there are any fields to update
        if not update_params:
            raise ValueError("No fields to update")

        # Construct a dynamic SQL query to update specific fields
        update_query = f"""
            UPDATE users
            SET {', '.join([f'{field} = %({field})s' for field in update_params.keys()])}
            WHERE id = %(id)s;
        """

        # Add user_id to the update_params
        update_params['id'] = id

        # Execute the query using your database library
        execute_query(update_query, params=update_params)

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
    
# Fetch the Maximum EID NO.(Last Eid for add users automation)
    @classmethod
    def get_last_eid(cls):
        query = """ SELECT MAX(CAST(eid AS UNSIGNED)) + 1 AS next_eid FROM users; """
        return execute_query(query).fetchall()
    
    @classmethod
    def get_all_inst_learner(cls):
        query = """ SELECT * FROM users WHERE role IN ('Instructor', 'Learner'); """
        return execute_query(query).fetchall()
    
#Fetch All dept from users table
    @classmethod
    def get_dept(cls):
        query = """ SELECT DISTINCT dept FROM users WHERE dept IS NOT NULL; """
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
        query = f"""   INSERT into {table_course}(id, user_id, coursename, file, description, coursecode,price,courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, course_allowed, auth_token, request_token, token, isActive, isHide) VALUES 
                        (%(id)s, %(user_id)s, %(coursename)s, %(file)s, %(description)s, %(coursecode)s, %(price)s, %(courselink)s, %(coursevideo)s,%(capacity)s, %(startdate)s, %(enddate)s, %(timelimit)s, %(certificate)s, %(level)s, %(category)s, %(course_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(isActive)s, %(isHide)s)
                        ; 
                    """
        return execute_query(query, params=params)
    
    @classmethod
    def add_clone_courses(cls, params):
        query = f"""   INSERT into {table_course}(user_id, coursename, file, description, coursecode,price,courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, course_allowed, auth_token, request_token, token, isActive, isHide) VALUES 
                        (%(user_id)s, %(coursename)s, %(file)s, %(description)s, %(coursecode)s, %(price)s, %(courselink)s, %(coursevideo)s,%(capacity)s, %(startdate)s, %(enddate)s, %(timelimit)s, %(certificate)s, %(level)s, %(category)s, %(course_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(isActive)s, %(isHide)s)
                        ; 
                    """
        return execute_query(query, params=params)
    
#Fetch All Courses for Superadmin Course Store page
    @classmethod
    def get_all_courses(cls):
        query = """ SELECT * FROM course; """
        return execute_query(query).fetchall()
    
# Fetch the Maximum EID NO.(Last Eid for add users automation)
    @classmethod
    def get_last_id(cls):
        query = """ SELECT MAX(CAST(id AS UNSIGNED)) + 1 AS next_id FROM course; """
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
        
    @classmethod
    def update_course_fields(cls, id, update_params):
        # Check if there are any fields to update
        if not update_params:
            raise ValueError("No fields to update")

        # Construct a dynamic SQL query to update specific fields
        update_query = f"""
            UPDATE course
            SET {', '.join([f'{field} = %({field})s' for field in update_params.keys()])}
            WHERE id = %(id)s;
        """

        # Add course_id to the update_params
        update_params['id'] = id

        # Execute the query using your database library
        execute_query(update_query, params=update_params)

#Update Courses
    @classmethod
    def update_course_to_db(cls,id, user_id, coursename, file, description, coursecode, price, courselink, coursevideo, capacity, startdate, enddate, timelimit, certificate, level, category, isActive, isHide):
        query = f"""   
        UPDATE course SET
            user_id = %(user_id)s,
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
        "user_id": user_id,
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

    @classmethod
    def update_course_to_db_new(
        cls,
        id,
        user_id,
        coursename,
        file,
        description,
        coursecode,
        price,
        courselink,
        coursevideo,
        capacity,
        startdate,
        enddate,
        timelimit,
        certificate,
        level,
        category,
        isActive,
        isHide
    ):

        # Create the update query and parameter dictionary
        query = """
            UPDATE course SET
                user_id = %(user_id)s,
                coursename = %(coursename)s,
                description = %(description)s,
                coursecode = %(coursecode)s,
                price = %(price)s,
                courselink = %(courselink)s,
                capacity = %(capacity)s,
                startdate = %(startdate)s,
                enddate = %(enddate)s,
                timelimit = %(timelimit)s,
                certificate = %(certificate)s,
                level = %(level)s,
                category = %(category)s,
                isActive = %(isActive)s,
                isHide = %(isHide)s
        """

        params = {
            "id": id,
            "user_id": user_id,
            "coursename": coursename,
            "description": description,
            "coursecode": coursecode,
            "price": price,
            "courselink": courselink,
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

        # Check if a new file is provided and update it if necessary
        if file:
            query += ", file = %(file)s"
            params["file"] = file

        # Check if a new course video is provided and update it if necessary
        if coursevideo:
            query += ", coursevideo = %(coursevideo)s"
            params["coursevideo"] = coursevideo

        # Add a WHERE clause to update the specific course based on its ID
        query += " WHERE id = %(id)s"

        return execute_query(query, params=params)

#Delete Courses
    @classmethod
    def delete_courses(cls, id):
        query = f""" DELETE FROM course WHERE id = '{id}'; """
        return execute_query(query)
    
###############################################################################################################

#Course Content CRUD
    def get_course_content_by_token(token):
        query = f"""SELECT * FROM {n_table_course_content} where token=%(token)s and token is not NULL and token != '';"""
        resp = execute_query(query=query, params={'token': token})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
        
#Get Course Content data by course_id for update fields Mapping
    def get_course_content_by_course_id(course_id):
        query = f"""SELECT * FROM course_content WHERE course_id = %(course_id)s AND course_id IS NOT NULL AND course_id != '';"""
        resp = execute_query(query=query, params={'course_id': course_id})
        data = resp.fetchone()
        if data is None:
            raise HTTPException(
                status_code=401, detail="Token Expired or Invalid Token")
        else:
            return data
        
    @classmethod
    def insert_course_content(cls, params):
        query = """
            INSERT INTO {n_table_course_content} (
                course_id, video_unitname, video_file, course_content_allowed, auth_token, request_token, token, active, deactive
            )
            VALUES (%(course_id)s, %(video_unitname)s, %(video_file)s, %(course_content_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(active)s, %(deactive)s);
        """
        return execute_query(query, params=params)
        
#Add Course Content
    @classmethod
    def add_course_content(cls, params):
        query = f"""
            INSERT INTO {n_table_course_content} (
                course_id, video_unitname, video_file, course_content_allowed, auth_token, request_token, token, active, deactive
            )
            VALUES (%(course_id)s, %(video_unitname)s, %(video_file)s, %(course_content_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(active)s, %(deactive)s);
                    """
        return execute_query(query, params=params)

#Fetch Course Content
    @classmethod
    def get_all_course_contents(cls):
        query = """ SELECT * FROM course_content; """
        return execute_query(query).fetchall()

#Fetch Course Content By virtualname
    @classmethod
    def get_course_content_by_video_unitname(cls, video_unitname):
        query = f"SELECT * FROM {n_table_course_content} WHERE video_unitname = %(video_unitname)s"
        params = {"video_unitname": video_unitname}
        resp = execute_query(query=query, params=params)
        data = resp.fetchone()
        if data is None:
            raise HTTPException(status_code=401, detail="Course Content not found")
        else:
            return data
        
#Update Course Content
    @classmethod
    def update_course_content_to_db(cls, id, course_id, video_unitname, video_file, active, deactive):
        query = f"""   
        UPDATE course_content SET
        course_id = %(course_id)s,
        video_unitname = %(video_unitname)s,
        video_file = %(video_file)s,
        active = %(active)s,
        deactive = %(deactive)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "course_id": course_id,
        "video_unitname": video_unitname,
        "video_file": video_file,
        "active": active,
        "deactive": deactive
    }
        return execute_query(query, params=params)
    
#Update Put call for course content fields and video
    @classmethod
    def update_course_content_fields(cls, course_id, update_params):
        # Check if there are any fields to update
        if not update_params:
            raise ValueError("No fields to update")

        # Construct a dynamic SQL query to update specific fields
        update_query = f"""
            UPDATE course_content
            SET {', '.join([f'{field} = %({field})s' for field in update_params.keys()])}
            WHERE course_id = %(course_id)s;
        """

        # Add user_id to the update_params
        update_params['course_id'] = course_id

        # Execute the query using your database library
        execute_query(update_query, params=update_params)

#Delete Course Content
    @classmethod
    def delete_course_content(cls, id):
        query = f""" DELETE FROM course_content WHERE id = '{id}'; """
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
        query = f"""   INSERT into {table_lmsgroup} (user_id, groupname,groupdesc,groupkey, group_allowed, auth_token, request_token, token, isActive) VALUES 
                        (%(user_id)s, %(groupname)s, %(groupdesc)s, %(groupkey)s, %(group_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(isActive)s)
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
    def update_group_to_db(cls, id, user_id, groupname, groupdesc, groupkey):
        query = f"""   
        UPDATE lmsgroup SET
            user_id = %(user_id)s,
            groupname = %(groupname)s,
            groupdesc = %(groupdesc)s,
            groupkey = %(groupkey)s
        WHERE id = %(id)s;
        """
        params = {
        "id":id,
        "user_id": user_id,
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

######################################## Users TAB Courses Page #################################################

    @classmethod
    def enroll_courses_user_enrollment(cls, params):
        query = f"""   INSERT INTO {users_courses_enrollment}
                    (user_id, course_id, u_c_enrollment_allowed, auth_token, request_token, token)
                    SELECT
                        %(user_id)s,
                        %(course_id)s,
                        %(u_c_enrollment_allowed)s,
                        %(auth_token)s,
                        %(request_token)s,
                        %(token)s
                    FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM {users_courses_enrollment}
                        WHERE user_id = %(user_id)s AND course_id = %(course_id)s
                    ); 
                    """
        return execute_query(query, params=params)

    @classmethod
    def get_allcourses_of_user(cls, user_id):
        query = """
            SELECT
                uce.course_id AS course_id,
                c.coursename,
                uce.id AS user_course_enrollment_id,
                uce.created_at AS enrolled_on,
                u.role AS user_role
            FROM user_course_enrollment uce
            LEFT JOIN course c ON uce.course_id = c.id
            LEFT JOIN users u ON uce.user_id = u.id
            WHERE uce.user_id = %(user_id)s

            UNION

            SELECT
                c.id AS course_id,
                c.coursename,
                NULL AS user_course_enrollment_id,
                NULL AS enrolled_on,
                u.role AS user_role
            FROM course c
            CROSS JOIN users u
            WHERE c.id NOT IN (
                SELECT course_id FROM user_course_enrollment WHERE user_id = %(user_id)s
            ) AND u.id = %(user_id)s;
        """
        params = {"user_id": user_id}
        return execute_query(query, params).fetchall()
    
    
#Delete or Remove Enrolled User from Course
    @classmethod
    def unenroll_courses_from_user(cls, id):
        query = f""" DELETE FROM user_course_enrollment WHERE id = '{id}'; """
        return execute_query(query)

######################################## Users TAB Courses Page(Admin,Instructor) #################################################

    @classmethod
    def get_enrollcourse_for_inst_learner(cls, user_id, admin_user_id):
        query = """
            SELECT
                uce.course_id AS course_id,
                c.coursename,
                uce.id AS user_course_enrollment_id,
                uce.created_at AS enrolled_on,
                CASE
                    WHEN u.role = 'admin' THEN 'Admin'
                    ELSE u.role
                END AS user_role,
                uce.id AS data_user_course_enrollment_id
            FROM user_course_enrollment uce
            LEFT JOIN course c ON uce.course_id = c.id
            LEFT JOIN users u ON uce.user_id = u.id
            WHERE 
                (
                    (u.role = 'instructor' OR u.role = 'learner')
                    AND uce.user_id = %(user_id)s
                )
                OR
                (
                    u.role = 'admin'
                    AND uce.user_id = %(admin_user_id)s
                )
            UNION
            SELECT
                c.id AS course_id,
                c.coursename,
                NULL AS user_course_enrollment_id,
                NULL AS enrolled_on,
                'Admin' AS user_role, -- Specify 'Admin' for admin-enrolled courses
                NULL AS data_user_course_enrollment_id
            FROM course c
            WHERE c.user_id = %(admin_user_id)s;
        """
        params = {"user_id": user_id, "admin_user_id": admin_user_id}
        return execute_query(query, params).fetchall()
    
############################# Courses Lists for for Admin,Instructor & Learner #############################################

    @classmethod
    def fetch_enrolled_course_details(cls, user_id):
        query = """
            SELECT
                uce.course_id AS course_id,
                c.*,
                uce.id AS user_course_enrollment_id,
                uce.created_at AS enrolled_on,
                u.role AS user_role,
                uce.id AS data_user_course_enrollment_id
            FROM user_course_enrollment uce
            LEFT JOIN course c ON uce.course_id = c.id
            LEFT JOIN users u ON uce.user_id = u.id
            WHERE uce.user_id = %(user_id)s

            UNION

            SELECT
                cu.id AS course_id,
                cu.*,
                NULL AS user_course_enrollment_id,
                NULL AS enrolled_on,
                NULL AS user_role,
                NULL AS data_user_course_enrollment_id
            FROM course cu
            WHERE cu.user_id = %(user_id)s;
            """
        params = {"user_id": user_id}
        return execute_query(query, params).fetchall()

    @classmethod
    def unenroll_courses_from_enrolled_user(cls, data_user_course_enrollment_id):
        query = f""" DELETE FROM user_course_enrollment WHERE id = {data_user_course_enrollment_id}; """
        return execute_query(query)
    
######################################## Users TAB Groups Page(Admin,Instructor) #################################################

    @classmethod
    def get_enrollgroup_for_inst_learner(cls, user_id, admin_user_id):
        query = """
            SELECT
                uge.group_id AS group_id,
                lg.groupname,
                uge.id AS user_group_enrollment_id,
                uge.created_at AS enrolled_on,
                CASE
                    WHEN u.role = 'admin' THEN 'Admin'
                    ELSE u.role
                END AS user_role,
                uge.id AS data_user_group_enrollment_id
            FROM user_group_enrollment uge
            LEFT JOIN lmsgroup lg ON uge.group_id = lg.id
            LEFT JOIN users u ON uge.user_id = u.id
            WHERE 
                (
                    (u.role = 'instructor' OR u.role = 'learner')
                    AND uge.user_id = %(user_id)s
                )
                OR
                (
                    u.role = 'admin'
                    AND uge.user_id = %(admin_user_id)s
                )
            UNION
            SELECT
                lg.id AS group_id,
                lg.groupname,
                NULL AS user_group_enrollment_id,
                NULL AS enrolled_on,
                'Admin' AS user_role, -- Specify 'Admin' for admin-enrolled groups
                NULL AS data_user_group_enrollment_id
            FROM lmsgroup lg
            WHERE lg.user_id = %(admin_user_id)s;
        """
        params = {"user_id": user_id, "admin_user_id": admin_user_id}
        return execute_query(query, params).fetchall()
    
############################# Groups Lists for Admin,Instructor & Learner #############################################

    @classmethod
    def fetch_enrolled_group_details(cls, user_id):
        query = """
            SELECT
                uge.group_id AS group_id,
                lg.*,
                uge.id AS user_group_enrollment_id,
                uge.id AS data_user_group_enrollment_id
            FROM user_group_enrollment uge
            LEFT JOIN lmsgroup lg ON uge.group_id = lg.id
            WHERE uge.user_id = %(user_id)s

            UNION

            SELECT
                lu.id AS group_id,
                lu.*,
                NULL AS user_group_enrollment_id,
                NULL AS data_user_group_enrollment_id
            FROM lmsgroup lu
            WHERE lu.user_id = %(user_id)s;
            """
        params = {"user_id": user_id}
        return execute_query(query, params).fetchall()
    
    @classmethod
    def remove_groups_from_enrolled_user(cls, data_user_group_enrollment_id):
        query = f""" DELETE FROM user_group_enrollment WHERE id = {data_user_group_enrollment_id}; """
        return execute_query(query)
    
######################################## Users TAB Group Page #################################################

    @classmethod
    def enroll_groups_to_user(cls, params):
        query = f"""   INSERT INTO {users_groups_enrollment}
                    (user_id, group_id, u_g_enrollment_allowed, auth_token, request_token, token)
                    SELECT
                        %(user_id)s,
                        %(group_id)s,
                        %(u_g_enrollment_allowed)s,
                        %(auth_token)s,
                        %(request_token)s,
                        %(token)s
                    FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM {users_groups_enrollment}
                        WHERE user_id = %(user_id)s AND group_id = %(group_id)s
                    ); 
                    """
        return execute_query(query, params=params)

#
    @classmethod
    def get_allgroups_of_user(cls, user_id):
        query = """
        SELECT
            e.group_id AS group_id,
            lg.groupname,
            e.id AS user_group_enrollment_id
        FROM user_group_enrollment e
        JOIN lmsgroup lg ON e.group_id = lg.id
        WHERE e.user_id = %(user_id)s

        UNION DISTINCT

        SELECT
            lg.id AS group_id,
            lg.groupname,
            NULL AS user_group_enrollment_id
        FROM lmsgroup lg
        WHERE lg.id NOT IN (SELECT group_id FROM user_group_enrollment WHERE user_id = %(user_id)s)
        ORDER BY group_id ASC; """
        params = {"user_id": user_id}
        return execute_query(query, params).fetchall()
    
    
#Delete or Remove Enrolled User from Course
    @classmethod
    def remove_groups_from_user(cls, id):
        query = f""" DELETE FROM user_group_enrollment WHERE id = '{id}'; """
        return execute_query(query)
    
######################################## Courses TAB Users Page(Admin,Instructor) #################################################

    @classmethod
    def get_enrollusers_to_course_for_inst_learner(cls, course_id, admin_user_id):
        query = """
            WITH AdminDept AS (
                SELECT
                    dept
                FROM users
                WHERE id = %(admin_user_id)s
            ),

            FilteredUsers AS (
                SELECT
                    u.id AS user_id,
                    u.full_name,
                    u.role,
                    NULL AS enrolled_on, -- Add a placeholder for enrolled_on
                    NULL AS user_course_enrollment_id
                FROM users u
                JOIN AdminDept ad ON u.dept = ad.dept
                WHERE u.role IN ('Instructor', 'Learner')
                AND u.id != 2 -- Exclude the admin_user_id (replace 2 with the actual admin_user_id)
            ),

            EnrolledUsers AS (
                SELECT
                    u.id AS user_id,
                    u.full_name,
                    u.role,
                    uce.created_at AS enrolled_on,
                    uce.id AS user_course_enrollment_id -- Include user_course_enrollment_id
                FROM user_course_enrollment uce
                JOIN users u ON uce.user_id = u.id
                JOIN AdminDept ad ON u.dept = ad.dept
                WHERE uce.course_id = %(course_id)s
            )

            SELECT * FROM FilteredUsers
            UNION ALL
            SELECT * FROM EnrolledUsers;
        """
        params = {"course_id": course_id, "admin_user_id": admin_user_id}
        return execute_query(query, params).fetchall()
    
######################################## Course TAB User Page #################################################

    @classmethod
    def enroll_users_to_course(cls, params):
        query = f"""   INSERT INTO {users_courses_enrollment}
                    (user_id, course_id, u_c_enrollment_allowed, auth_token, request_token, token)
                    SELECT
                        %(user_id)s,
                        %(course_id)s,
                        %(u_c_enrollment_allowed)s,
                        %(auth_token)s,
                        %(request_token)s,
                        %(token)s
                    FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM {users_courses_enrollment}
                        WHERE user_id = %(user_id)s AND course_id = %(course_id)s
                    ); 
                    """
        return execute_query(query, params=params)

#
    @classmethod
    def get_allusers_of_course(cls, course_id):
        query = """
        WITH AdminUsers AS (
            SELECT
                u.id AS user_id,
                u.role,
                u.full_name
            FROM users u
            WHERE u.role = 'Admin'
        ),
        CourseEnrollments AS (
            SELECT
                u.id AS user_id,
                c.coursename AS enrolled_coursename,
                e.id AS user_course_enrollment_id
            FROM users u
            LEFT JOIN user_course_enrollment e ON u.id = e.user_id
            LEFT JOIN course c ON e.course_id = c.id
            WHERE e.course_id = %(course_id)s
        )
        SELECT
            au.user_id,
            au.role,
            au.full_name,
            ce.enrolled_coursename,
            ce.user_course_enrollment_id
        FROM AdminUsers au
        LEFT JOIN CourseEnrollments ce ON au.user_id = ce.user_id;
        """
        params = {"course_id": course_id}
        return execute_query(query, params).fetchall()
    
    @classmethod
    def get_allinst_of_course(cls, course_id, user_id):
        query = """
            WITH InstructorUsers AS (
                SELECT
                    u.id AS user_id,
                    u.role,
                    u.full_name,
                    u.dept 
                FROM users u
                WHERE u.role = 'Instructor'
            ),
            CourseEnrollments AS (
                SELECT
                    u.id AS user_id,
                    c.coursename AS enrolled_coursename,
                    e.id AS user_course_enrollment_id
                FROM users u
                LEFT JOIN user_course_enrollment e ON u.id = e.user_id
                LEFT JOIN course c ON e.course_id = c.id
                WHERE e.course_id = %(course_id)s
            )
            SELECT
                iu.user_id,
                iu.role,
                iu.full_name,
                ce.enrolled_coursename,
                ce.user_course_enrollment_id
            FROM InstructorUsers iu
            LEFT JOIN CourseEnrollments ce ON iu.user_id = ce.user_id
            WHERE iu.dept = (SELECT dept FROM users WHERE id = %(user_id)s);
        """
        params = {"course_id": course_id, "user_id": user_id}
        return execute_query(query, params).fetchall()
    
    @classmethod
    def get_alllearner_of_course(cls, course_id):
        query = """
        WITH LearnerUsers AS (
            SELECT
                u.id AS user_id,
                u.role,
                u.full_name
            FROM users u
            WHERE u.role = 'Learner'
        ),
        CourseEnrollments AS (
            SELECT
                u.id AS user_id,
                c.coursename AS enrolled_coursename,
                e.id AS user_course_enrollment_id
            FROM users u
            LEFT JOIN user_course_enrollment e ON u.id = e.user_id
            LEFT JOIN course c ON e.course_id = c.id
            WHERE e.course_id = %(course_id)s
        )
        SELECT
            lu.user_id,
            lu.role,
            lu.full_name,
            ce.enrolled_coursename,
            ce.user_course_enrollment_id
        FROM LearnerUsers lu
        LEFT JOIN CourseEnrollments ce ON lu.user_id = ce.user_id;
        """
        params = {"course_id": course_id}
        return execute_query(query, params).fetchall()
    
#Delete or Remove Enrolled Course from User
    @classmethod
    def unenroll_users_from_course(cls, id):
        query = f""" DELETE FROM user_course_enrollment WHERE id = '{id}'; """
        return execute_query(query)
    
######################################## Courses TAB Groups Page(Admin,Instructor) #################################################

    @classmethod
    def get_enrollgroup_to_course_for_inst_learner(cls, course_id):
        query = """
            SELECT
                cge.course_id,
                cg.id AS group_id,
                cg.groupname,
                cg.user_id,
                cg.groupkey,
                u.role AS user_role,
                cge.id AS course_group_enrollment_id
            FROM course_group_enrollment cge
            JOIN lmsgroup cg ON cge.group_id = cg.id
            JOIN users u ON cg.user_id = u.id
            WHERE cge.course_id = %(course_id)s
            UNION ALL
            SELECT
                cge.course_id,
                cg.id AS group_id,
                cg.groupname,
                NULL AS user_id,
                cg.groupkey,
                u.role AS user_role,
                cge.id AS course_group_enrollment_id
            FROM course_group_enrollment cge
            JOIN lmsgroup cg ON cge.group_id = cg.id
            LEFT JOIN users u ON cg.user_id = u.id
            WHERE cge.course_id = %(course_id)s
            ORDER BY group_id ASC;
        """
        params = {"course_id": course_id}
        return execute_query(query, params).fetchall()
    
######################################## Course TAB Group Page #################################################

    @classmethod
    def add_groups_to_course(cls, params):
        query = f"""   INSERT INTO {courses_groups_enrollment}
                    (course_id, group_id, c_g_enrollment_allowed, auth_token, request_token, token)
                    SELECT
                        %(course_id)s,
                        %(group_id)s,
                        %(c_g_enrollment_allowed)s,
                        %(auth_token)s,
                        %(request_token)s,
                        %(token)s
                    FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM {courses_groups_enrollment}
                        WHERE course_id = %(course_id)s AND group_id = %(group_id)s
                    ); 
                    """
        return execute_query(query, params=params)

    @classmethod
    def get_allgroups_of_course(cls, course_id):
        query = """
            SELECT
                g.id AS group_id,
                g.groupname,
                c.coursename AS enrolled_coursename,
                cge.id AS course_group_enrollment_id
            FROM lmsgroup g
            LEFT JOIN course_group_enrollment cge ON g.id = cge.group_id AND cge.course_id = %(course_id)s
            LEFT JOIN course c ON cge.course_id = c.id
            ORDER BY g.id ASC;
            """
        params = {"course_id": course_id}
        return execute_query(query, params).fetchall()
        
#Delete or Remove Enrolled Course from Groups
    @classmethod
    def remove_groups_from_course(cls, id):
        query = f""" DELETE FROM course_group_enrollment WHERE id = '{id}'; """
        return execute_query(query)
    
######################################## Group TAB User Page #################################################

    @classmethod
    def add_users_to_group(cls, params):
        query = f"""   INSERT INTO {users_groups_enrollment}
                    (user_id, group_id, u_g_enrollment_allowed, auth_token, request_token, token)
                    SELECT
                        %(user_id)s,
                        %(group_id)s,
                        %(u_g_enrollment_allowed)s,
                        %(auth_token)s,
                        %(request_token)s,
                        %(token)s
                    FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM {users_groups_enrollment}
                        WHERE user_id = %(user_id)s AND group_id = %(group_id)s
                    ); 
                    """
        return execute_query(query, params=params)

#
    @classmethod
    def get_allusers_of_group(cls, group_id):
        query = """ 
            SELECT
                e.user_id AS user_id,
                u.role,
                u.full_name,
                e.id AS user_group_enrollment_id
            FROM user_group_enrollment e
            JOIN users u ON e.user_id = u.id
            WHERE e.group_id = %(group_id)s

            UNION DISTINCT

            SELECT
                u.id AS user_id,
                'Admin' AS role, -- Assuming role should be 'Admin'
                u.full_name,
                NULL AS user_group_enrollment_id
            FROM users u
            WHERE u.role = 'Admin'
                AND u.id NOT IN (SELECT user_id FROM user_group_enrollment WHERE group_id = %(group_id)s)
                ORDER BY user_id ASC; """
        params = {"group_id": group_id}
        return execute_query(query, params).fetchall()
    
    @classmethod
    def get_allinst_of_group(cls, group_id):
        query = """ 
            WITH InstructorUsers AS (
                SELECT
                    u.id AS user_id,
                    u.role,
                    u.full_name
                FROM users u
                WHERE u.role = 'Instructor'
            ),
            GroupEnrollments AS (
                SELECT
                    u.id AS user_id,
                    g.groupname AS enrolled_groupname,
                    e.id AS user_group_enrollment_id
                FROM users u
                LEFT JOIN user_group_enrollment e ON u.id = e.user_id
                LEFT JOIN lmsgroup g ON e.group_id = g.id
                WHERE e.group_id = %(group_id)s
            )
            SELECT
                iu.user_id,
                iu.role,
                iu.full_name,
                ge.enrolled_groupname,
                ge.user_group_enrollment_id
            FROM InstructorUsers iu
            LEFT JOIN GroupEnrollments ge ON iu.user_id = ge.user_id;
 """
        params = {"group_id": group_id}
        return execute_query(query, params).fetchall()
    
    @classmethod
    def get_alllearner_of_group(cls, group_id):
        query = """ 
            WITH LearnerUsers AS (
                SELECT
                    u.id AS user_id,
                    u.role,
                    u.full_name
                FROM users u
                WHERE u.role = 'Learner'
            ),
            GroupEnrollments AS (
                SELECT
                    u.id AS user_id,
                    g.groupname AS enrolled_groupname,
                    e.id AS user_group_enrollment_id
                FROM users u
                LEFT JOIN user_group_enrollment e ON u.id = e.user_id
                LEFT JOIN lmsgroup g ON e.group_id = g.id
                WHERE e.group_id = %(group_id)s
            )
            SELECT
                lu.user_id,
                lu.role,
                lu.full_name,
                ge.enrolled_groupname,
                ge.user_group_enrollment_id
            FROM LearnerUsers lu
            LEFT JOIN GroupEnrollments ge ON lu.user_id = ge.user_id; """
        params = {"group_id": group_id}
        return execute_query(query, params).fetchall()
        
#Delete or Remove added group from Users
    @classmethod
    def remove_users_from_group(cls, id):
        query = f""" DELETE FROM user_group_enrollment WHERE id = '{id}'; """
        return execute_query(query)
    
######################################## Groups TAB Users Page(Admin,Instructor) #################################################

    @classmethod
    def get_enrollusers_of_group_for_inst_learner(cls, group_id, admin_user_id):
        query = """
            WITH AdminDept AS (
                SELECT dept
                FROM users
                WHERE id = %(admin_user_id)s
            ),

            FilteredUsers AS (
                SELECT
                    u.id AS user_id,
                    u.full_name,
                    u.role,
                    NULL AS enrolled_on,
                    NULL AS user_group_enrollment_id
                FROM users u
                JOIN AdminDept ad ON u.dept = ad.dept
                WHERE u.role IN ('Instructor', 'Learner')
                AND u.id != %(admin_user_id)s -- Exclude the admin_user_id
            ),

            EnrolledUsers AS (
                SELECT
                    u.id AS user_id,
                    u.full_name,
                    u.role,
                    uge.created_at AS enrolled_on,
                    uge.id AS user_group_enrollment_id
                FROM user_group_enrollment uge
                JOIN users u ON uge.user_id = u.id
                JOIN AdminDept ad ON u.dept = ad.dept
                WHERE uge.group_id = %(group_id)s
            )

            SELECT * FROM FilteredUsers
            UNION ALL
            SELECT * FROM EnrolledUsers;
        """
        params = {"group_id": group_id,"admin_user_id": admin_user_id}
        return execute_query(query, params).fetchall()
    
######################################## Group TAB Course Page #################################################

    @classmethod
    def enroll_courses_to_group(cls, params):
        query = f"""   INSERT INTO {courses_groups_enrollment}
                    (course_id, group_id, c_g_enrollment_allowed, auth_token, request_token, token)
                    SELECT
                        %(course_id)s,
                        %(group_id)s,
                        %(c_g_enrollment_allowed)s,
                        %(auth_token)s,
                        %(request_token)s,
                        %(token)s
                    FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM {courses_groups_enrollment}
                        WHERE course_id = %(course_id)s AND group_id = %(group_id)s
                    );
                    """
        return execute_query(query, params=params)

    @classmethod
    def get_allcourses_of_group(cls, group_id):
        query = """ 
            SELECT
            c.id AS course_id,
            c.coursename,
            c.category,
            cge.id AS course_group_enrollment_id
        FROM course_group_enrollment cge
        LEFT JOIN course c ON cge.course_id = c.id
        WHERE cge.group_id = %(group_id)s

        UNION DISTINCT

        SELECT
            c.id AS course_id,
            c.coursename,
            c.category,
            NULL AS course_group_enrollment_id
        FROM course c
        WHERE c.id NOT IN (SELECT course_id FROM course_group_enrollment WHERE group_id = %(group_id)s)

        ORDER BY course_id ASC; """
        params = {"group_id": group_id}
        return execute_query(query, params).fetchall()
    
    
#Delete or Remove Enrolled Courses from Group
    @classmethod
    def remove_courses_from_group(cls, id):
        query = f""" DELETE FROM course_group_enrollment WHERE id = '{id}'; """
        return execute_query(query)
    



##################################################################################################################

    @classmethod
    def add_course_group_enrollment(cls, params):
        query = f"""  
            INSERT INTO {courses_groups_enrollment} 
            (course_id, group_id, c_g_enrollment_allowed, auth_token, request_token, token)
            VALUES 
            (%(course_id)s, %(group_id)s, %(c_g_enrollment_allowed)s, %(auth_token)s, %(request_token)s, %(token)s)
            ON DUPLICATE KEY UPDATE
            course_id = VALUES(course_id),
            group_id = VALUES(group_id),
            c_g_enrollment_allowed = VALUES(c_g_enrollment_allowed),
            auth_token = VALUES(auth_token),
            request_token = VALUES(request_token),
            token = VALUES(token);
        """
        return execute_query(query, params=params)

    #Delete or Remove Enrolled Courses from Group
    @classmethod
    def remove_course_from_all_groups(cls, course_id):
        query = f"""DELETE FROM {courses_groups_enrollment} WHERE course_id = %(course_id)s;"""
        params = {'course_id': course_id}
        return execute_query(query, params=params)
    
    @classmethod
    def get_all_user_course_enrollment(cls):
        query = """ SELECT user_id, role, full_name, coursename, user_course_enrollment_id FROM (
            SELECT e.user_id as user_id, u.role, u.full_name, c.coursename, e.id as user_course_enrollment_id, NULL as email, NULL as dept, NULL as adhr, NULL as username, NULL as password, NULL as bio, NULL as file, NULL as timezone, NULL as langtype, NULL as users_allowed, NULL as auth_token, NULL as request_token, NULL as token, NULL as active, NULL as deactive, NULL as exclude_from_email, NULL as created_at, NULL as updated_at
            FROM user_course_enrollment e
            JOIN users u ON e.user_id = u.id
            JOIN course c ON e.course_id = c.id
            WHERE u.role = 'Admin'

            UNION DISTINCT

            SELECT id as user_id, role, full_name, NULL as coursename, NULL as user_course_enrollment_id, NULL as email, NULL as dept, NULL as adhr, NULL as username, NULL as password, NULL as bio, NULL as file, NULL as timezone, NULL as langtype, NULL as users_allowed, NULL as auth_token, NULL as request_token, NULL as token, NULL as active, NULL as deactive, NULL as exclude_from_email, NULL as created_at, NULL as updated_at
            FROM users
            WHERE role = 'Admin' AND id NOT IN (SELECT user_id FROM user_course_enrollment WHERE user_id IS NOT NULL)
        ) AS combined_data; """
        return execute_query(query).fetchall()

######################################## Courses TAB Groups Page(Admin,Instructor) #################################################

    @classmethod
    def get_enrollcourse_to_group_for_inst_learner(cls, group_id):
        query = """
            SELECT
                cge.group_id,
                cg.id AS course_id,
                cg.coursename,
                cg.user_id,
                u.role AS user_role,
                cge.id AS course_group_enrollment_id
            FROM course_group_enrollment cge
            JOIN course cg ON cge.course_id = cg.id
            JOIN users u ON cg.user_id = u.id
            WHERE cge.group_id = %(group_id)s
            UNION ALL
            SELECT
                cge.group_id,
                cg.id AS course_id,
                cg.coursename,
                NULL AS user_id,
                u.role AS user_role,
                cge.id AS course_group_enrollment_id
            FROM course_group_enrollment cge
            JOIN course cg ON cge.course_id = cg.id
            LEFT JOIN users u ON cg.user_id = u.id
            WHERE cge.group_id = %(group_id)s
            ORDER BY course_id ASC;
        """
        params = {"group_id": group_id}
        return execute_query(query, params).fetchall()
    
####################################################################################################################

#Files / Documents
    @classmethod
    def add_files(cls, params):
        query = f"""   INSERT into {n_table_user_files} (user_id, files, files_allowed, auth_token, request_token, token, active, created_at, updated_at) VALUES 
                        (%(user_id)s, %(files)s, %(files_allowed)s, %(auth_token)s, %(request_token)s, %(token)s, %(active)s, %(created_at)s, %(updated_at)s)
                        ;
                    """
        return execute_query(query, params=params)

    @classmethod
    def fetch_active_files(cls):
        query = """ SELECT * FROM documents WHERE active = ; """
        return execute_query(query).fetchall()
    

    @classmethod
    def remove_files(cls, id):
        query = f""" DELETE FROM documents WHERE id = '{id}'; """
        return execute_query(query)

####################################################################################################################

    @classmethod
    def user_wise_infographics(cls, user_id):
        query = """
            SELECT 
            u.full_name,
            uce.course_id,
            c.coursename,
            up.points,
            up.user_level,
            uc.total_course_count
        FROM
            users u
        LEFT JOIN
            user_course_enrollment uce
        ON
            u.id = uce.user_id
        LEFT JOIN
            course c
        ON
            uce.course_id = c.id
        JOIN
            user_points up
        ON
            u.id = up.user_id
        LEFT JOIN (
            SELECT 
                user_id,
                COUNT(*) as total_course_count
            FROM
                user_course_enrollment
            GROUP BY
                user_id
        ) uc
        ON
            u.id = uc.user_id
        WHERE
            u.id = %(user_id)s; 
            """
        params = {"user_id": user_id}
        return execute_query(query, params).fetchall()

    @classmethod
    def learner_overview(cls, user_id):
        query = """
            SELECT 
            u.full_name,
            c.coursename,
            up.points,
            up.user_level,
            uc.total_course_count,
            u.file,
            u.bio,
            u.created_at
            FROM users u
            LEFT JOIN user_course_enrollment uce ON u.id = uce.user_id
            LEFT JOIN course c ON uce.course_id = c.id
            JOIN user_points up ON u.id = up.user_id
            LEFT JOIN (
                SELECT 
                user_id,
                COUNT(*) as total_course_count
                FROM user_course_enrollment
                GROUP BY user_id
            ) uc ON u.id = uc.user_id
            WHERE u.id = %(user_id)s; 
            """
        params = {"user_id": user_id}
        return execute_query(query, params).fetchall()

    




    