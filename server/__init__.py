"""Initialize the Flask app."""

from typing import Type, cast

import numpy
from apiflask import APIFlask
from flask import redirect, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from psycopg2.extensions import AsIs, register_adapter
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


def addapt_numpy_float64(numpy_float64):
    """Adapt numpy.float64 to SQL syntax.

    See here:
    https://stackoverflow.com/questions/50626058/psycopg2-cant-adapt-type-numpy-int64
    """
    return AsIs(numpy_float64)


def addapt_numpy_int64(numpy_int64):
    """Adapt numpy.int64 to SQL syntax.

    See here:
    https://stackoverflow.com/questions/50626058/psycopg2-cant-adapt-type-numpy-int64
    """
    return AsIs(numpy_int64)


register_adapter(numpy.float64, addapt_numpy_float64)
register_adapter(numpy.int64, addapt_numpy_int64)

cors = CORS()


class Base(DeclarativeBase, MappedAsDataclass):
    """Base SQLAlchemy class. Don't use this class; use db.Model instead.

    Since we use Flask SQLAlchemy, this class shouldn't be used directly.
    Instead, use db.Model.
    """

    pass


class ProperlyTypedSQLAlchemy(SQLAlchemy):
    """Temporary type hinting workaround for Flask SQLAlchemy.

    This is a temporary workaround for the following issue:
    https://github.com/pallets-eco/flask-sqlalchemy/issues/1312
    This workaround may not be correct.
    """

    Model: Type[Base]


db = SQLAlchemy(model_class=Base)
db = cast(ProperlyTypedSQLAlchemy, db)


def create_app():
    """Create the Flask app."""
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

        allowed_domains = app.config.get("ALLOWED_DOMAINS")

        cors.init_app(
            app,
            origins=cast(list[str], allowed_domains),
            supports_credentials=True,
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
