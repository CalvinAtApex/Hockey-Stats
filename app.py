from flask import Flask, render_template, jsonify, redirect
import requests

app = Flask(__name__)

@app.route('/')
def index():
    # redirect the root URL to your default team roster
    return redirect('/roster/WSH')

@app.route('/roster/<team>')
def roster(team):
    resp = requests.get(f'https://api-web.nhle.com/v1/roster/{team}/current')
    resp.raise_for_status()
    data = resp.json()

    players = data.get('forwards', []) \
            + data.get('defensemen', []) \
            + data.get('goalies', [])

    return render_template('index.html',
                           players=players,
                           teamAbbrev=team)


@app.route('/api/player_stats/<team>')
def player_stats(team):
    resp = requests.get(f'https://api-web.nhle.com/v1/roster/{team}/current')
    resp.raise_for_status()
    roster = resp.json()

    all_players = roster.get('forwards', []) \
                + roster.get('defensemen', []) \
                + roster.get('goalies', [])

    stats_map = {}
    for p in all_players:
        pid = p['id']
        landing = requests.get(f'https://api-web.nhle.com/v1/player/{pid}/landing')
        if landing.status_code != 200:
            continue
        fs = landing.json().get('featuredStats', {})

        regular = fs.get('regularSeason', {}).get('subSeason', {})
        playoffs = fs.get('playoffs', {}).get('subSeason', {})

        stats_map[pid] = {
            'regularSeason': {
                'gamesPlayed': regular.get('gamesPlayed', 0),
                'goals':       regular.get('goals', 0),
                'assists':     regular.get('assists', 0),
                'points':      regular.get('points', 0),
            },
            'playoffs': {
                'gamesPlayed': playoffs.get('gamesPlayed', 0),
                'goals':       playoffs.get('goals', 0),
                'assists':     playoffs.get('assists', 0),
                'points':      playoffs.get('points', 0),
            },
        }

    return jsonify(stats_map)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
