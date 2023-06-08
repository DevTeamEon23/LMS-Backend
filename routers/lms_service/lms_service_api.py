from fastapi import APIRouter, Depends
from starlette import status

from routers.authenticators import verify_user
from routers.lms_service.lms_service_ops import sample_data
from schemas.lms_service_schema import CategorySchema
from utils import success_response

service = APIRouter(tags=["Service :  Service Name"], dependencies=[Depends(verify_user)])


@service.post("/list-data")
def get_list_data(payload:CategorySchema):
    return success_response(status_code=status.HTTP_200_OK, data=sample_data(payload))
