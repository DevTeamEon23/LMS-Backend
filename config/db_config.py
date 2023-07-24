import sqlalchemy as sql
from sqlalchemy import MetaData, Table, Column, String, Integer, DECIMAL, VARCHAR, Index, UniqueConstraint, \
    func, BOOLEAN, create_engine, Date, BigInteger, event, DDL, Float, ForeignKey,Enum
from sqlalchemy.dialects.postgresql import JSONB, UUID, TIMESTAMP,BYTEA
from sqlalchemy.dialects.mysql import LONGBLOB
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base, configure_mappers
from .settings import settings
from enum import Enum as PythonEnum
engine_str = f'mysql+mysqlconnector://{settings.PG_USER}:{settings.PG_PASSWORD}@{settings.PG_HOST}:{settings.PG_PORT}/{settings.DBNAME}'
connection = sql.create_engine(engine_str)

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class Role(PythonEnum):
    Superadmin = 'Superadmin'
    Admin = 'Admin'
    Instructor = 'Instructor'
    Learner = 'Learner'

class TimeZoneEnum(PythonEnum):
    IST = 'IST'
    NST = 'NST'
    AST = 'AST'
    ECT = 'ECT'
    GMT = 'GMT'
    ARABIC = 'ARABIC'

class LanguageEnum(PythonEnum):
    English = 'English'
    Hindi = 'Hindi'
    Marathi = 'Marathi'

class Certificate(PythonEnum):
    Certificate1 = 'Certificate1'
    Certificate2 = 'Certificate2'
    Certificate3 = 'Certificate3'
    Certificate4 = 'Certificate4'

class Level(PythonEnum):
    level1 = 'level1'
    level2 = 'level2'
    level3 = 'level3'
    level4 = 'level4'

class ParentCategory(PythonEnum):
    ParentCategory1 = 'ParentCategory1'
    ParentCategory2 = 'ParentCategory2'
    ParentCategory3 = 'ParentCategory3'
    ParentCategory4 = 'ParentCategory4'

class EventEnum(PythonEnum):
    Selectevent = 'Selectevent'
    Onusercreate = 'Onusercreate'
    Onusersignup = 'Onusersignup'
    Xhoursafterusersignup = 'Xhoursafterusersignup'
    Xhoursafterusersignupandtheuserhasnotmadeapurchase = 'Xhoursafterusersignupandtheuserhasnotmadeapurchase'
    Xhoursafterusercreation = 'Xhoursafterusercreation'
    Xhoursafterusercreationandtheuserhasnotsignedin = ''
    Xhoursafterusersignupandtheuserhasnotsignedin = ''
    Xhourssinceuserlastsignedin = ''
    Xhourssinceuserfirstsigninandtheuserhasnotcompletedanycourse = ''
    Xhoursbeforeuserdeactivation = 'Xhoursbeforeuserdeactivation'
    Oncourseassignment = 'Oncourseassignment'
    Oncourseselfassignment = 'Oncourseselfassignment'
    Xhoursaftercourseacquisition = 'Xhoursaftercourseacquisition'
    Xhoursbeforecoursestart = 'Xhoursbeforecoursestart'
    Oncoursecompletion = 'Oncoursecompletion'
    Xhoursaftercoursecompletion = 'Xhoursaftercoursecompletion'
    Oncoursefailure = 'Oncoursefailure'
    Oncourseexpiration = 'Oncourseexpiration'
    Xhoursbeforecourseexpiration = 'Xhoursbeforecourseexpiration'
    Oncertificateacquisition = 'Oncertificateacquisition'
    Oncertificateexpiration = 'Oncertificateexpiration'
    Xhoursbeforecertificateexpiration = 'Xhoursbeforecertificateexpiration'
    Ongroupassignment = 'Ongroupassignment'
    Onbranchassignment = 'Onbranchassignment'
    Onassignmentsubmission = 'Onassignmentsubmission'
    Onassignmentgrading = 'Onassignmentgrading'
    OnILTsessioncreate = 'OnILTsessioncreate'
    OnILTsessionregistration = 'OnILTsessionregistration'
    XhoursbeforeanILTsessionstarts = 'XhoursbeforeanILTsessionstarts'
    OnILTgrading = 'OnILTgrading'
    Onuserpayment = 'Onuserpayment'
    OnlevelXreached = 'OnlevelXreached'

class RecipientEnum(PythonEnum):
    Selectrecipient = 'Selectrecipient'
    Relateduser = 'Relateduser'
    Accountowner = 'Accountowner'
    SuperAdmins = 'SuperAdmins'
    Branchadmins = 'Branchadmins'
    Courseinstructors = 'Courseinstructors'
    Courselearners = 'Courselearners'
    Specificrecipients = 'Specificrecipients'

#Discussion
class Access(PythonEnum):
    Access1 = 'Access1'
    Access2 = 'Access2'
    Access3 = 'Access3'

#Calendar
class Audience(PythonEnum):
    Audience1 = 'Audience1'
    Audience2 = 'Audience2'
    Audience3 = 'Audience3'


#Tables Codes Go Here --*
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

table_course = 'course'
s_table_course = Table(
    table_course, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('coursename',VARCHAR(30), nullable=False),
    Column('file',LONGBLOB, nullable=False),
    Column('description',VARCHAR(255), nullable=False),
    Column('coursecode',VARCHAR(20), unique=True),
    Column('price', Float(10, 2)),
    Column('courselink', VARCHAR(255)),
    Column('coursevideo',LONGBLOB),
    Column('capacity', VARCHAR(20)),
    Column('startdate', VARCHAR(20)),
    Column('enddate', VARCHAR(20)),
    Column('timelimit', VARCHAR(20)),
    Column('certificate', Enum(Certificate), server_default='Certificate1', nullable=False),
    Column('level', Enum(Level), server_default='level1', nullable=False),
    # Column('category', Enum(ParentCategory), server_default='ParentCategory1', nullable=False),
    Column('category', Integer, ForeignKey('category.id'), nullable=False),
    Column('course_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('isActive', BOOLEAN, default=True),
    Column('isHide', BOOLEAN, default=False),
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    UniqueConstraint('coursecode', name=f'uq_{table_course}_couref'),
    Index(f'idx_{table_course}_token', 'token'),
)

# lmsgroup table
table_lmsgroup = 'lmsgroup'
s_table_lmsgroup = Table(
    table_lmsgroup, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('groupname', VARCHAR(45), nullable=False),
    Column('groupdesc', VARCHAR(255), nullable=False),
    Column('groupkey', VARCHAR(20)),
    Column('group_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    UniqueConstraint('groupkey', name=f'uq_{table_lmsgroup}_grpref'),
    Index(f'idx_{table_lmsgroup}_token', 'token'),
)

# lmsevent table
table_lmsevent = 'lmsevent'
s_table_lmsevent = Table(
    table_lmsevent, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('ename', VARCHAR(20), nullable=False),
    Column('eventtype', Enum(EventEnum), nullable=False),
    Column('recipienttype', Enum(RecipientEnum), nullable=False),
    Column('descp', VARCHAR(300)),
    Column('isActive', BOOLEAN, default=True),
    Column('event_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Index(f'idx_{table_lmsevent}_token', 'token'),
)

# parentcategory table
table_parentcategory = 'parentcategory'
s_table_parentcategory = Table(
    table_parentcategory, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', VARCHAR(45)),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Index(f'idx_{table_parentcategory}_token', 'token'),
)

# virtualtraining table
table_virtualtraining = 'virtualtraining'
s_table_virtualtraining = Table(
    table_virtualtraining, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('instname', VARCHAR(45)),
    Column('virtualname', VARCHAR(20)),
    Column('date', VARCHAR(20)),
    Column('starttime', VARCHAR(20)),
    Column('meetlink', VARCHAR(455)),
    Column('messg', VARCHAR(655)),
    Column('duration', VARCHAR(20)),
    Column('virtualtraining_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Index(f'idx_{table_virtualtraining}_token', 'token'),
)

# category table
table_category = 'category'
s_table_category = Table(
    table_category, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', VARCHAR(20)),
    Column('price', Float(10, 2)),
    Column('category_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Index(f'idx_{table_category}_token', 'token'),
)

# classroom table
table_classroom = 'classroom'
s_table_classroom = Table(
    table_classroom, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('instname', VARCHAR(45)),
    Column('classname', VARCHAR(20)),
    Column('date', VARCHAR(20)),
    Column('starttime', VARCHAR(20)),
    Column('venue', VARCHAR(455)),
    Column('messg', VARCHAR(655)),
    Column('duration', VARCHAR(20)),
    Column('classroom_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Index(f'idx_{table_classroom}_token', 'token'),
)

# conference table
table_conference = 'conference'
s_table_conference = Table(
    table_conference, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('instname', VARCHAR(45)),
    Column('confname', VARCHAR(20)),
    Column('date', VARCHAR(20)),
    Column('starttime', VARCHAR(20)),
    Column('meetlink', VARCHAR(455)),
    Column('messg', VARCHAR(655)),
    Column('duration', VARCHAR(20)),
    Column('conference_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Index(f'idx_{table_conference}_token', 'token'),
)

# Discussion table
table_discussion = 'discussion'
s_table_discussion = Table(
    table_discussion, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('topic', VARCHAR(45)),
    Column('messg', VARCHAR(655)),
    Column('file', VARCHAR(20)),
    Column('access', Enum(Access), server_default='Access1', nullable=False),
    Column('discussion_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Index(f'idx_{table_discussion}_token', 'token'),
)

# calender table
table_calender = 'calender'
s_table_calender = Table(
    table_calender, metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('cal_eventname', VARCHAR(45)),
    Column('date', VARCHAR(20)),
    Column('starttime', VARCHAR(20)),
    Column('duration', VARCHAR(20)),
    Column('audience', Enum(Audience), server_default='Audience1', nullable=True),
    Column('messg', VARCHAR(655)),
    Column('calender_allowed', VARCHAR(150), nullable=False),
    Column('auth_token', VARCHAR(2500), nullable=False),  # Google
    Column('request_token', VARCHAR(2500), nullable=False),
    Column('token', VARCHAR(100), nullable=False),  # For data endpoints
    Column('created_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Column('updated_at', TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
    Index(f'idx_{table_calender}_token', 'token'),
)

meta_engine = sql.create_engine(engine_str, isolation_level='AUTOCOMMIT')
metadata.create_all(meta_engine, checkfirst=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=meta_engine)
# Close the engine
meta_engine.dispose()


if __name__=="__main__":
   pass