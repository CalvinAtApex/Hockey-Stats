from flask import Flask, jsonify, render_template
import requests
import asyncio
import aiohttp
from datetime import datetime

app = Flask(__name__)

NHLE_BASE_URL = "https://api-web.nhle.com/v1"

def get_current_season():
    now = datetime.now()
    year = now.year if now.month >= 9 else now.year - 1
    return f"{year}{year+1}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/teams")
def get_teams():
    url = f"{NHLE_BASE_URL}/standings/now"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

    teams = []
    for record in data.get("standings", []):
        team = record.get("team", {})
        teams.append({
            "id": team.get("id"),
            "teamAbbrev": team.get("abbrev"),
            "teamName": team.get("name", {}),
            "fullTeamName": team.get("fullName", {})
        })

    return jsonify(teams)

@app.route("/roster/<team_abbrev>")
async def get_roster(team_abbrev):
    season = get_current_season()
    url = f"{NHLE_BASE_URL}/roster/{team_abbrev}/{season}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return jsonify({"error": f"Failed to fetch roster for {team_abbrev}"}), 500
            roster_data = await resp.json()

        players = []
        for category in ["forwards", "defensemen", "goalies"]:
            for player in roster_data.get(category, []):
                goals, assists = await get_player_stats(session, player["id"], season)
                players.append({
                    "number": player.get("sweaterNumber", ""),
                    "name": f"{player['firstName']['default']} {player['lastName']['default']}",
                    "position": player.get("positionCode", ""),
                    "goals": goals,
                    "assists": assists
                })

    return jsonify(players)

async def get_player_stats(session, player_id, season):
    url = f"{NHLE_BASE_URL}/player/{player_id}/landing"
    async with session.get(url) as resp:
        if resp.status != 200:
            return 0, 0
        data = await resp.json()

    featured = data.get("featuredStats", {})
    regular = featured.get("regularSeason", {}).get("subSeason", {})
    stats_season = featured.get("season")

    if stats_season != int(season):
        return 0, 0

    goals = regular.get("goals", 0)
    assists = regular.get("assists", 0)

    return goals, assists

if __name__ == "__main__":
    app.run(debug=True)
