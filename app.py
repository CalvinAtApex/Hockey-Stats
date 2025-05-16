from flask import Flask, jsonify, render_template
import aiohttp
import asyncio
from datetime import datetime

app = Flask(__name__)

async def fetch_json(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            raise Exception(f"Failed to fetch {url}: {response.status}")
        return await response.json()

def get_current_season_id():
    now = datetime.now()
    year = now.year if now.month >= 9 else now.year - 1
    return f"{year}{year+1}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/teams")
async def get_teams():
    url = "https://api-web.nhle.com/v1/standings/now"
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, url)

    teams = []
    for record in data.get("standings", []):
        team_info = {
            "abbrev": record.get("teamAbbrev", {}).get("default"),
            "name": record.get("teamName", {}).get("default"),
        }
        if team_info["abbrev"] and team_info["name"]:
            teams.append(team_info)

    teams.sort(key=lambda t: t["name"])
    return jsonify(teams)

@app.route("/roster/<team_abbrev>")
async def get_roster(team_abbrev):
    season_id = get_current_season_id()
    url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/{season_id}"

    async with aiohttp.ClientSession() as session:
        try:
            data = await fetch_json(session, url)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        players = []
        for category in ["forwards", "defensemen", "goalies"]:
            for player in data.get(category, []):
                stats_goals, stats_assists = await get_player_stats(session, player["id"], season_id)
                players.append({
                    "id": player["id"],
                    "name": f"{player['firstName']['default']} {player['lastName']['default']}",
                    "number": player.get("sweaterNumber", "N/A"),
                    "position": player.get("positionCode", "N/A"),
                    "goals": stats_goals,
                    "assists": stats_assists
                })

    return jsonify(players)

async def get_player_stats(session, player_id, season_id):
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    try:
        data = await fetch_json(session, url)
        splits = data.get("featuredStats", {}).get("regularSeason", {}).get("subSeason", [])
        
        # Filter only dicts (skip strings)
        splits = [entry for entry in splits if isinstance(entry, dict)]

        nhl_stats = next(
            (entry for entry in splits if entry.get("leagueAbbrev") == "NHL" and entry.get("seasonId") == season_id),
            None
        )
        if nhl_stats:
            return nhl_stats.get("goals", 0), nhl_stats.get("assists", 0)
    except Exception as e:
        print(f"Error fetching stats for player {player_id}: {e}")
    
    return 0, 0

if __name__ == "__main__":
    app.run(debug=True)
