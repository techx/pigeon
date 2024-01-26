from server import db
from flask import current_app as app, request, session, redirect
from apiflask import APIBlueprint, abort
from authlib.integrations.flask_client import OAuth

auth = APIBlueprint("auth", __name__, url_prefix="/auth", tag="Auth")

oauth = OAuth(app)
google = oauth.register(
    name="google",
    client_id=app.config["AUTH_CLIENT_ID"],
    client_secret=app.config["AUTH_CLIENT_SECRET"],
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "profile email"},
)


def auth_required_decorator(roles):
    """
    middleware for protected routes
    """

    def auth_required(func):
        def wrapper(*args, **kwargs):
            if not dict(session).get("user", 0):
                return abort(401)
            elif dict(session).get("user").get("role") not in roles:
                return abort(401)
            return func(*args, **kwargs)

        wrapper.__name__ = (
            func.__name__
        )  # avoid overwriting wrapper. something about scoping issues
        return wrapper

    return auth_required


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
        username == current_app.config["PIGEON_USERNAME"]
        and password == current_app.config["PIGEON_PASSWORD"]
    ):
        session["user"] = username
        return {"new_url": "/inbox"}
    message = "incorrect username or password"
    abort(400, message)


@auth.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return {"message": "Logged out successfully"}
