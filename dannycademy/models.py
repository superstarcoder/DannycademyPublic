from datetime import datetime
from dannycademy import db, login_manager, app
from flask_login import UserMixin
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


# is authenticated, is active, is anonymous, get id

@login_manager.user_loader
def load_User(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    profile_description = db.Column(db.String(200), default="welcome to my profile!")

    role = db.Column(db.String(20), default="student")

    # saying that you have a relationship with Post
    # backref is like an attribute
    posts = db.relationship('Post', backref='author', lazy=True)
    courses = db.relationship('Course', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    # it is lowercase since all classes have a default lowercase name for the table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    thumbnail = db.Column(db.String(20), nullable=False, default='default.jpg')

    # it is lowercase since all classes have a default lowercase name for the table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    published = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', `{self.thumbnail}`)"


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.Text, default="edit course content here")
    course_id = db.Column(db.Integer, nullable=False)
    published = db.Column(db.Boolean, default=False)
    orderIndex = db.Column(db.Integer, default=1, nullable=False)


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    course_id = db.Column(db.Integer, nullable=False)
    published = db.Column(db.Boolean, default=False)
    orderIndex = db.Column(db.Integer, default=1, nullable=False)
    content = db.Column(db.Text, default="edit exercise content here")
    checker = db.Column(db.Text, default="#do 'import submission.[function name]'\n#to show result do 'result(testsPassed, totalTests)' for example:\nresult(10, 10)")