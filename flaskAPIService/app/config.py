import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    REDIS_URL = os.getenv('REDIS_URL')
    HOST_PORT = os.getenv('HOST_PORT')
    BIND_IP = os.getenv('BIND_IP')
