from apiflask import APIFlask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import redirect, render_template

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
        static_folder="../client/dist",
        template_folder="../client/dist",
    )

    app.config.from_pyfile("config.py")

    with app.app_context():
        db.init_app(app)
        cors.init_app(
            app, origins=app.config.get("ALLOWED_DOMAINS"), supports_credentials=True
        )

        from server.controllers import api

        app.register_blueprint(api)

        from server.cli import seed

        app.register_blueprint(seed)

        db.create_all()

        @app.errorhandler(404)
        def _default(_error):
            if app.config["ENV"] == "production":
                return render_template("index.html"), 200
            else:
                return redirect(app.config["FRONTEND_URL"])

    return app
