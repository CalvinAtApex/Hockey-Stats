from flask import Flask, jsonify, render_template, send_from_directory
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def teams():
    standings_url = 'https://api-web.nhle.com/v1/standings/now'
    response = requests.get(standings_url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch standings'}), 500

    standings_data = response.json()
    teams = []
    for team_data in standings_data['standings']:
        team_info = {
            'abbrev': team_data['teamAbbrev']['default'],
            'name': team_data['teamName']['default'],
            'logo': team_data['teamLogo']
        }
        teams.append(team_info)

    return jsonify(teams)

@app.route('/roster/<team_abbrev>')
def roster(team_abbrev):
    roster_url = f'https://api-web.nhle.com/v1/roster/{team_abbrev}/current'
    response = requests.get(roster_url)
    if response.status_code != 200:
        return jsonify({'error': f'Failed to fetch roster for {team_abbrev}'}), 500

    roster_data = response.json()
    players = []
    for player in roster_data['forwards'] + roster_data['defensemen'] + roster_data['goalies']:
        players.append({
            'name': player['firstName']['default'] + ' ' + player['lastName']['default'],
            'position': player['position'],
            'sweaterNumber': player.get('sweaterNumber', ''),
            'goals': player.get('stats', {}).get('goals', 0),
            'assists': player.get('stats', {}).get('assists', 0)
        })

    return jsonify(players)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
