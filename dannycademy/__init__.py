from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import secrets
from flask_bcrypt import Bcrypt
from flask_login.login_manager import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///site.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
# message category is whats being used in bootstrap classes. for example, danger, or success categories
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

from dannycademy.users.users import users
from dannycademy.courses.courses import courses
from dannycademy.chapters.chapters import chapters
from dannycademy.main.main import main
from dannycademy.exercises.exercises import exercises

app.register_blueprint(users)
app.register_blueprint(courses)
app.register_blueprint(chapters)
app.register_blueprint(main)
app.register_blueprint(exercises)
