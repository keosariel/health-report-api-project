from app import app, create_db
from app.helpers import get_http_exception_handler

# Override the HTTP exception handler.
app.handle_http_exception = get_http_exception_handler(app)

if __name__ == "__main__":
    with app.app_context():
        create_db()
    app.run(debug=True)