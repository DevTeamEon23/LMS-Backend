import random
import traceback
from routers.db_ops import execute_query
from config.db_config import n_table_user
from config.logconfig import logger
from routers.lms_service.lms_db_ops import LmsHandler
from schemas.lms_service_schema import User
from starlette.responses import JSONResponse
from starlette import status


def sample_data(payload):
    logger.info(payload)
    return {
        "A":random.randint(100,1500),
    }

def fetch_all_users_data():
    try:
        # Query all users from the database
        users = LmsHandler.get_all_users()

        # Transform the user objects into a list of dictionaries
        users_data = []
        for user in users:
            user_data = {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "email": user.email,
                "token": user.token,
                "active": user.active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                # Include other user attributes as needed
            }
            users_data.append(user_data)

        return users_data
    except Exception as exc:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={
            "status": "failure",
            "message": "Failed to fetch users data"
        })