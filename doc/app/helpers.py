from hashlib import md5

from functools import wraps
from flask import jsonify, request
from app.errors import E004, E002
from app.errors import ERRORS_DESCRIPTION, ERRORS_STATUS_CODE
from app.status_codes import BAD_REQUEST, SUCCESS_NO_CONTENT


def get_public_id(unique_id):
    return md5(str(unique_id).encode("UTF-8")).hexdigest()


def response_data(data, error_code=None, description="", error_data=None, status_code=200):
    data = data
    has_error = True if error_code else False

    if not description:
        description = ERRORS_DESCRIPTION.get(error_code, "")

    if has_error and error_code:
        status_code = ERRORS_STATUS_CODE.get(error_code, BAD_REQUEST)

    ret_json = {
        "data": data,
        "error_code": error_code,
        "has_error": has_error,
        "description": description,
        "error_data": error_data,
        "status_code": status_code
    }

    return jsonify(ret_json), status_code


def args_check(validator):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            json_data = request.json if request.json else {}
            no_err, msg = validator.validate(json_data)

            if not no_err:
                # E002 = Invalid Request JSON
                res = response_data(
                    data=None,
                    error_code=E002,
                    error_data=msg
                )

                return res

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def login_required(optional=False):
    def _login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from app.models import User

            # E004 = Authentication Error (406)
            res = response_data(
                data=None,
                error_code=E004,
                description="No Authorization Header"
            )

            access_token = None

            try:
                auth_header = request.headers.get('Authorization')
                access_token = auth_header.split(" ")[1]
            except Exception:
                if not optional:
                    return res
            
            if access_token:
                valid, user_id = User.decode_token(access_token.strip())
                if valid:
                    kwargs["current_user"] = {"id": user_id}
                    return f(*args, **kwargs)

            if optional:
                kwargs["current_user"] = {"id": None}
                return f(*args, **kwargs)

            # E004 = Authentication Error (406)
            res = response_data(
                data=None,
                error_code=E004,
                description="You need to Login"
            )

            return res

        return decorated_function
    return _login_required


def get_http_exception_handler(app):
    """Overrides the default http exception handler to return JSON."""

    handle_http_exception = app.handle_http_exception

    @wraps(handle_http_exception)
    def ret_val(exception):
        code = exception.code
        description = exception.description

        res = response_data(
            data=None,
            description=description,
            status_code=code
        )

        return res

    return ret_val


class JSONObject(object):
    def __init__(self, _dict):
        self.keys = []
        if type(_dict) == dict:
            self.keys = list(_dict.keys())
            for k, v in _dict.items():
                try:
                    self.__setattr__(k, v)
                except Exception:
                    pass

    def has(self, key):
        return key in self.keys

    def get(self, key):
        if self.has(key):
            return self.__getattribute__(key)
        return None

    def isnull(self, key):
        if self.has(key):
            return not bool(self.__getattribute__(key))
        self.keys.append(key)
        self.__setattr__(key, None)
        return True

    def hasall(self, keys):
        for key in keys:
            if not self.has(key):
                return False
        return True
