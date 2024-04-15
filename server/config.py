"""Configuration for backend server."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(os.path.dirname(__file__) / Path("../.env"))

OpenAIMessage = dict[str, str]
RedisDocument = dict[str, str]

ENV = os.environ.get("ENV", "development")
LOCAL: bool = os.environ.get("LOCAL", False) == "True"

if not LOCAL:
    print("\033[91mWarning! you are missing the LOCAL environment variable.\033[0m")
    print("\033[91mThis will cause issues when running tests locally.\033[0m")
    print(
        "\033[91mThis is only acceptable in environments outside of "
        "production/development, e.g., running tests with github actions.\033[0m"
    )
    print("\033[91mMake sure you know what you are doing!\033[0m")
else:
    print("\033[92mLocal environment detected.\033[0m")


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
REDIS_HOST = _get_config_option("REDIS_HOST", "redis")

FLASK_RUN_PORT = 2010
DEBUG = True
MAIL_USERNAME = _get_config_option("MAIL_USERNAME", "test_mail_username")
MAIL_PASSWORD = _get_config_option("MAIL_PASSWORD", "test_mail_password")
MAIL_CC = _get_config_option("MAIL_CC", "test_mail_cc")

MAIL_SENDER_TAG = f'"Blueprint Team" <{MAIL_USERNAME}>'

AUTH_CLIENT_ID = _get_config_option("AUTH_CLIENT_ID", "test_auth_client_id")
AUTH_CLIENT_SECRET = _get_config_option("AUTH_CLIENT_SECRET", "test_auth_client_secret")
SESSION_SECRET = _get_config_option("SESSION_SECRET", "test_session_secret")

OPENAI_API_KEY = _get_config_option("OPENAI_API_KEY", "test_openai_api_key")

AUTH_USERNAME = _get_config_option("AUTH_USERNAME", "test_auth_username")
AUTH_PASSWORD = _get_config_option("AUTH_PASSWORD", "test_auth_password")

AWS_REGION = _get_config_option("AWS_REGION", "test_aws_region")
AWS_ACCESS_KEY_ID = _get_config_option("AWS_ACCESS_KEY_ID", "test_aws_access_key_id")
AWS_SECRET_ACCESS_KEY = _get_config_option(
    "AWS_SECRET_ACCESS_KEY", "test_aws_secret_access_key"
)

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
