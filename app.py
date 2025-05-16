import os
import uuid
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required
from flask_security.utils import hash_password

app = Flask(__name__)

# ─── Configuration ───────────────────────────────────────────────────────────────
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Flask-Security configuration
app.config['SECURITY_PASSWORD_HASH'] = 'bcrypt'
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'salty-secret')
app.config['SECURITY_REGISTERABLE'] = False
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_RECOVERABLE'] = False
app.config['SECURITY_CHANGEABLE'] = False

# ─── Extensions ─────────────────────────────────────────────────────────────────
db = SQLAlchemy(app)

# Association table for roles ↔ users
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id'), primary_key=True),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'), primary_key=True),
)

class Role(db.Model, RoleMixin):
    id          = db.Column(db.Integer(), primary_key=True)
    name        = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    id              = db.Column(db.Integer, primary_key=True)
    email           = db.Column(db.String(255), unique=True, nullable=False)
    password        = db.Column(db.String(255), nullable=False)
    fs_uniquifier   = db.Column(
                        db.String(255),
                        unique=True,
                        nullable=False,
                        default=lambda: str(uuid.uuid4())
                     )
    active          = db.Column(db.Boolean(), default=True)
    roles           = db.relationship('Role', secondary=roles_users,
                                      backref=db.backref('users', lazy='dynamic'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# ─── One-time setup before first request ─────────────────────────────────────────
@app.before_first_request
def initialize_security():
    db.create_all()

    # Create 'admin' role if missing
    admin_role = user_datastore.find_role('admin')
    if not admin_role:
        admin_role = user_datastore.create_role(
            name='admin',
            description='Site Administrator'
        )

    # Create default admin user if missing
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'password')
    admin_user = user_datastore.find_user(email=admin_email)
    if not admin_user:
        user_datastore.create_user(
            email=admin_email,
            password=hash_password(admin_password),
            roles=[admin_role]
        )

    db.session.commit()

# ─── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/teams')
@login_required
def teams():
    # ... your existing logic to fetch and render teams ...
    return render_template('teams.html')

@app.route('/roster/<team_abbrev>')
@login_required
def roster(team_abbrev):
    # ... your existing logic to fetch and render a team's roster ...
    return jsonify({})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
