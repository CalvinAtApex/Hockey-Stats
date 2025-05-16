from flask import Flask, render_template, jsonify
import aiohttp
import asyncio

app = Flask(__name__)

TEAM_URL = "https://api-web.nhle.com/v1/standings/now"
ROSTER_URL_TEMPLATE = "https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025"
STATS_URL_TEMPLATE = "https://api-web.nhle.com/v1/player/{player_id}/landing"

async def fetch_json(session, url):
    async with session.get(url) as response:
        return await response.json()

@app.route('/')
async def index():
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, TEAM_URL)
        teams = [
            {
                'abbrev': t['teamAbbrev']['default'],
                'name': t['teamName']['default']
            }
            for t in data['standings']
        ]
    return render_template('index.html', teams=teams)

@app.route('/roster/<team_abbrev>')
async def get_roster(team_abbrev):
    async with aiohttp.ClientSession() as session:
        roster_data = await fetch_json(session, ROSTER_URL_TEMPLATE.format(team_abbrev=team_abbrev))

        players = []
        for category in ['forwards', 'defensemen', 'goalies']:
            for player in roster_data.get(category, []):
                player_id = player['id']
                stats_data = await fetch_json(session, STATS_URL_TEMPLATE.format(player_id=player_id))
                
                stats = stats_data.get('seasonTotals', [])
                goals = assists = 0
                if stats:
                    goals = stats[0].get('goals', 0)
                    assists = stats[0].get('assists', 0)

                players.append({
                    'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                    'number': player.get('sweaterNumber', 'N/A'),
                    'position': player.get('positionCode', 'N/A'),
                    'goals': goals,
                    'assists': assists
                })

    return jsonify(players)

if __name__ == '__main__':
    app.run(debug=True)
