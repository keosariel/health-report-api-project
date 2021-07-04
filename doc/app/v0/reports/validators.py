from flask_jsonvalidator import (
    JSONValidator,
    StringValidator
)

class ReportValidator(JSONValidator):
    validators = {
        "content" : StringValidator(nullable=False),
    }
    