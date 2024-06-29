from flask import Flask
from flask_pymongo import PyMongo
from flask_redis import FlaskRedis
from dotenv import load_dotenv
import os

mongo = PyMongo()
redis_client = FlaskRedis()

def create_app():
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('app.config.Config')
    app.config.from_pyfile('config.py')

    mongo.init_app(app)
    redis_client.init_app(app)

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)

    return app
