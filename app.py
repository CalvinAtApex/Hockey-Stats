from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def get_teams():
    url = 'https://api-web.nhle.com/v1/standings/now'
    response = requests.get(url)
    data = response.json()

    teams = []
    for record in data.get('standings', []):
        team_info = {
            'abbrev': record['teamAbbrev']['default'],
            'name': record['teamName']['default']
        }
        teams.append(team_info)

    return jsonify({'teams': teams})

@app.route('/roster/<team_abbrev>')
def get_roster(team_abbrev):
    url = f'https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025'
    response = requests.get(url)
    data = response.json()

    players = []

    for group in ['forwards', 'defensemen', 'goalies']:
        for player in data.get(group, []):
            player_info = {
                'id': player['id'],
                'number': player.get('sweaterNumber', ''),
                'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                'position': player.get('positionCode', ''),
                'goals': 0,    # Placeholder
                'assists': 0   # Placeholder
            }
            players.append(player_info)

    return jsonify({'players': players})

if __name__ == '__main__':
    app.run(debug=True)
