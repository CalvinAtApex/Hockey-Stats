from flask import Flask, jsonify, render_template, send_from_directory
import requests

app = Flask(__name__, static_folder='static', template_folder='.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def get_teams():
    standings_url = 'https://api-web.nhle.com/v1/standings/now'
    response = requests.get(standings_url)
    data = response.json()
    teams = []
    for team in data['standings']:
        teams.append({
            'abbreviation': team['teamAbbrev']['default'],
            'name': team['teamName']['default'],
            'logo': team['teamLogo']
        })
    return jsonify(teams)

@app.route('/roster/<team_abbr>')
def get_roster(team_abbr):
    roster_url = f'https://api-web.nhle.com/v1/roster/{team_abbr}/current'
    response = requests.get(roster_url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch roster'}), 500
    data = response.json()
    roster = data.get('forwards', []) + data.get('defensemen', []) + data.get('goalies', [])
    players = []
    for player in roster:
        players.append({
            'id': player['id'],
            'name': f"{player['firstName']['default']} {player['lastName']['default']}",
            'position': player['position'],
            'sweaterNumber': player.get('sweaterNumber', '')
        })
    return jsonify(players)

@app.route('/player/<int:player_id>')
def get_player_stats(player_id):
    player_url = f'https://api-web.nhle.com/v1/player/{player_id}/landing'
    response = requests.get(player_url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch player stats'}), 500
    data = response.json()
    stats = data.get('featuredStats', {}).get('regularSeason', {}).get('subSeason', {})
    player_info = {
        'gamesPlayed': stats.get('gamesPlayed', 0),
        'goals': stats.get('goals', 0),
        'assists': stats.get('assists', 0),
        'points': stats.get('points', 0)
    }
    return jsonify(player_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
