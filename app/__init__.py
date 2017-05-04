from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import importlib

app = Flask(__name__)

app.config.from_object('config.default')
app.config.from_object("config.{0}".format(os.environ['APP_CONFIG_MODE']))

import cli # import after app defined

db = SQLAlchemy(app)
migrate = Migrate(app, db)

for f in [f for f in os.listdir(os.path.dirname(os.path.realpath(__file__)))]:
    if f.find("_blueprint") >= 0:
        p = f[0:-10] # _blueprint is 10 chars long
        app.logger.info("Registering blueprint {0} at {1}".format(f, p))

        default_config_name = "app.{0}.config.default".format(f)
        default_config_module = importlib.import_module(default_config_name)
        app.config.from_object(default_config_name)

        mode_config_name = "app.{0}.config.{1}".format(f, os.environ['APP_CONFIG_MODE'])
        mode_config_module = importlib.import_module(mode_config_name)
        app.config.from_object(mode_config_name)

        blueprint_module = importlib.import_module("app.{0}.controller".format(f))
        app.register_blueprint(blueprint_module.blueprint, url_prefix="/{0}".format(p))

        importlib.import_module("app.{0}.cli".format(f))
