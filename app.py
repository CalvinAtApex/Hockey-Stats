from flask import Flask, jsonify, render_template, send_from_directory
import requests
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def teams():
    standings_url = 'https://api-web.nhle.com/v1/standings/now'
    response = requests.get(standings_url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch teams'}), 500

    standings_data = response.json()
    teams = []

    for team in standings_data.get('standings', []):
        team_info = {
            'name': team.get('teamName', {}).get('default', ''),
            'abbrev': team.get('teamAbbrev', {}).get('default', ''),
            'logo': team.get('teamLogo', '')
        }
        teams.append(team_info)

    return jsonify(teams)

@app.route('/roster/<team_abbrev>')
def roster(team_abbrev):
    roster_url = f'https://api-web.nhle.com/v1/roster/{team_abbrev}/current'
    response = requests.get(roster_url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch roster'}), 500

    roster_data = response.json()
    players = []

    for category in ['forwards', 'defensemen', 'goalies']:
        for player in roster_data.get(category, []):
            players.append({
                'name': f"{player.get('firstName', {}).get('default', '')} {player.get('lastName', {}).get('default', '')}",
                'position': player.get('positionCode', category[:-1].upper()),  # fallback to F/D/G
                'sweaterNumber': player.get('sweaterNumber', ''),
                'goals': player.get('stats', {}).get('goals', 0),
                'assists': player.get('stats', {}).get('assists', 0)
            })

    return jsonify(players)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
