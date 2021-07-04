from flask import Flask, url_for
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_caching import Cache

# from flask_migrate import Migrate, MigrateCommand
# from flask_script import Manager

import json

app = Flask(__name__)

app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
# migrate = Migrate(app)
cache = Cache(app)

# manager = Manager(app)
# manager.add_command("db", MigrateCommand)

from app.v0 import users
from app.v0 import auth
from app.v0 import reports
from app.v0 import replies

app.register_blueprint(auth)
app.register_blueprint(users)
app.register_blueprint(reports)
app.register_blueprint(replies)

def create_db():
    db.create_all()
