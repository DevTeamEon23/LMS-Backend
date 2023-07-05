import hashlib
import string
import re
from random import SystemRandom

from fastapi import Header
from fastapi.security import APIKeyHeader
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse


AUTH_TOKEN = APIKeyHeader(name='auth-token', scheme_name="user-token")
regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # better


def success_response(status_code=200, data=[], message="", is_type_auto: bool = True):
    """
    The success_response function is a helper function that returns a JSONResponse object with the following properties:
        - status_code: The HTTP status code of the response. Defaults to 200 (OK).
        - content: A dictionary containing two keys, &quot;message&quot; and &quot;data&quot;.
        - message: A string containing an optional message about the request. Defaults to empty string (&quot;&quot;).
        - data: An array or dictionary containing any data returned by your API endpoint. Defaults to empty list ([]).

    :param status_code: Set the status code of the response
    :param data: Pass the data to be returned
    :param message: Display a message to the user
    :param is_type_auto: bool: Determine whether the response should be returned as a json response object or just a dictionary
    :return: A json response object with a status code, data and message

    """
    if is_type_auto:
        return JSONResponse(status_code=status_code, content=dict(message=message, data=data))
    else:
        return dict(message=message, data=data)


def failure_response(status_code=200, message="", is_type_auto: bool = True):
    """
    The success_response function is a helper function that returns a JSONResponse object with the following properties:
        - status_code: The HTTP status code of the response. Defaults to 200 (OK).
        - content: A dictionary containing two keys, &quot;message&quot; and &quot;data&quot;.
        - message: A string containing an optional message about the request. Defaults to empty string (&quot;&quot;).
        - data: An array or dictionary containing any data returned by your API endpoint. Defaults to empty list ([]).

    :param status_code: Set the status code of the response

    :param message: Display a message to the user
    :param is_type_auto: bool: Determine whether the response should be returned as a json response object or just a dictionary
    :return: A json response object with a status code, data and message

    """
    if is_type_auto:
        return JSONResponse(status_code=status_code, content=dict(message=message))
    else:
        return dict(message=message)


def generate_token(token, host):
    """
    The generate_token function is used to generate a new token for the user.
        It takes in an authorization token as input and verifies it with the parent server.
        If valid, it generates a new token and stores it in cache.

    :param token: token to  Verify the with the parent server
    :return: A token

    """
    pass
    # url = f"{host}/auth/verify-token"
    # response = requests.get(url, headers={"auth-token": token}, verify=False)
    # if response.status_code == 200:
    # response_data: dict = response.json()
    # _token = response_data['token']
    # if DBHandler.cache_token(_token, datetime.now(), datetime.now() + relativedelta(minutes=settings.TOKEN_BUFFER_TIME)):
    # logger.info(f"Token Added : {_token}")

    # else:
    # logger.error(response.json())
    # raise HTTPException(status_code=401, detail="Authorization Token is invalid")


def chunkify(lst, batch_size):
    batches = {id: lst[batch_num[0]: batch_num[1]] for id, batch_num in enumerate(
        [i, i + batch_size] for i in range(0, len(lst), batch_size))}
    return batches


def random_string(n=10):
    return ''.join(SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n))


def md5(data: str) -> str:
    if type(data) == str:
        data = data.encode()
    c = hashlib.md5(data)
    encrypt = c.hexdigest()
    return encrypt


def validate_email(email):
    # pass the regular expression
    # and the string into the fullmatch() method
    if re.fullmatch(regex_email, email):
        return True
    else:
        return False

def validate_emails(email):
    if not isinstance(email, str):
        return False
    if re.fullmatch(regex_email, email):
        return True
    else:
        return False
    

if __name__ == "__main__":
    pass
