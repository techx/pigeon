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

from server.models.document import Document


# def init():
#     documents = Document.query.order_by(Document.id.desc()).all()

#     if len(documents) > 0:
#         return
#     # initialize with some default documents to create the index
#     document = Document(
#         "what is hackmit?",
#         "HackMIT is a weekend-long event where thousands of students from around the world come together to work on cool new software and/or hardware projects.",
#         "https://hackmit.org",
#         "what is hackmit?",
#     )
#     db.session.add(document)
#     document = Document(
#         "what is blueprint?",
#         "Blueprint is a weekend-long learnathon and hackathon for high school students hosted at MIT",
#         "https://blueprint.hackmit.org",
#         "what is blueprint?",
#     )
#     db.session.add(document)
#     db.session.commit()


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
        db.create_all()

        from server.controllers import api

        app.register_blueprint(api)

        from server.cli import seed

        app.register_blueprint(seed)

        # from server.controllers.admin import update_embeddings

        # on server start, embed some hard-coded documents and update index
        # this doesn't work for some reason
        # from server.controllers.admin import update_embeddings

        # init()
        # update_embeddings()

        @app.errorhandler(404)
        def _default(_error):
            if app.config["ENV"] == "production":
                return render_template("index.html"), 200
            else:
                return redirect(app.config["FRONTEND_URL"])

    return app
