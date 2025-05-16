from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Get all teams from standings API
def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        teams = []
        for record in data['standings']:
            team_info = record['team']
            teams.append({
                'id': team_info['id'],
                'name': team_info['fullName'],
                'abbreviation': team_info['abbrev'],
                'logo': f"https://assets.nhle.com/logos/nhl/svg/{team_info['abbrev']}_light.svg"
            })
        return teams
    return []

# Get active players for a team
def get_team_players(team_id):
    url = f"https://api-web.nhle.com/v1/roster/{team_id}/current"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get('forwards', []) + data.get('defensemen', []) + data.get('goalies', [])
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
