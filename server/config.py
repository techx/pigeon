import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(os.path.dirname(__file__) / Path("../.env"))

OpenAIMessage = dict[str, str]
RedisDocument = dict[str, str]

ENV = os.environ.get("ENV", "development")

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:2010")
ALLOWED_DOMAINS = [FRONTEND_URL]
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:password@database/pigeondb"
)
REDIS_URL = os.environ.get("REDIS_URL", "redis")

FLASK_RUN_PORT = 2010
DEBUG = True
MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
MAIL_CC = os.environ.get("MAIL_CC")

MAIL_SENDER_TAG = f'"Blueprint Team" <{MAIL_USERNAME}>'

AUTH_CLIENT_ID = os.environ.get("AUTH_CLIENT_ID")
AUTH_CLIENT_SECRET = os.environ.get("AUTH_CLIENT_SECRET")
SESSION_SECRET = os.environ.get("SESSION_SECRET")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

AUTH_USERNAME = os.environ.get("AUTH_USERNAME")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD")

AWS_REGION = os.environ.get("AWS_REGION")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

AUTH_ADMINS = [
    {"name": "HackMIT", "email": "admin@hackmit.org"},
    {"name": "Andrew Liu", "email": "azliu@mit.edu"},
    {"name": "Richard Chen", "email": "richen@mit.edu"},
    {"name": "Annie Wang", "email": "anniewang2023@gmail.com"},
    {"name": "Eddie Qiao", "email": "eqiao@mit.edu"},
    {"name": "Albert Tam", "email": "altam@mit.edu"},
    {"name": "Kathryn Le", "email": "kle@mit.edu"},
    {"name": "Audrey Douglas", "email": "adouglas@mit.edu"},
    {"name": "Darren Yao", "email": "dyao@mit.edu"},
    {"name": "Jenny Yu", "email": "yujenny@mit.edu"},
    {"name": "Michael Zeng", "email": "michzeng@mit.edu"},
    {"name": "Anna Li", "email": "annawli@mit.edu"},
    {"name": "Claire Wang", "email": "clairely@mit.edu"},
    {"name": "Eddie Qiao", "email": "eqiao@mit.edu"},
    {"name": "Elaine Jiang", "email": "ejiang@mit.edu"},
    {"name": "Janet Guo", "email": "janetguo@mit.edu"},
    {"name": "Maggie Liu", "email": "magpie@mit.edu"},
    {"name": "Nathan Wang", "email": "nrwang@mit.edu"},
    {"name": "Claire Wang", "email": "clara32356@gmail.com"},
    {"name": "Claire Wang", "email": "sparrowsong325@gmail.com"},
]
