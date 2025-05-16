from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

# NHL Standings API
STANDINGS_URL = 'https://api-web.nhle.com/v1/standings/now'
# NHL Roster API Template
ROSTER_URL_TEMPLATE = 'https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025'

@app.route('/')
def index():
    response = requests.get(STANDINGS_URL)
    if response.status_code != 200:
        return "Failed to load standings", 500

    data = response.json()
    teams = []

    for record in data.get('standings', []):
        teams.append({
            'name': record['teamName']['default'],
            'abbreviation': record['teamAbbrev']['default'],
            'logo': record['teamLogo']
        })

    return render_template('index.html', teams=teams)

@app.route('/roster/<team_abbrev>')
def get_roster(team_abbrev):
    url = ROSTER_URL_TEMPLATE.format(team_abbrev=team_abbrev.upper())
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error fetching roster for {team_abbrev}: {response.status_code} - {response.text}")
        return jsonify({'players': []})  # Return empty list, not 500 error

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
