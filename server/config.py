import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.dirname(__file__) / Path("../.env"))

OpenAIMessage = dict[str, str]
RedisDocument = dict[str, str]

ENV = os.environ.get("ENV", "development")

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:2003")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:2000")
ALLOWED_DOMAINS = [FRONTEND_URL]
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:password@postgresdb/pigeondb"
)

FLASK_RUN_PORT = 2000
DEBUG = True
MAIL_SERVER = "smtp.mailgun.org"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_DEBUG = False
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_MAX_EMAILS = 40

MAIL_SENDER_TAG = f'"HackMIT Team" <{MAIL_USERNAME}>'

AUTH_CLIENT_ID = os.environ.get("AUTH_CLIENT_ID")
AUTH_CLIENT_SECRET = os.environ.get("AUTH_CLIENT_SECRET")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

AUTH_USERNAME = os.environ.get("AUTH_USERNAME")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD")

AUTH_ADMINS = [
    {"name": "HackMIT", "email": "admin@hackmit.org"},
    {"name": "Andrew Liu", "email": "azliu@mit.edu"},
    {"name": "Richard Chen", "email": "richen@mit.edu"},
    {"name": "Annie Wang", "email": "anniewang2023@gmail.com"},
    {"name": "Eddie Qiao", "email": "eqiao@mit.edu"},
    {"name": "Albert Tam", "email": "altam@mit.edu"},
]
