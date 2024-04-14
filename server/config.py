"""Configuration for backend server."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(os.path.dirname(__file__) / Path("../.env"))

OpenAIMessage = dict[str, str]
RedisDocument = dict[str, str]

ENV = os.environ.get("ENV", "development")


def _get_config_option(name: str, default_value: str | None = None) -> str:
    if ENV == "production":
        value = os.environ.get(name, None)
        if value is None:
            raise Exception(
                f"Environment variable {name} not set. In production, "
                "every environment variable must be set."
            )
    else:
        value = os.environ.get(name, default_value)

    if value is None:
        raise Exception(f"Environment variable {name} not set.")

    return value


FRONTEND_URL = _get_config_option("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = _get_config_option("BACKEND_URL", "http://127.0.0.1:2010")
ALLOWED_DOMAINS = [FRONTEND_URL]
SQLALCHEMY_DATABASE_URI = _get_config_option(
    "DATABASE_URL", "postgresql://postgres:password@database/pigeondb"
)
REDIS_URL = _get_config_option("REDIS_URL", "redis")

FLASK_RUN_PORT = 2010
DEBUG = True
MAIL_USERNAME = _get_config_option("MAIL_USERNAME")
MAIL_PASSWORD = _get_config_option("MAIL_PASSWORD")
MAIL_CC = _get_config_option("MAIL_CC")

MAIL_SENDER_TAG = f'"Blueprint Team" <{MAIL_USERNAME}>'

AUTH_CLIENT_ID = _get_config_option("AUTH_CLIENT_ID")
AUTH_CLIENT_SECRET = _get_config_option("AUTH_CLIENT_SECRET")
SESSION_SECRET = _get_config_option("SESSION_SECRET")

OPENAI_API_KEY = _get_config_option("OPENAI_API_KEY")

AUTH_USERNAME = _get_config_option("AUTH_USERNAME")
AUTH_PASSWORD = _get_config_option("AUTH_PASSWORD")

AWS_REGION = _get_config_option("AWS_REGION")
AWS_ACCESS_KEY_ID = _get_config_option("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = _get_config_option("AWS_SECRET_ACCESS_KEY")

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
