from flask import Flask
from application import routes
from .extensions import mongo
from .routes import main

def create_app(config_object='application.settings'):
    app = Flask(__name__)

    app.config.from_object(config_object)

    mongo.init_app(app)

    app.register_blueprint(main)

    return app