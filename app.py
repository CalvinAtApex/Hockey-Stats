import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='templates')

# Home route: serve index.html
@app.route('/')
def index():
    return render_template('index.html')

# Return the teams grouped by division
@app.route('/teams')
def teams():
    resp = requests.get('https://api-web.nhle.com/v1/standings/now').json()
    divisions = {}
    for t in resp['standings']:
        div_name = t['divisionName']  # e.g. "Central", "Atlantic", etc.
        divisions.setdefault(div_name, []).append({
            'abbr': t['teamAbbrev']['default'],
            'name': t['teamCommonName']['default'],
            'logo': t['teamLogo']
        })
    return jsonify(divisions)

# Return roster + current‐season stats for a given team
@app.route('/roster/<team>')
def roster(team):
    # 1) fetch raw roster
    r = requests.get(f'https://api-web.nhle.com/v1/roster/{team}/current').json()
    players = r.get('forwards', []) + r.get('defensemen', []) + r.get('goalies', [])

    output = []
    for p in players:
        pid = p['id']
        # 2) fetch landing (to get featuredStats → regularSeason.subSeason)
        landing = requests.get(f'https://api-web.nhle.com/v1/player/{pid}/landing').json()
        stats = landing.get('featuredStats', {}) \
                       .get('regularSeason', {}) \
                       .get('subSeason', {})

        output.append({
            'number': p.get('sweaterNumber'),
            'name': f"{p['firstName']['default']} {p['lastName']['default']}",
            'headshot': p.get('headshot'),
            'pos': p.get('positionCode'),
            'gp': stats.get('gamesPlayed', 0),
            'g':  stats.get('goals', 0),
            'a':  stats.get('assists', 0),
            'p':  stats.get('points', 0)
        })

    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
