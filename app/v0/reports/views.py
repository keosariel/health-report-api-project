from flask import jsonify, request, current_app
from flask.views import MethodView

from app.models import Report

from app.helpers import (
    response_data,
    args_check,
    login_required,
    JSONObject
)

from app.errors import E000, E010, E011, E012, E013
from app.v0.reports.validators import ReportValidator


class ReportView(MethodView):

    def get(self, public_id):
        """Handles GET request"""
        
        with current_app.app_context():

            item = (
                Report.query.filter_by(public_id=public_id)
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

    @args_check(ReportValidator())
    @login_required()
    def post(self, current_user):
        """Handles POST request"""

        current_user_id = current_user["id"]

        json_data = JSONObject(request.json)

        with current_app.app_context():
            content = json_data.content.strip()

            item = Report(
                content=content,
                user_id=current_user_id,
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

    @args_check(ReportValidator())
    @login_required()
    def put(self, current_user, public_id):
        """Handles PUT request"""

        current_user_id = current_user["id"]

        json_data = JSONObject(request.json)

        with current_app.app_context():
            content = json_data.content.strip()

            item = Report.query.filter_by(public_id=public_id).first()

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

    


    


    