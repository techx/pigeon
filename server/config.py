import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.dirname(__file__) / Path('../.env'))

OpenAIMessage = dict[str, str]
RedisDocument = dict[str, str]

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:2003")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:2000")
ALLOWED_DOMAINS = [FRONTEND_URL]
SQLALCHEMY_DATABASE_URI = "postgresql://localhost/pigeon"

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

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")