from apiflask import APIFlask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

cors = CORS()
db = SQLAlchemy()


def create_app():
    app = APIFlask(
        __name__,
        docs_path="/api/docs",
        version="2",
        docs_ui="elements",
        title="Pigeon API",
        static_url_path="",
    )

    app.config.from_pyfile("config.py")

    with app.app_context():
        db.init_app(app)
        cors.init_app(
            app, origins=app.config.get("ALLOWED_DOMAINS"), supports_credentials=True
        )

        from server.controllers import api

        app.register_blueprint(api)
        db.create_all()

    return app
