from flask import Flask, render_template, request
import requests

app = Flask(__name__)

# Get list of NHL teams from standings API
def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    response = requests.get(url)
    teams = []
    if response.status_code == 200:
        data = response.json()
        for record in data.get('standings', []):
            teams.append({
                'abbrev': record.get('teamAbbrev', {}).get('default'),
                'name': record.get('teamName', {}).get('default'),
                'logo': record.get('teamLogo', '')
            })
    else:
        print(f"Failed to fetch teams: {response.status_code} - {response.text}")
    return teams

# Get roster for selected team
def get_team_roster(team_abbrev, season="20242025"):
    url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/{season}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        players = []
        
        # Combine forwards, defensemen, goalies
        player_groups = data.get('forwards', []) + data.get('defensemen', []) + data.get('goalies', [])
        
        for player in player_groups:
            players.append({
                'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                'position': player['positionCode'],
                'sweaterNumber': player.get('sweaterNumber', ''),
                'headshot': player.get('headshot', ''),
                'shootsCatches': player.get('shootsCatches', ''),
                'birthDate': player.get('birthDate', ''),
                'heightInches': player.get('heightInInches', ''),
                'weightPounds': player.get('weightInPounds', ''),
                'birthCity': player.get('birthCity', {}).get('default', ''),
                'birthCountry': player.get('birthCountry', '')
            })
        return players
    else:
        print(f"Failed to fetch roster for {team_abbrev}: {response.status_code} - {response.text}")
    return []

# Home page with team dropdown
@app.route('/')
def index():
    teams = get_teams()
    return render_template('index.html', teams=teams)

# Team roster page
@app.route('/team/<team_abbrev>')
def team_roster(team_abbrev):
    players = get_team_roster(team_abbrev)
    return render_template('roster.html', team=team_abbrev, players=players)

if __name__ == '__main__':
    app.run(debug=True)
