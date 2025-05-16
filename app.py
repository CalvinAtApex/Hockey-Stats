from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    response = requests.get(url)
    data = response.json()

    teams = []
    for record in data.get('standings', []):
        team = {
            'name': record['teamName']['default'],
            'abbreviation': record['teamAbbrev']['default']
        }
        teams.append(team)

    return teams

@app.route('/')
def index():
    teams = get_teams()
    return render_template('index.html', teams=teams)

@app.route('/roster/<team_abbrev>')
def get_roster(team_abbrev):
    roster_url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025"
    stats_url = f"https://api-web.nhle.com/v1/club-stats-season/{team_abbrev}/20242025"

    roster_response = requests.get(roster_url)
    stats_response = requests.get(stats_url)

    if roster_response.status_code != 200 or stats_response.status_code != 200:
        return jsonify({'players': []})

    roster_data = roster_response.json()
    stats_data = stats_response.json()

    stats_lookup = {}
    for player in stats_data.get('skaters', []) + stats_data.get('goalies', []):
        stats_lookup[player['playerId']] = {
            'goals': player.get('goals', 0),
            'assists': player.get('assists', 0)
        }

    players = []

    for category in ['forwards', 'defensemen', 'goalies']:
        for player in roster_data.get(category, []):
            player_id = player['id']
            player_stats = stats_lookup.get(player_id, {'goals': 0, 'assists': 0})

            players.append({
                'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                'number': player.get('sweaterNumber', 'N/A'),
                'position': player.get('positionCode', 'N/A'),
                'goals': player_stats['goals'],
                'assists': player_stats['assists']
            })

    return jsonify({'players': players})

if __name__ == '__main__':
    app.run(debug=True)
