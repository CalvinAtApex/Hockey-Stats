from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    response = requests.get(url)
    data = response.json()

    teams = []
    for record in data.get('standings', []):
        teams.append({
            'name': record['teamName']['default'],
            'abbreviation': record['teamAbbrev']['default']
        })

    return teams

@app.route('/')
def index():
    teams = get_teams()
    return render_template('index.html', teams=teams)

@app.route('/roster/<team_abbrev>')
def get_roster(team_abbrev):
    roster_url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025"

    roster_response = requests.get(roster_url)
    if roster_response.status_code != 200:
        return jsonify({'players': []})

    roster_data = roster_response.json()
    players = []

    for category in ['forwards', 'defensemen', 'goalies']:
        for player in roster_data.get(category, []):
            players.append({
                'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                'number': player.get('sweaterNumber', 'N/A'),
                'position': player.get('positionCode', 'N/A'),
                'goals': 0,   # Placeholder (no bulk stats endpoint works reliably)
                'assists': 0  # Placeholder
            })

    return jsonify({'players': players})

if __name__ == '__main__':
    app.run(debug=True)
