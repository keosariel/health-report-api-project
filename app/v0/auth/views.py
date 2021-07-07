from flask import request, current_app
from flask.views import MethodView

from app.helpers import (
    response_data,
    args_check,
    JSONObject
)

from app.v0.auth.validators import LoginValidator, RegisterValidator
from app.errors import E005, E006, E015, E016, E017
from app.models import User


class LoginView(MethodView):

    def get(self, access_token):
        try:
            if access_token:
                valid, user_id = User.decode_token(access_token.strip())
                if valid:
                    user = User.query.get(user_id)
                    if user:
                        res = (
                            response_data(
                                {"islogged_in": True, "user": user.to_dict(flag=1)}
                            )
                        )
                        return res

        except Exception as err:
            print(err)

        res = (
            response_data(
                {"islogged_in": False, "user": None}
            )
        )

        return res

    @args_check(LoginValidator())
    def post(self):
        """Handles POST request"""

        json_data = JSONObject(request.json)

        with current_app.app_context():
            email = (
                json_data.email.strip()
            )

            user = (
                User.query.filter_by(email=email)
                .first()
            )

            if user:
                if user.password_is_valid(json_data.password):
                    access_token = user.generate_token()

                    res = (
                        response_data(
                            {"access_token": access_token,
                                "user": user.to_dict(flag=1)}
                        )
                    )

                    return res

        # E006 = Login Error
        res = response_data(
            data=None,
            error_code=E006
        )

        return res


class RegisterView(MethodView):

    @args_check(RegisterValidator())
    def post(self):
        """Handles POST request"""

        json_data = JSONObject(request.json)

        with current_app.app_context():
            name = json_data.name.lower().strip()
            email = json_data.email.strip()
            is_doctor = json_data.is_doctor

            _user = User.query.filter_by(email=email).first()
            if _user:
                # E016 = Email Already Exists
                res = response_data(
                    data=None,
                    error_code=E016
                )

                return res

            # Creating a User instance
            user = User(
                name=name,
                email=email,
                password=json_data.password,
                is_doctor=bool(is_doctor)
            )

            # Adding instance to the database
            user.save()

            # Setting public id
            user.set_public_id()

            access_token = user.generate_token()

            res = (
                response_data(
                    {"access_token": access_token, "user": user.to_dict(flag=1)}
                )
            )

            return res

        # E005 = SignUp Error
        res = response_data(
            data=None,
            error_code=E005
        )

        return res
