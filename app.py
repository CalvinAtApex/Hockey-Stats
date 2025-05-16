# app.py
from flask import Flask, render_template, jsonify
import requests

API_BASE = 'https://api-web.nhle.com/v1'

app = Flask(__name__,
            template_folder='templates',
            static_folder='static')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/teams')
def teams():
    resp = requests.get(f'{API_BASE}/standings/now')
    data = resp.json().get('standings', [])
    divisions = {}
    for t in data:
        # divisionAbbrev is a plain string in the API now
        div = t['divisionAbbrev']
        divisions.setdefault(div, []).append({
            'abbr': t['teamAbbrev']['default'],
            'name': t['teamCommonName']['default'],
            'logo': t['teamLogo']
        })
    return jsonify(divisions)


@app.route('/roster/<team_abbrev>')
def roster(team_abbrev):
    resp = requests.get(f'{API_BASE}/roster/{team_abbrev}/current')
    data = resp.json()
    players = []
    for grp in ('forwards', 'defensemen', 'goalies'):
        for p in data.get(grp, []):
            players.append({
                'id':       p['id'],
                'name':     f"{p['firstName']['default']} {p['lastName']['default']}",
                'number':   p.get('sweaterNumber'),
                'pos':      p.get('positionCode'),
                'headshot': p.get('headshot')
            })
    return jsonify(players)


@app.route('/player/<int:player_id>')
def player(player_id):
    resp = requests.get(f'{API_BASE}/player/{player_id}/landing')
    d = resp.json()

    fs = d.get('featuredStats', {})
    reg = fs.get('regularSeason', {}).get('subSeason', {})
    po  = fs.get('playoffs',      {}).get('subSeason', {})

    out = {
        'id':       player_id,
        'name':     f"{d['firstName']['default']} {d['lastName']['default']}",
        'team':     d.get('currentTeamAbbrev'),
        'position': d.get('position'),
        'headshot': d.get('headshot'),
        'regular': {
            'season':    fs.get('season'),
            'games':     reg.get('gamesPlayed'),
            'goals':     reg.get('goals'),
            'assists':   reg.get('assists'),
            'points':    reg.get('points'),
            'plusMinus': reg.get('plusMinus')
        },
        'playoffs': {
            'games':     po.get('gamesPlayed'),
            'goals':     po.get('goals'),
            'assists':   po.get('assists'),
            'points':    po.get('points'),
            'plusMinus': po.get('plusMinus')
        }
    }
    return jsonify(out)


if __name__ == '__main__':
    app.run(debug=True)
