from flask import Flask, render_template, redirect
import requests

app = Flask(__name__)

# load divisions once per request so your base.html can use them
@app.context_processor
def inject_divisions():
    resp = requests.get('https://api-web.nhle.com/v1/teams/current')
    resp.raise_for_status()
    teams = resp.json().get('teams', [])
    divisions = {}
    for t in teams:
        div = t.get('divisionAbbrev', 'Unknown')
        divisions.setdefault(div, []).append(t)
    return dict(divisions=divisions)

@app.route('/')
def home():
    # auto-redirect to Capitals by default
    return redirect('/roster/WSH')

@app.route('/teams')
def teams():
    # this page simply lists all divisions → teams
    return render_template('teams.html')

@app.route('/roster/<team_abbrev>')
def roster(team_abbrev):
    # 1) fetch the roster
    r = requests.get(f'https://api-web.nhle.com/v1/roster/{team_abbrev}/current')
    r.raise_for_status()
    data = r.json()
    players = []
    for grp in ('forwards','defensemen','goalies'):
        players.extend(data.get(grp, []))

    # 2) fetch team logo via one player's landing endpoint
    if players:
        pid = players[0]['id']
        l = requests.get(f'https://api-web.nhle.com/v1/player/{pid}/landing')
        l.raise_for_status()
        team_logo = l.json().get('teamLogo','')
    else:
        team_logo = ''

    return render_template('index.html',
        players=players,
        team_logo=team_logo,
        team_abbrev=team_abbrev
    )

if __name__ == '__main__':
    app.run(debug=True)
