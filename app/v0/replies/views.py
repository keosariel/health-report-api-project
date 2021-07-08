from flask import jsonify, request, current_app
from flask.views import MethodView

from app.models import Reply, Report, User

from app.helpers import (
    response_data,
    args_check,
    login_required,
    JSONObject
)

from app.errors import E000, E010, E011, E012, E013, E020
from app.v0.replies.validators import ReplyValidator, ReplyEditValidator


class ReplyView(MethodView):

    def get(self, public_id):
        """Handles GET request"""
        
        with current_app.app_context():

            item = (
                Reply.query.filter_by(public_id=public_id)
                .first()
            )

            if item:

                res = (
                    response_data(
                        item.to_dict()
                    )
                )

                return res
            
        # E012 = Item Does Not Exist (404)
        res = response_data(
            data=None, 
            error_code=E012
        )

        return res

    @args_check(ReplyValidator())
    @login_required()
    def post(self, current_user):
        """Handles POST request"""

        current_user_id = current_user["id"]

        json_data = JSONObject(request.json)

        with current_app.app_context():
            user = User.query.get(current_user_id)

            content = json_data.content.strip()
            report_public_id = json_data.report_public_id.strip()

            report_item = (
                Report.query.filter_by(public_id=report_public_id)
                .first()
            )

            if not report_item:
                # E012 = Item Does Not Exist (404)
                res = response_data(
                    data=None, 
                    error_code=E012,
                    description="Report Item with the `report_public_id` does not exists"
                )

                return res
            
            '''
            if not user.is_doctor:
                # E020 = User cannot reply to report (User is not a doctor)
                res = response_data(
                    data=None, 
                    error_code=E020
                )

                return res
            '''

            item = Reply(
                content=content,
                user_id=current_user_id,
                report_id=report_item.id
            ) 

            item.save()

            # Setting Public ID
            item.set_public_id()

            res = (
                response_data(
                    item.to_dict()
                )
            )

            return res

        # E000 = Server Error
        res = response_data(
            data=None, 
            error_code=E000
        )

        return res

    @args_check(ReplyEditValidator())
    @login_required()
    def put(self, current_user, public_id):
        """Handles PUT request"""

        current_user_id = current_user["id"]

        json_data = JSONObject(request.json)

        with current_app.app_context():
            content = json_data.content.strip()

            item = Reply.query.filter_by(public_id=public_id).first()

            if item:
                if item.user_id == current_user_id:
                    item.content = content

                    item.save()

                    res = (
                        response_data(
                            item.to_dict()
                        )
                    )

                    return res
                
                # E010 = User Cannot Edit Item
                res = response_data(
                    data=None, 
                    error_code=E010
                )

                return res

            # E012 = Item Does Not Exist (404)
            res = response_data(
                data=None, 
                error_code=E012
            )

            return res

        # E000 = Server Error
        res = response_data(
            data=None, 
            error_code=E000
        )

        return res

    @login_required()
    def delete(self, current_user, public_id):
        """Handles DELETE request"""

        current_user_id = current_user["id"]

        with current_app.app_context():
            item = Report.query.filter_by(public_id=public_id).first()

            if item:
                if item.user_id == current_user_id:
                    item.deleted = True
                    item.save()

                    res = response_data(
                        data=None
                    )

                    return res

                # E011 = User Cannot Delete Item
                res = response_data(
                    data=None, 
                    error_code=E011
                )

                return res

            # E012 = Item Does Not Exist (404)
            res = response_data(
                data=None, 
                error_code=E012
            )

            return res
        
        # E000 = Server Error
        res = response_data(
            data=None, 
            error_code=E000
        )

        return res

    


    


    
