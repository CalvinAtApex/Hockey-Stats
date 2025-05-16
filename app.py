from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    standings_url = 'https://api-web.nhle.com/v1/standings/now'
    response = requests.get(standings_url)
    data = response.json()

    teams = []
    for record in data.get('standings', []):
        teams.append({
            'name': record['teamName']['default'],
            'abbreviation': record['teamAbbrev']['default']
        })

    return render_template('index.html', teams=teams)

@app.route('/roster/<team_abbrev>')
def get_roster(team_abbrev):
    roster_url = f'https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025'
    response = requests.get(roster_url)
    data = response.json()

    players = []
    for category in ['forwards', 'defensemen', 'goalies']:
        for player in data.get(category, []):
            players.append({
                'id': player['id'],
                'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                'number': player.get('sweaterNumber', 'N/A'),
                'position': player.get('positionCode', 'N/A'),
                'goals': 0,
                'assists': 0
            })

    return jsonify({'players': players})

if __name__ == '__main__':
    app.run(debug=True)