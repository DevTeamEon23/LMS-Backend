from mangum import Mangum

from analysis import process_sqs_analysis_event
from dashboard.app import app

mangum_app = Mangum(app=app)


def lambda_handler(event: dict, context):
    is_sqs = event.get('Records', None) is not None and len(event['Records']) > 0
    if is_sqs:
        records = event.get('Records')
        for _record in records:
            _body = _record['body']
            print(_body)
            process_sqs_analysis_event(_body)
        return {'statusCode': 200, 'body': 'event processed success', 'headers': {"content-type": 'application/json'}}
    else:
        response = mangum_app(event, context)
        return response