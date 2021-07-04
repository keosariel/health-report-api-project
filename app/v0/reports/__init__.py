from flask import Blueprint

reports = Blueprint("reports", __name__)

from app.v0.reports.views import ReportView

report_view = ReportView.as_view('report_view')

reports.add_url_rule("/v0/reports/<string:public_id>", view_func=report_view, methods=["GET", "DELETE", "PUT"])
reports.add_url_rule("/v0/reports", view_func=report_view, methods=["POST"])