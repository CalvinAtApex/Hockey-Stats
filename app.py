from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

@app.route('/')
def index():
    standings_url = "https://api-web.nhle.com/v1/standings/now"
    response = requests.get(standings_url)
    standings_data = response.json()
    
    teams = []
    for record in standings_data.get('standings', []):
        team_info = {
            'abbreviation': record['teamAbbrev']['default'],
            'name': record['teamName']['default'],
            'logo': record['teamLogo']
        }
        teams.append(team_info)

    return render_template('index.html', teams=teams)

@app.route('/roster/<team_abbrev>')
def get_roster(team_abbrev):
    season = '20242025'  # Adjust if dynamic season is needed
    roster_url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/{season}"
    response = requests.get(roster_url)

    if response.status_code != 200:
        return jsonify({'error': f'Failed to fetch roster for {team_abbrev}'}), 404

    roster_data = response.json()
    players = []

    for category in ['forwards', 'defensemen', 'goalies']:
        for player in roster_data.get(category, []):
            players.append({
                'id': player['id'],
                'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                'position': player['positionCode'],
                'number': player['sweaterNumber'],
                'shootsCatches': player['shootsCatches'],
                'height': f"{player['heightInInches']} in / {player['heightInCentimeters']} cm",
                'weight': f"{player['weightInPounds']} lbs / {player['weightInKilograms']} kg",
                'birthDate': player['birthDate'],
                'birthPlace': f"{player['birthCity']['default']}, {player.get('birthStateProvince', {}).get('default', '')} {player['birthCountry']}",
                'headshot': player['headshot']
            })

    return jsonify(players)

if __name__ == "__main__":
    app.run(debug=True)
