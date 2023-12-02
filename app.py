"""
    This is the main entry point for the Api
"""
import traceback

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from config import settings
from config.logconfig import logger

from routers.auth.auth_service_api import auth
from routers.lms_service.lms_service_api import service, user_tab1,user_tab2, course_tab1,course_tab2, group_tab1,group_tab2

app = FastAPI(title="EonLearnings", debug=settings.DEBUG, docs_url=settings.DOCS_URL, redoc_url=settings.REDOC_URL,
              openapi_url=settings.OPENAPI_URL)

# Set up Pre-configured Routes
app.add_middleware(GZipMiddleware, minimum_size=500)

app.mount("/media/", StaticFiles(directory="media/"), name="media")
app.mount("/course/", StaticFiles(directory="course/"), name="course")
app.mount("/coursevideo/", StaticFiles(directory="coursevideo/"), name="coursevideo")
app.mount("/files/", StaticFiles(directory="files/"), name="files")
app.mount("/exported_files/", StaticFiles(directory="exported_files/"), name="exported_files")
app.mount("/uploads/", StaticFiles(directory="uploads/"), name="uploads")
app.mount("/courseppt/", StaticFiles(directory="courseppt/"), name="courseppt")
app.mount("/coursescorm/", StaticFiles(directory="coursescorm/"), name="coursescorm")

# Modify Default Exception Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Get the original 'detail' list of errors
    details = exc.errors()
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "status": "failure",
                "message": f"{details[0]['loc'][-1]}:{details[0]['msg']}",
            }
        ),
    )


# Default Exceptions Handling
@app.exception_handler(Exception)
def default_exception_handler(request, exc):
    logger.error(f"Default Exception: {exc}\nTraceback: {''.join(traceback.format_tb(exc.__traceback__))}")
    return JSONResponse(content={"message": "unknown error"}, status_code=status.HTTP_400_BAD_REQUEST)


# Set MiddleWare
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services Registration
app.include_router(auth, prefix="/auth")
app.include_router(service, prefix="/lms-service")
app.include_router(user_tab1, prefix="/user-tab1")
app.include_router(user_tab2, prefix="/user-tab2")

app.include_router(course_tab1, prefix="/course_tab1")
app.include_router(course_tab2, prefix="/course_tab2")

app.include_router(group_tab1, prefix="/group_tab1")
app.include_router(group_tab2, prefix="/group_tab2")

@app.get('/')
def root_message():
    return{"Welcome To EonLearning LMS Application Have a Great Day! 🌻👨‍💻🌹"}

@app.on_event('startup')
def startup_function():
    # create_database()
    pass