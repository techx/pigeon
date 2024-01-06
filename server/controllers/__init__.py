from flask import Blueprint
from server.controllers.emails import emails
from server.controllers.admin import admin
from server.controllers.faq import faq
from server.controllers.auth import auth

api = Blueprint("api", __name__, url_prefix="/api")
api.register_blueprint(emails)
api.register_blueprint(admin)
api.register_blueprint(faq)
api.register_blueprint(auth)
