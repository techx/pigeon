from flask import Blueprint
from server.controllers.emails import emails
from server.controllers.admin import admin
from server.controllers.faq import faq

api = Blueprint("api", __name__, url_prefix="/api")
api.register_blueprint(emails)
api.register_blueprint(admin)
api.register_blueprint(faq)
