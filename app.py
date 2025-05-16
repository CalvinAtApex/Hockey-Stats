from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teams')
def teams():
    # fetch current standings / teams
    resp = requests.get('https://api-web.nhle.com/v1/standings/now')
    standings = resp.json()['standings']
    # group by division
    divisions = {}
    for t in standings:
        div = t['divisionAbbrev']['default']
        divisions.setdefault(div, []).append({
            'abbrev': t['teamAbbrev']['default'],
            'name': t['teamCommonName']['default'],
            'logo': t['teamLogo']
        })
    return jsonify(divisions)

@app.route('/roster/<team_abbrev>')
def roster(team_abbrev):
    # 1) fetch the raw roster
    r = requests.get(f'https://api-web.nhle.com/v1/roster/{team_abbrev}/current')
    roster_json = r.json()
    players = []
    # 2) for each skater, fetch landing/stats and pluck current-season + playoff
    for group in ('forwards','defensemen','goalies'):
        for p in roster_json.get(group, []):
            pid = p['id']
            summ = requests.get(f'https://api-web.nhle.com/v1/player/{pid}/landing').json()
            fs = summ['featuredStats']
            rs = fs['regularSeason']['subSeason']
            po = fs['playoffs']['subSeason']
            players.append({
                'name': f"{p['firstName']['default']} {p['lastName']['default']}",
                'position': p['positionCode'],
                'gamesPlayed': rs['gamesPlayed'],
                'goals': rs['goals'],
                'assists': rs['assists'],
                'points': rs['points'],
                'playoffGoals': po['goals'],
                'playoffAssists': po['assists'],
                'playoffPoints': po['points'],
            })
    # 3) look up the team’s logo from the same standings feed
    std = requests.get('https://api-web.nhle.com/v1/standings/now').json()['standings']
    logo = next((t['teamLogo']
                 for t in std
                 if t['teamAbbrev']['default'] == team_abbrev), '')
    return jsonify({ 'logo': logo, 'players': players })

if __name__ == '__main__':
    app.run(debug=True)
