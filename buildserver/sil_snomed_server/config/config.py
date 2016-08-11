import os
basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    MIGRATIONS_PATH = os.environ['MIGRATIONS_PATH']

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True