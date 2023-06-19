import traceback
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends
from starlette import status
from schemas.lms_service_schema import User
from routers.authenticators import verify_user
from routers.lms_service.lms_service_ops import sample_data, fetch_all_users_data
from schemas.lms_service_schema import CategorySchema
from utils import success_response
from config.logconfig import logger


service = APIRouter(tags=["Service :  Service Name"], dependencies=[Depends(verify_user)])


@service.post("/list-data")
def get_list_data(payload:CategorySchema):
    return success_response(status_code=status.HTTP_200_OK, data=sample_data(payload))


@service.get("/users")
def fetch_all_users():
    try:
        # Fetch all users' data here
        users = fetch_all_users_data()

        return {
            "status": "success",
            "data": users
        }
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={
            "status": "failure",
            "message": "Failed to fetch users' data"
        })