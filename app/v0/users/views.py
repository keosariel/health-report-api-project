from flask import request, current_app
from flask.views import MethodView

from app.helpers import (
    response_data,
    args_check,
    login_required,
    JSONObject
)
from app.v0.users.validators import UserValidator, ChangePasswordValidator, RequestPasswordChangeValidator
from app.errors import E000, E007, E008, E009, E015, E016, E017, E018, E019
from app.models import User
from app.v0.users import users


@args_check(RequestPasswordChangeValidator())
@users.route("/v0/change_password_request", methods=["POST"])
def request_change_password():
    """Handles PATCH request"""

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
            access_token = user.generate_token(minutes=30)

            res = (
                response_data(
                    data=None
                )
            )

            return res
        else:
            # E018 = Email does not exists
            res = response_data(
                data=None,
                error_code=E018
            )

            return res

    # E017 = Incorrect Password
    res = response_data(
        data=None,
        error_code=E017
    )

    return res


@args_check(ChangePasswordValidator())
@users.route("/v0/change_password/<string:token>", methods=["POST"])
def change_password(token):
    """Handles PATCH request"""

    json_data = JSONObject(request.json)

    with current_app.app_context():
        valid, user_id = User.decode_token(token.strip())
        if valid:
            user = User.query.get(user_id)
            if user:
                if user.password_is_valid(json_data.old_password):
                    new_password = json_data.new_password
                    access_token = user.generate_token()

                    user.set_password(new_password)
                    user.save()

                    res = (
                        response_data(
                            { "public_id" : user.public_id  }
                        )
                    )

                    return res
                else:
                    # E017 = Incorrect Password
                    res = response_data(
                        data=None,
                        error_code=E017
                    )

                    return res

        # E019 = Expired token
        res = response_data(
            data=None,
            error_code=E019
        )

        return res

    # E000 = Server Error
    res = response_data(
        data=None,
        error_code=E000
    )

    return res


class UserView(MethodView):

    def get(self, public_id):
        """Handles GET request"""

        with current_app.app_context():

            user = (
                User.query.filter_by(public_id=public_id)
                .first()
            )

            if user:
                res = (
                    response_data(
                        user.to_dict(flag=1)
                    )
                )

                return res

        # E009 = User Does Not Exist (404)
        res = response_data(
            data=None,
            error_code=E009
        )

        return res


    @args_check(UserValidator())
    @login_required()
    def put(self, current_user):
        """Handles PUT request"""

        current_user_id = current_user["id"]

        json_data = JSONObject(request.json)

        with current_app.app_context():
            user = User.query.get(current_user_id)

            if user:
                name        = json_data.name.lower().strip()
                description = json_data.description.strip()
                email       = json_data.email.lower().strip()

                images       = request.json.get("images", None)


                if email != user.email:
                    _user = User.query.filter_by(email=email).first()

                    if _user:
                        # E016 = Email Already Exists
                        res = response_data(
                            data=None,
                            error_code=E016
                        )

                        return res

                    # Update Email
                    user.email = email

                if name:
                    user.name = name

                if description:
                    user.description = description

                user.save()

                res = response_data(
                    data=user.to_dict()
                )

                return res

        # E009 = User Does Not Exist (404)
        res = response_data(
            data=None,
            error_code=E009
        )

        return res

    @login_required()
    def delete(self, current_user):
        """Handles DELETE request"""

        current_user_id = current_user["id"]

        with current_app.app_context():
            user = User.query.get(current_user_id)

            if user:
                user.deleted = True
                user.save()

                res = response_data(
                    data=None
                )

                return res

        # E009 = User Does Not Exist (404)
        res = response_data(
            data=None,
            error_code=E009
        )

        return res
