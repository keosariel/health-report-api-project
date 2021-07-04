from flask import Blueprint

replies = Blueprint("replies", __name__)

from app.v0.replies.views import ReplyView

replies_view = ReplyView.as_view('replies_view')

replies.add_url_rule("/v0/replies/<string:public_id>", view_func=replies_view, methods=["GET", "DELETE", "PUT"])
replies.add_url_rule("/v0/replies", view_func=replies_view, methods=["POST"])