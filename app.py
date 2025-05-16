from flask import Flask, render_template, jsonify
import aiohttp
import asyncio

app = Flask(__name__)

TEAMS_URL = 'https://api-web.nhle.com/v1/teams'
ROSTER_URL_TEMPLATE = 'https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025'
STATS_URL_TEMPLATE = 'https://api-web.nhle.com/v1/player/{player_id}/landing'

async def fetch_json(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            return await response.json()
        return {}

@app.route('/')
async def index():
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, TEAMS_URL)
        teams = [
            {'abbrev': team['abbrev'], 'name': team['fullName']}
            for team in data.get('teams', [])
        ]
    return render_template('index.html', teams=teams)

@app.route('/roster/<team_abbrev>')
async def get_roster(team_abbrev):
    async with aiohttp.ClientSession() as session:
        roster_url = ROSTER_URL_TEMPLATE.format(team_abbrev=team_abbrev)
        roster_data = await fetch_json(session, roster_url)

        players = []
        for category in ['forwards', 'defensemen', 'goalies']:
            for player in roster_data.get(category, []):
                player_id = player['id']
                stats_url = STATS_URL_TEMPLATE.format(player_id=player_id)
                stats_data = await fetch_json(session, stats_url)

                # Find season totals for 20242025 or default to 0s
                season_totals = next(
                    (s for s in stats_data.get('seasonTotals', []) if s.get('seasonId') == 20242025),
                    {}
                )

                players.append({
                    'id': player_id,
                    'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                    'number': player.get('sweaterNumber', 'N/A'),
                    'position': player.get('positionCode', 'N/A'),
                    'goals': season_totals.get('goals', 0),
                    'assists': season_totals.get('assists', 0)
                })

    if not players:
        return jsonify({'error': 'No roster data found.'}), 404

    return jsonify(players)

if __name__ == '__main__':
    app.run(debug=True)
