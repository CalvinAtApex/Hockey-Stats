from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # replace with a secure random key

# --- Flask-Login setup ---
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Simple in-memory user store; replace with DB in production
users = {
    'admin': generate_password_hash('password123')
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# --- Authentication routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        pw_hash = users.get(username)
        if pw_hash and check_password_hash(pw_hash, password):
            user = User(username)
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- NHL API integration routes ---

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/teams')
@login_required
def teams():
    resp = requests.get('https://api-web.nhle.com/v1/standings/regularSeason')
    data = resp.json()
    # process and render as before
    return render_template('teams.html', standings=data['standings'])

@app.route('/roster/<team_abbrev>')
@login_required
def roster(team_abbrev):
    resp = requests.get(f'https://api-web.nhle.com/v1/roster/{team_abbrev}/current')
    data = resp.json()
    return render_template('roster.html', roster=data)

if __name__ == '__main__':
    app.run(debug=True)
