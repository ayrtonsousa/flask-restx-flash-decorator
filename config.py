import os
from datetime import timedelta

from dotenv import load_dotenv


load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class ConfigBase:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('HOURS_TO_JWT_ACCESS_TOKEN_EXPIRES')))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('HOURS_TO_JWT_REFRESH_TOKEN_EXPIRES')))
    PROPAGATE_EXCEPTIONS = True
    RESTX_MASK_SWAGGER = False


class Config(ConfigBase):
    DEBUG = os.getenv('DEBUG').lower() == "true"
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    RATELIMIT_STORAGE_URI = os.getenv('RATELIMIT_STORAGE_URI')
    CACHE_TYPE = os.getenv('CACHE_TYPE')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS').split(',')


class ConfigTest(ConfigBase):
    DEBUG = True
    TESTING = True
    SECRET_KEY = "secret_key_to_test"
    SQLALCHEMY_DATABASE_URI =  'sqlite:///' + os.path.join(basedir, 'test.sqlite')
    JWT_SECRET_KEY = 'secret_key_to_jwt'
    RATELIMIT_STORAGE_URI = 'memory://'
    CACHE_TYPE = 'flask_caching.backends.SimpleCache'
    CORS_ORIGINS = '*'
    