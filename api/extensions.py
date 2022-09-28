from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer
import os
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flasgger import LazyString, Swagger
from flask import request
from flask_migrate import Migrate
from celery import Celery


cors = CORS()
db = SQLAlchemy()
ma = Marshmallow()
mail = Mail()
migrate = Migrate()
url_serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY', 'secret-key'))

def make_celery():
    """Create the celery extension."""
    backend = "redis://redis:6379"
    broker = "redis://redis:6379"
    celery = Celery(__name__, backend=backend, broker=broker)
    # celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
    # celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

    return celery


def init_celery(celery, app):
    """Initialize the celery extension."""
    celery.conf.update(app.config)

    TaskBase = celery.Task

    class ContextTask(TaskBase):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


celery = make_celery()

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Email Sending service.",
        "description": "An application for sending user registration and password reset emails.",
        "contact": {
            "responsibleOrganization": "",
            "responsibleDeveloper": "",
            "email": "lyceokoth@gmail.com",
            "url": "www.twitter.com/lylethedesigner",
        },
        "termsOfService": "www.twitter.com/deve",
        "version": "1.0"
    },
    "host": LazyString(lambda: request.host),
    "basePath": "/",  # base bash for blueprint registration
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "APIKeyHeader": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example:\"Authorization: Bearer {token}\""
        }
    },
}


swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger = Swagger(template=swagger_template,
                  config=swagger_config)