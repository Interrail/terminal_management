from .base import *
import dj_database_url


DEBUG = True

ALLOWED_HOSTS = ["*"]

DATABASES = {"default": dj_database_url.config(default=os.getenv("DATABASE_URL"))}

CDN_URL = os.getenv("CDN_URL")
CDN_ACCESS_KEY = os.getenv("CDN_ACCESS_KEY")
CDN_SECRET_KEY = os.getenv("CDN_SECRET_KEY")
MTT_BUCKET = os.getenv("MTT_BUCKET")
