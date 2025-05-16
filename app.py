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
            teams.append({
                'id': record['teamId'],
                'name': record['teamName'],
                'abbreviation': record['teamAbbrev'],
                'logo': record['teamLogo']
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
