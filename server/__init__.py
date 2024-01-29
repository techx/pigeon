from apiflask import APIFlask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# https://stackoverflow.com/questions/50626058/psycopg2-cant-adapt-type-numpy-int64
import numpy
from psycopg2.extensions import register_adapter, AsIs


def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)


def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)


register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)

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

    # https://stackoverflow.com/questions/52733540/flask-session-dont-persist-data
    app.config.update(
        SESSION_COOKIE_SAMESITE="None",
        SESSION_COOKIE_SECURE=True,
        SESSION_TYPE="filesystem",
    )

    with app.app_context():
        db.init_app(app)
        cors.init_app(
            app, origins=app.config.get("ALLOWED_DOMAINS"), supports_credentials=True
        )

        from server.controllers import api

        app.register_blueprint(api)
        db.create_all()

    return app
