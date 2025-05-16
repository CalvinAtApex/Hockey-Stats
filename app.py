from flask import Flask, render_template, jsonify, request
import aiohttp
import asyncio

app = Flask(__name__)

STANDINGS_URL = 'https://api-web.nhle.com/v1/standings/now'
ROSTER_URL_TEMPLATE = 'https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025'
STATS_URL_TEMPLATE = 'https://api-web.nhle.com/v1/player/{player_id}/landing'

async def fetch_json(session, url):
    async with session.get(url) as response:
        return await response.json()

@app.route('/')
async def index():
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, STANDINGS_URL)
        teams = [
            {
                'abbrev': t['teamAbbrev']['default'],
                'name': t['teamName']['default']
            }
            for t in data.get('standings', [])
        ]
    return render_template('index.html', teams=teams)

@app.route('/roster/<team_abbrev>')
async def get_roster(team_abbrev):
    async with aiohttp.ClientSession() as session:
        url = ROSTER_URL_TEMPLATE.format(team_abbrev=team_abbrev)
        roster_data = await fetch_json(session, url)

        players = []
        for category in ['forwards', 'defensemen', 'goalies']:
            for player in roster_data.get(category, []):
                player_id = player['id']
                stats_url = STATS_URL_TEMPLATE.format(player_id=player_id)
                stats_data = await fetch_json(session, stats_url)

                season_stats = stats_data.get('seasonTotals', [])
                stats = next((s for s in season_stats if s.get('seasonId') == 20242025), {})

                players.append({
                    'id': player_id,
                    'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                    'number': player.get('sweaterNumber', 'N/A'),
                    'position': player.get('positionCode', 'N/A'),
                    'goals': stats.get('goals', 0),
                    'assists': stats.get('assists', 0)
                })

    if not players:
        return jsonify({'error': 'No roster data found.'}), 404

    return jsonify(players)

if __name__ == '__main__':
    app.run(debug=True)
