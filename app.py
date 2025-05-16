from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# SportsRadar API setup
API_KEY = os.getenv('SPORTSRADAR_API_KEY')
BASE_URL = "https://api.sportradar.us/nhl/trial/v7/en"

def get_teams():
    url = f"{BASE_URL}/league/hierarchy.json?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        teams = []
        for conference in data['conferences']:
            for division in conference['divisions']:
                teams.extend(division['teams'])
        return teams
    return []

def get_team_players(team_id):
    url = f"{BASE_URL}/teams/{team_id}/profile.json?api_key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('players', [])
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
