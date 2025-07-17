from flask import Flask, render_template, jsonify, Response
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def teams():
    # Fetch the current standings/teams
    resp = requests.get('https://api-web.nhle.com/v1/standings/now')
    data = resp.json()
    standings = data.get('standings', [])

    # Group teams by division
    divisions = {}
    for t in standings:
        div = t['divisionName']
        divisions.setdefault(div, []).append({
            'abbrev': t['teamAbbrev']['default'],
            'name':   t['teamCommonName']['default'],
            'logo':   t['teamLogo']
        })

    return jsonify(divisions)

@app.route('/roster/<team_abbrev>')
def roster(team_abbrev):
    # 1) fetch the raw roster
    r = requests.get(f'https://api-web.nhle.com/v1/roster/{team_abbrev}/current')
    roster_json = r.json()
    players = []

    # 2) for each skater, fetch landing/stats and pluck
    for group in ('forwards', 'defensemen', 'goalies'):
        for p in roster_json.get(group, []):
            pid = p['id']
            summ = requests.get(f'https://api-web.nhle.com/v1/player/{pid}/landing').json()
            fs  = summ.get('featuredStats', {})
            rs  = fs.get('regularSeason', {}).get('subSeason', {})
            po  = fs.get('playoffs', {}).get('subSeason', {})

            players.append({
                'headshot':       p.get('headshot'),
                'name':           f"{p['firstName']['default']} {p['lastName']['default']}",
                'number':         p.get('sweaterNumber'),
                'position':       p.get('positionCode'),
                'gamesPlayed':    rs.get('gamesPlayed', 0),
                'goals':          rs.get('goals', 0),
                'assists':        rs.get('assists', 0),
                'points':         rs.get('points', 0),
                'playoffGames':   po.get('gamesPlayed', 0),
                'playoffGoals':   po.get('goals', 0),
                'playoffAssists': po.get('assists', 0),
                'playoffPoints':  po.get('points', 0),
            })

    # 3) look up the team’s logo
    std = requests.get('https://api-web.nhle.com/v1/standings/now').json().get('standings', [])
    logo = next((t['teamLogo'] for t in std if t['teamAbbrev']['default'] == team_abbrev), '')

    return jsonify({ 'logo': logo, 'players': players })

@app.route('/robots.txt')
def robots_txt():
    return Response("User-agent: *\nDisallow:\n", mimetype="text/plain")

if __name__ == '__main__':
    app.run(debug=True)
