
from flask import Flask, render_template, jsonify
import aiohttp
import asyncio

app = Flask(__name__)

@app.route('/')
async def index():
    return render_template('index.html')

@app.route('/roster/<team_abbrev>')
async def get_roster(team_abbrev):
    roster_url = f'https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025'
    stats_url = 'https://api-web.nhle.com/v1/players/'

    async with aiohttp.ClientSession() as session:
        async with session.get(roster_url) as resp:
            if resp.status != 200:
                return jsonify({'error': 'Failed to fetch roster'}), 500
            data = await resp.json()

        players = []
        for category in ['forwards', 'defensemen', 'goalies']:
            for player in data.get(category, []):
                players.append({
                    'id': player['id'],
                    'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                    'number': player.get('sweaterNumber', 'N/A'),
                    'position': player.get('positionCode', 'N/A'),
                    'goals': 0,  # Will update from stats call
                    'assists': 0
                })

        # Fetch player stats
        async def fetch_stats(player_id):
            async with session.get(f'{stats_url}{player_id}/summary') as stat_resp:
                if stat_resp.status != 200:
                    return {'goals': 0, 'assists': 0}
                stats_data = await stat_resp.json()
                stats = stats_data.get('stats', {})
                return {
                    'goals': stats.get('goals', 0),
                    'assists': stats.get('assists', 0)
                }

        tasks = [fetch_stats(p['id']) for p in players]
        stats_results = await asyncio.gather(*tasks)

        # Update players with stats
        for p, s in zip(players, stats_results):
            p['goals'] = s['goals']
            p['assists'] = s['assists']

    return jsonify({'players': players})

if __name__ == '__main__':
    app.run(debug=True)
