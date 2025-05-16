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
                'id': record['teamAbbrev']['default'],  # Use abbrev as ID
                'name': record['teamName']['default'],  # Team name
                'abbreviation': record['teamAbbrev']['default'],  # Abbrev for logos/keys
                'logo': record['teamLogo']  # Logo URL directly
            })
        return teams
    else:
        print(f"Failed to fetch teams: {response.status_code} - {response.text}")
    return []



def get_team_roster(abbrev):
    team_id = get_team_id(abbrev)
    if not team_id:
        return []
    url = f"https://api-web.nhle.com/v1/roster/{team_id}/current"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['forwards'] + data['defensemen'] + data['goalies']
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
