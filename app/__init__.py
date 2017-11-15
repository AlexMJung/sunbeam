from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
import importlib

app = Flask(__name__)

app.config.from_object('config.default')
app.config.from_object("config.{0}".format(os.environ.get('APP_CONFIG_MODE', None)))

@app.route("/")
def index():
    return "Ok"

import cli # import after app defined

db = SQLAlchemy(app)
migrate = Migrate(app, db)

blueprints = [];

for f in [f for f in os.listdir(os.path.dirname(os.path.realpath(__file__)))]:
    if f.find("_blueprint") >= 0:

        p = f[0:-10] # _blueprint is 10 chars long

        default_config_name = "app.{0}.config.default".format(f)
        default_config_module = importlib.import_module(default_config_name)
        app.config.from_object(default_config_name)

        mode_config_name = "app.{0}.config.{1}".format(f, os.environ.get('APP_CONFIG_MODE', None))
        mode_config_module = importlib.import_module(mode_config_name)
        app.config.from_object(mode_config_name)

        blueprints.append((f, p));

# register blueprints and cli after all config, so that blueprints that
# reference others won't be missing config references

for (f, p) in blueprints:
    app.logger.info("Registering blueprint {0} at {1}".format(f, p))
    blueprint_module = importlib.import_module("app.{0}.controller".format(f))
    app.register_blueprint(blueprint_module.blueprint, url_prefix="/{0}".format(p))
    importlib.import_module("app.{0}.cli".format(f))
