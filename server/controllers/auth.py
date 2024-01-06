from server import db
from flask import current_app, request, session, redirect
from apiflask import APIBlueprint, abort

auth = APIBlueprint("auth", __name__, url_prefix="/auth", tag="Auth")

current_app.secret_key = current_app.config["SECRET_KEY"]

@auth.route("/whoami", methods=["GET"])
def whoami():
    is_authenticated = "user" in session
    return {"auth": is_authenticated}

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    if (
        username == current_app.config["PIGEON_USERNAME"] and
        password == current_app.config["PIGEON_PASSWORD"]
    ):
        session["user"] = username
        return {"new_url": "/inbox"}
    message = "incorrect username or password"
    abort(400, message)

@auth.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return {"message": "Logged out successfully"}

