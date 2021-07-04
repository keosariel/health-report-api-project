from flask_jsonvalidator import (
    JSONValidator,
    StringValidator
)

class ReplyValidator(JSONValidator):
    validators = {
        "content" : StringValidator(nullable=False),
        "report_public_id" : StringValidator(nullable=False),
    }
    
class ReplyEditValidator(JSONValidator):
    validators = {
        "content" : StringValidator(nullable=False)
    }
    
