from flask import Flask, render_template, jsonify
import aiohttp
import asyncio
from datetime import datetime

app = Flask(__name__)

@app.route("/")
async def index():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api-web.nhle.com/v1/standings/now") as resp:
            data = await resp.json()
        teams = [
            {
                "abbrev": record["teamAbbrev"]["default"],
                "name": record["teamName"]["default"],
            }
            for record in data["standings"]
        ]
    return render_template("index.html", teams=teams)

@app.route("/roster/<team_abbrev>")
async def get_roster(team_abbrev):
    current_year = datetime.now().year
    season_id = int(f"{current_year if datetime.now().month >= 9 else current_year - 1}{current_year + 1 if datetime.now().month >= 9 else current_year}")

    roster_url = f"https://api-web.nhle.com/v1/roster/{team_abbrev}/{season_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(roster_url) as resp:
            if resp.status != 200:
                return jsonify({"error": "Failed to fetch roster"}), 500
            data = await resp.json()

        players = []
        all_players = data.get("forwards", []) + data.get("defensemen", []) + data.get("goalies", [])

        tasks = [fetch_player_stats(session, player, season_id) for player in all_players]
        players = await asyncio.gather(*tasks)

    players = [p for p in players if p is not None]  # remove failed lookups
    if not players:
        return jsonify({"error": "No roster data found."}), 404

    return jsonify(players)

async def fetch_player_stats(session, player, season_id):
    player_id = player["id"]
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"

    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                print(f"Failed to fetch stats for player {player_id}: {resp.status}")
                return None
            data = await resp.json()

        splits = data.get("seasonTotals", [])
        nhl_stats = next(
            (entry for entry in splits if entry.get("leagueAbbrev") == "NHL" and entry.get("seasonId") == season_id),
            {}
        )

        goals = nhl_stats.get("goals", 0)
        assists = nhl_stats.get("assists", 0)

        return {
            "name": f"{player['firstName']['default']} {player['lastName']['default']}",
            "number": player.get("sweaterNumber", "N/A"),
            "position": player.get("positionCode", ""),
            "goals": goals,
            "assists": assists,
        }

    except Exception as e:
        print(f"Error fetching stats for player {player_id}: {e}")
        return None

if __name__ == "__main__":
    app.run(debug=True)
