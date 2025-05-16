from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, hash_password

app = Flask(__name__)
app.config.update(
    SECRET_KEY='…',
    SQLALCHEMY_DATABASE_URI='sqlite:///users.db',
    SECURITY_PASSWORD_SALT='…',
)

db = SQLAlchemy(app)

# -- your models (simplified) -----------------------------------
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)

class Role(db.Model):
    id          = db.Column(db.Integer(), primary_key=True)
    name        = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    email            = db.Column(db.String(255), unique=True)
    password         = db.Column(db.String(255))
    active           = db.Column(db.Boolean())
    fs_uniquifier    = db.Column(db.String(64), unique=True, nullable=False)
    roles            = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
# --------------------------------------------------------------

# Set up Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

@app.before_first_request
def create_admin_user():
    db.create_all()

    # 1) Create 'admin' role if missing
    if not user_datastore.find_role('admin'):
        user_datastore.create_role(name='admin', description='Administrator')

    # 2) Create the admin user if missing
    if not user_datastore.get_user('admin@example.com'):
        user_datastore.create_user(
            email='admin@example.com',
            password=hash_password('ChangeMe123!'),
            roles=['admin']
        )

    db.session.commit()

if __name__ == '__main__':
    app.run()
