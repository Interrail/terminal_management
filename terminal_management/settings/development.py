import dj_database_url
from .base import *


DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {"default": dj_database_url.config(default=os.getenv("DATABASE_URL"))}
