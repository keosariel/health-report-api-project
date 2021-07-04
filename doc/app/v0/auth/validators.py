from flask_jsonvalidator import (
    JSONValidator,
    StringValidator,
    BooleanValidator
)

from app.regex import NAME, PASSWORD, EMAIL


class LoginValidator(JSONValidator):
    validators = {
        "email": StringValidator(nullable=False, err_msg="Invalid Email address"),
        "password": StringValidator(nullable=False, err_msg="Password field cannot be empty")
    }


class RegisterValidator(JSONValidator):
    validators = {
        "name": StringValidator(regex=NAME, nullable=False, err_msg="Invalid Name"),
        "email": StringValidator(regex=EMAIL, nullable=False, err_msg="Invalid Email address"),
        "is_doctor": BooleanValidator(nullable=False),
        "password": StringValidator(regex=PASSWORD, nullable=False, err_msg="Password must be at least 8 characters long and must contain at least one *capital letter [A-Z]* and one *number [0-9]*")
    }
