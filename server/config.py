import os
from pathlib import Path
from dotenv import load_dotenv
from typing import cast

load_dotenv(os.path.dirname(__file__) / Path("../.env"))

OpenAIMessage = dict[str, str]
RedisDocument = dict[str, str]

ENV = os.environ.get("ENV", "development")


def _get_config_option(
    name: str, default_value: str | None = None, required: bool = False
) -> str | None:
    if ENV == "production":
        value = os.environ.get(name, None)
        if value is None:
            raise Exception(
                f"Environment variable {name} not set. In production, "
                "every environment variable must be set."
            )
    else:
        value = os.environ.get(name, default_value)

    if required and value is None:
        raise Exception(f"Environment variable {name} is required but not set.")

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
MAIL_USERNAME = cast(str, _get_config_option("MAIL_USERNAME", required=True))
MAIL_PASSWORD = cast(str, _get_config_option("MAIL_PASSWORD", required=True))
MAIL_CC = _get_config_option("MAIL_CC", required=True)

MAIL_SENDER_TAG = f'"Blueprint Team" <{MAIL_USERNAME}>'

AUTH_CLIENT_ID = _get_config_option("AUTH_CLIENT_ID", required=True)
AUTH_CLIENT_SECRET = _get_config_option("AUTH_CLIENT_SECRET", required=True)
SESSION_SECRET = _get_config_option("SESSION_SECRET", required=True)

OPENAI_API_KEY = _get_config_option("OPENAI_API_KEY", required=True)

AUTH_USERNAME = _get_config_option("AUTH_USERNAME", required=True)
AUTH_PASSWORD = _get_config_option("AUTH_PASSWORD", required=True)

AWS_REGION = _get_config_option("AWS_REGION", required=True)
AWS_ACCESS_KEY_ID = _get_config_option("AWS_ACCESS_KEY_ID", required=True)
AWS_SECRET_ACCESS_KEY = _get_config_option("AWS_SECRET_ACCESS_KEY", required=True)

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
