from flask import Flask, jsonify, render_template
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/teams')
def teams():
    standings_url = 'https://api-web.nhle.com/v1/standings/now'
    response = requests.get(standings_url)
    data = response.json()

    teams = []
    for team in data['standings']:
        teams.append({
            'name': team['teamName']['default'],
            'abbrev': team['teamAbbrev']['default'],
            'division': team['divisionName'],
            'logo': team['teamLogo']
        })
    return jsonify(teams)

@app.route('/roster/<team_abbrev>')
def roster(team_abbrev):
    roster_url = f'https://api-web.nhle.com/v1/roster/{team_abbrev}/current'
    response = requests.get(roster_url)
    data = response.json()

    players = []
    for player in data.get('forwards', []) + data.get('defensemen', []) + data.get('goalies', []):
        stats = player.get('seasonStats', {}).get('total', {})
        players.append({
            'name': player.get('firstName', {}).get('default', '') + ' ' + player.get('lastName', {}).get('default', ''),
            'position': player.get('position', ''),
            'sweaterNumber': player.get('sweaterNumber', ''),
            'goals': stats.get('goals', 0),
            'assists': stats.get('assists', 0)
        })
    return jsonify(players)

if __name__ == '__main__':
    app.run(debug=True)
