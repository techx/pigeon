from apiflask import APIFlask
from flask_mail import Mail
from flask_cors import CORS

cors = CORS()
mail = Mail()

def create_app():
    app = APIFlask(__name__, docs_path="/api/docs", version="2", docs_ui="elements", title="Pigeon API", static_url_path='')

    app.config.from_pyfile("config.py")

    with app.app_context():
        cors.init_app(app, origins=app.config.get("ALLOWED_DOMAINS"), supports_credentials=True)
        mail.init_app(app)

    return app