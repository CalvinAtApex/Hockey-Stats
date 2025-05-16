from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Static map of team abbreviations to numeric IDs
TEAM_ID_MAP = {
    "ANA": 24, "ARI": 53, "BOS": 6, "BUF": 7, "CGY": 20, "CAR": 12, "CHI": 16,
    "COL": 21, "CBJ": 29, "DAL": 25, "DET": 17, "EDM": 22, "FLA": 13, "LAK": 26,
    "MIN": 30, "MTL": 8, "NSH": 18, "NJD": 1, "NYI": 2, "NYR": 3, "OTT": 9,
    "PHI": 4, "PIT": 5, "SJS": 28, "SEA": 55, "STL": 19, "TBL": 14, "TOR": 10,
    "VAN": 23, "VGK": 54, "WSH": 15, "WPG": 52, "UTA": 56
}

def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        teams = []
        for record in data['standings']:
            teams.append({
                'id': record['teamAbbrev']['default'],  # Using abbrev as selection ID
                'name': record['teamName']['default'],
                'abbreviation': record['teamAbbrev']['default'],
                'logo': record['teamLogo'],
                'points': record['points'],
                'wins': record['wins'],
                'losses': record['losses'],
                'otLosses': record['otLosses'],
                'place': record['placeName']['default']
            })
        return teams
    else:
        print(f"Failed to fetch standings: {response.status_code} - {response.text}")
    return []

def get_team_roster(team_abbrev):
    team_id = TEAM_ID_MAP.get(team_abbrev)
    if not team_id:
        print(f"Unknown team abbreviation: {team_abbrev}")
        return []

    url = f"https://api-web.nhle.com/v1/roster/{team_id}/current"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        players = []
        for group in ['forwards', 'defensemen', 'goalies']:
            for player in data.get(group, []):
                players.append({
                    'name': player['fullName'],
                    'position': player['position'],
                    'sweaterNumber': player['sweaterNumber']
                })
        return players
    else:
        print(f"Failed to fetch roster for {team_abbrev}: {response.status_code} - {response.text}")
    return []

@app.route("/", methods=["GET", "POST"])
def index():
    teams = get_teams()
    players = []
    selected_team = None

    if request.method == "POST":
        selected_team = request.form.get("team")
        if selected_team:
            players = get_team_roster(selected_team)

    return render_template("index.html", teams=teams, players=players, selected_team=selected_team)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
