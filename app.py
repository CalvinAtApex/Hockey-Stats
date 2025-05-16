from flask import Flask, jsonify, render_template
import aiohttp
import asyncio
from datetime import datetime

app = Flask(__name__)

BASE_URL = "https://api-web.nhle.com/v1"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/teams")
async def get_teams():
    url = f"{BASE_URL}/standings/now"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    teams = []
    for record in data.get("standings", []):
        team_data = record.get("team", {})
        teams.append({
            "id": team_data.get("id"),
            "abbrev": team_data.get("abbrev"),
            "name": team_data.get("fullName", {}).get("default")
        })

    return jsonify(teams)

@app.route("/roster/<team_abbrev>")
async def get_roster(team_abbrev):
    current_year = datetime.now().year
    season_id = f"{current_year}{current_year + 1}"

    url = f"{BASE_URL}/roster/{team_abbrev}/{season_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return jsonify({"error": "Failed to fetch roster"}), 500
            roster_data = await resp.json()

        players = []
        for group in ['forwards', 'defensemen', 'goalies']:
            for player in roster_data.get(group, []):
                goals, assists = await get_player_stats(session, player['id'])
                players.append({
                    'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                    'number': player.get('sweaterNumber', ''),
                    'position': player.get('positionCode', ''),
                    'goals': goals,
                    'assists': assists
                })

    if not players:
        return jsonify({"error": "No roster data found."}), 404

    return jsonify(players)

async def get_player_stats(session, player_id):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    async with session.get(url) as resp:
        if resp.status != 200:
            print(f"Failed to fetch stats for player {player_id}: {resp.status}")
            return 0, 0

        data = await resp.json()
        stats = data.get("featuredStats", {}).get("regularSeason", {}).get("subSeason", {})
        goals = stats.get("goals", 0)
        assists = stats.get("assists", 0)

        return goals, assists

if __name__ == "__main__":
    app.run(debug=True)
