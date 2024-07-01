# app/__init__.py

from flask import Flask
from flask_pymongo import PyMongo
from flask_redis import FlaskRedis
from dotenv import load_dotenv
import os
from .celery import make_celery

mongo = PyMongo()
redis_client = FlaskRedis()

def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('app.config.Config')
    app.config.from_pyfile('config.py')

    mongo.init_app(app)
    redis_client.init_app(app)

    app.config.update(
        CELERY_BROKER_URL=os.environ.get('REDIS_URL'),
        CELERY_RESULT_BACKEND=os.environ.get('REDIS_URL')
    )

    celery = make_celery(app)

    with app.app_context():
        # Import and register the blueprint here
        from .routes import bp
        app.register_blueprint(bp)

    return app, celery
