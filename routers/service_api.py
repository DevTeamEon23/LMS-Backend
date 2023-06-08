from fastapi import APIRouter, Depends
from starlette import status

from routers.authenticators import verify_user
from routers.service_ops import sample_data
from utils import success_response

service = APIRouter(tags=["Service :  Service Name"], dependencies=[Depends(verify_user)])


@service.get("/list-data")
def get_list_data():
    return success_response(status_code=status.HTTP_200_OK, data=sample_data())
