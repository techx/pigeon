from server import db
from flask import current_app as app, request, session, redirect, url_for
from apiflask import APIBlueprint, abort
from authlib.integrations.flask_client import OAuth

auth = APIBlueprint("auth", __name__, url_prefix="/auth", tag="Auth")

app.secret_key = app.config["SESSION_SECRET"]

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


@auth.route("/whoami")
def whoami():
    """GET /whoami
    Returns user if they are logged in, otherwise returns nothing.
    """
    if dict(session).get("user", 0):
        return session["user"]
    return {}


@auth.route("/login")
def login():
    """GET /login
    launches google authentication.
    """
    google = oauth.create_client("google")
    redirect_uri = url_for("api.auth.authorize", _external=True)
    if app.config["ENV"] == "development":
        # docker url is backend:2000, but google auth requires a public url
        redirect_uri = "http://localhost:2000/api/auth/authorize"
    return google.authorize_redirect(redirect_uri)


@auth.route("/authorize")
def authorize():
    """GET /authorize
    callback function after google authentication. verifies user token, then returns user data if it is in the database.
    """
    google = oauth.create_client("google")
    token = google.authorize_access_token()
    user_info = oauth.google.userinfo(token=token)
    for admin in app.config["AUTH_ADMINS"]:
        if admin["email"] == user_info["email"] and admin["name"] == user_info["name"]:
            session["user"] = {"role": "Admin"}
            return redirect(app.config["FRONTEND_URL"] + "/inbox")
    return redirect(app.config["FRONTEND_URL"] + "/restricted")


@auth.post("/login_admin")
@auth.doc(tags=["Auth"])
def login_admin():
    """POST /login_admin
    log in with admin credentials
    """
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    if (username == app.config["AUTH_USERNAME"]) and (
        password == app.config["AUTH_PASSWORD"]
    ):
        session["user"] = {"role": "Admin"}
        return {}
    message = "incorrect username or password"
    abort(400, message)


@auth.post("/logout")
def logout():
    """POST /logout
    clears current user session
    """
    session.clear()
    return redirect(app.config["FRONTEND_URL"])
