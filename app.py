from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def get_teams():
    url = "https://statsapi.web.nhl.com/api/v1/teams"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('teams', [])
    return []

def get_team_players(team_id):
    url = f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}/roster"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('roster', [])
    return []

@app.route("/", methods=["GET", "POST"])
def index():
    teams = get_teams()
    players = []
    selected_team = None

    if request.method == "POST":
        selected_team = request.form.get("team")
        players = get_team_players(selected_team)

    return render_template("index.html", teams=teams, players=players, selected_team=selected_team)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
