from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# NHL Standings (for teams)
STANDINGS_URL = 'https://api-web.nhle.com/v1/standings/now'

# NHL Roster (per team)
ROSTER_URL_TEMPLATE = 'https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025'

@app.route('/')
def index():
    response = requests.get(STANDINGS_URL)
    data = response.json()

    teams = []
    for record in data.get('standings', []):
        team_data = {
            'name': record['teamName']['default'],
            'abbreviation': record['teamAbbrev']['default'],
            'logo': record['teamLogo']
        }
        teams.append(team_data)

    return render_template('index.html', teams=teams)

@app.route('/roster/<team_abbrev>')
def get_roster(team_abbrev):
    url = ROSTER_URL_TEMPLATE.format(team_abbrev=team_abbrev)
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': f'Failed to fetch roster for {team_abbrev}'}), 500

    data = response.json()

    players = []

    for category in ['forwards', 'defensemen', 'goalies']:
        for player in data.get(category, []):
            players.append({
                'id': player.get('id'),
                'name': f"{player.get('firstName', {}).get('default', '')} {player.get('lastName', {}).get('default', '')}",
                'position': player.get('positionCode', 'N/A'),
                'number': player.get('sweaterNumber', 'N/A'),
                'headshot': player.get('headshot', ''),
                'shootsCatches': player.get('shootsCatches', 'N/A'),
                'heightInches': player.get('heightInInches', 'N/A'),
                'weightPounds': player.get('weightInPounds', 'N/A'),
                'birthDate': player.get('birthDate', 'N/A'),
                'birthCity': player.get('birthCity', {}).get('default', ''),
                'birthCountry': player.get('birthCountry', 'N/A')
            })

    return jsonify({'players': players})

if __name__ == '__main__':
    app.run(debug=True)
