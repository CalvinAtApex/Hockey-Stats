from flask import Flask, render_template, jsonify
import requests
import asyncio
import aiohttp
from datetime import datetime

app = Flask(__name__)

def get_current_season_id():
    now = datetime.now()
    year = now.year
    if now.month >= 8:
        return f"{year}{year+1}"
    else:
        return f"{year-1}{year}"

async def fetch_json(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            print(f"Failed to fetch {url}: {response.status}")
            return {}
        return await response.json()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/teams")
async def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, url)
        if not data:
            return jsonify({"error": "Failed to fetch standings"}), 500

        teams = []
        for record in data.get('standings', []):
            team_info = {
                'id': record['teamAbbrev']['default'],
                'name': record['teamName']['default']
            }
            teams.append(team_info)

        return jsonify(teams)

@app.route("/roster/<team_id>")
async def get_roster(team_id):
    season_id = get_current_season_id()
    url = f"https://api-web.nhle.com/v1/roster/{team_id}/{season_id}"

    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, url)
        if not data:
            return jsonify({"error": "Failed to fetch roster"}), 500

        players = []
        for group in ['forwards', 'defensemen', 'goalies']:
            for player in data.get(group, []):
                goals, assists = await get_player_stats(session, player['id'])
                player_info = {
                    'name': f"{player['firstName']['default']} {player['lastName']['default']}",
                    'number': player.get('sweaterNumber', 'N/A'),
                    'position': player.get('positionCode', 'N/A'),
                    'goals': goals,
                    'assists': assists
                }
                players.append(player_info)

        return jsonify(players)

async def get_player_stats(session, player_id):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    data = await fetch_json(session, url)
    stats = data.get('seasonTotals', [])
    current_season_id = get_current_season_id()

    nhl_stats = next((s for s in stats if s.get('leagueAbbrev') == 'NHL' and s.get('season') == current_season_id), {})
    goals = nhl_stats.get('goals', 0)
    assists = nhl_stats.get('assists', 0)

    return goals, assists

if __name__ == "__main__":
    app.run(debug=True)
