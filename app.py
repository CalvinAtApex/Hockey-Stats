from flask import Flask, render_template, jsonify
import aiohttp
import asyncio

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

async def fetch_player_stats(session, player):
    url = f"https://api-web.nhle.com/v1/player/{player['id']}/summary"
    async with session.get(url) as resp:
        if resp.status != 200:
            print(f"Failed to fetch stats for player {player['id']}: {resp.status}")
            return {**player, 'goals': 0, 'assists': 0}
        data = await resp.json()
        stats = data.get('seasonTotals', [{}])[0].get('stat', {})
        return {
            **player,
            'goals': stats.get('goals', 0),
            'assists': stats.get('assists', 0)
        }

@app.route('/roster/<team_abbrev>')
async def get_roster(team_abbrev):
    url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/20242025"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return jsonify({'error': 'Failed to fetch roster'}), 500
            roster_data = await resp.json()

        players = []
        for group in ['forwards', 'defensemen', 'goalies']:
            for player in roster_data.get(group, []):
                players.append({
                    'id': player['id'],
                    'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                    'number': player.get('sweaterNumber', 'N/A'),
                    'position': player.get('positionCode', 'N/A')
                })

        tasks = [fetch_player_stats(session, player) for player in players]
        enriched_players = await asyncio.gather(*tasks)

    if not enriched_players:
        return jsonify({'error': 'No roster data found.'}), 404

    return jsonify({'players': enriched_players})

if __name__ == '__main__':
    app.run(debug=True)