import Mangum as Mangum

from app import app

mangum_app = Mangum(app=app)


def lambda_handler(event: dict, context):
    return mangum_app(event, context)
