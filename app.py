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
app.config.update(
    SECURITY_PASSWORD_HASH='bcrypt',
    SECURITY_PASSWORD_SALT=os.getenv('SECURITY_PASSWORD_SALT', 'salty-secret'),
    SECURITY_REGISTERABLE=False,
    SECURITY_SEND_REGISTER_EMAIL=False,
    SECURITY_RECOVERABLE=False,
    SECURITY_CHANGEABLE=False,
)

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
    id            = db.Column(db.Integer, primary_key=True)
    email         = db.Column(db.String(255), unique=True, nullable=False)
    password      = db.Column(db.String(255), nullable=False)
    fs_uniquifier = db.Column(
                      db.String(255),
                      unique=True,
                      nullable=False,
                      default=lambda: str(uuid.uuid4())
                    )
    active        = db.Column(db.Boolean(), default=True)
    roles         = db.relationship('Role', secondary=roles_users,
                                    backref=db.backref('users', lazy='dynamic'))

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

def initialize_security():
    """Create DB tables and a default admin user/role if they don't exist."""
    db.create_all()

    # ensure the 'admin' role exists
    admin_role = user_datastore.find_role('admin') or user_datastore.create_role(
        name='admin',
        description='Site Administrator'
    )

    # ensure the default admin user exists
    admin_email = os.getenv('ADMIN_EMAIL', 'admin@example.com')
    admin_password = os.getenv('ADMIN_PASSWORD', 'password')
    if not user_datastore.find_user(email=admin_email):
        user_datastore.create_user(
            email=admin_email,
            password=hash_password(admin_password),
            roles=[admin_role]
        )

    db.session.commit()

# run it immediately on startup (no missing‐hook errors)
with app.app_context():
    initialize_security()

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
