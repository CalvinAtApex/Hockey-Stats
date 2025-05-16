from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def teams():
    standings_url = 'https://api-web.nhle.com/v1/standings/now'
    standings_data = requests.get(standings_url).json()
    teams = []

    for team_data in standings_data.get('standings', []):
        team = {
            'name': team_data['teamName']['default'],
            'abbrev': team_data['teamAbbrev']['default'],
            'division': team_data['divisionName'],
            'logo': team_data['teamLogo']
        }
        teams.append(team)

    return jsonify(teams)

@app.route('/roster/<team_abbrev>')
def roster(team_abbrev):
    roster_url = f'https://api-web.nhle.com/v1/roster/{team_abbrev}/current'
    roster_data = requests.get(roster_url).json()

    players = []
    for player in roster_data.get('forwards', []) + roster_data.get('defensemen', []) + roster_data.get('goalies', []):
        player_id = player.get('id')
        player_name = player.get('firstName', {}).get('default', '') + ' ' + player.get('lastName', {}).get('default', '')
        sweater_number = player.get('sweaterNumber', '')
        position = player.get('position', '')

        stats_url = f'https://api-web.nhle.com/v1/player/{player_id}/landing'
        stats_data = requests.get(stats_url).json()

        goals = assists = 0
        try:
            regular_stats = stats_data['player']['currentTeamStats']['regularSeason']['subSeason']
            goals = regular_stats.get('goals', 0)
            assists = regular_stats.get('assists', 0)
        except (KeyError, TypeError):
            pass

        players.append({
            'id': player_id,
            'name': player_name,
            'sweaterNumber': sweater_number,
            'position': position,
            'goals': goals,
            'assists': assists
        })

    return jsonify(players)

if __name__ == '__main__':
    app.run(debug=True)
