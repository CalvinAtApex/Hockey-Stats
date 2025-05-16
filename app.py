from flask import Flask, render_template, request
import requests

app = Flask(__name__)

def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        teams = []
        for record in data['standings']:
            teams.append({
                'uuid': record['teamUuid'],
                'abbreviation': record['teamAbbrev'],
                'name': record['teamName'],
                'logo': record['teamLogo']
            })
        return teams
    else:
        print(f"Failed to fetch teams: {response.status_code} - {response.text}")
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
