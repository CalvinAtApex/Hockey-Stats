from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    UserMixin,
    current_user,
)
import requests

app = Flask(__name__)
app.secret_key = "your-secret-key"  # change this!

# ---- Flask-Login setup ----
login_manager = LoginManager(app)
login_manager.login_view = "login"

# very simple in-memory user store
users = {
    "admin": {"password": "password"},
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# ---- Authentication routes ----
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        user = users.get(u)
        if user and user["password"] == p:
            login_user(User(u))
            next_page = request.args.get("next") or url_for("index")
            return redirect(next_page)
        flash("Invalid username or password", "warning")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---- Main app routes ----
@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/teams")
@login_required
def teams():
    resp = requests.get("https://api-web.nhle.com/v1/standings/now")
    data = resp.json()["standings"]
    # Group by division
    divs = {}
    for t in data:
        div = t["divisionAbbrev"]
        divs.setdefault(div, []).append(t)
    return render_template("teams.html", divisions=divs)

@app.route("/roster/<abbr>")
@login_required
def roster(abbr):
    resp = requests.get(f"https://api-web.nhle.com/v1/roster/{abbr}/current")
    resp.raise_for_status()
    data = resp.json()
    players = data.get("forwards", []) + data.get("defensemen", []) + data.get("goalies", [])
    return render_template("roster.html", players=players, team=abbr)

if __name__ == "__main__":
    app.run(debug=True)
