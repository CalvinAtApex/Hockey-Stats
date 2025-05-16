import requests
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def teams():
    resp = requests.get('https://api-web.nhle.com/v1/standings/now').json()
    divisions = {}
    for t in resp['standings']:
        div_name = t['divisionName']
        divisions.setdefault(div_name, []).append({
            'abbr': t['teamAbbrev']['default'],
            'name': t['teamCommonName']['default'],
            'logo': t['teamLogo']
        })
    return jsonify(divisions)

@app.route('/roster/<team>')
def roster(team):
    r = requests.get(f'https://api-web.nhle.com/v1/roster/{team}/current').json()
    players = r.get('forwards', []) + r.get('defensemen', []) + r.get('goalies', [])

    output = []
    for p in players:
        pid = p['id']
        land = requests.get(f'https://api-web.nhle.com/v1/player/{pid}/landing').json()
        rs = land.get('featuredStats', {}) \
                 .get('regularSeason', {}) \
                 .get('subSeason', {})
        po = land.get('featuredStats', {}) \
                 .get('playoffs', {}) \
                 .get('subSeason', {})

        output.append({
            'number': p.get('sweaterNumber'),
            'name': f"{p['firstName']['default']} {p['lastName']['default']}",
            'headshot': p.get('headshot'),
            'pos': p.get('positionCode'),
            'gp': rs.get('gamesPlayed', 0),
            'g':  rs.get('goals', 0),
            'a':  rs.get('assists', 0),
            'p':  rs.get('points', 0),
            'playoffGoals':   po.get('goals', 0),
            'playoffAssists': po.get('assists', 0),
            'playoffPoints':  po.get('points', 0),
        })

    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
