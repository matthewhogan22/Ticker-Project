import requests
from datetime import date, datetime
import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

utc_time = datetime.now(ZoneInfo('UTC')) 

# Data Holders for all Games
nfl_dict = {}
nba_dict = {}

# Base variables needed across the whole code
load_dotenv()
API_KEY = os.getenv("API_KEY")

BASE_URL = "https://api.balldontlie.io"

auth_headers = {"Authorization": API_KEY}
today = date.today().isoformat()

est_tz = ZoneInfo("America/New_York")
# print(today)

# NFL DATA - Stored in football_dict
nfl_response = requests.get(f"{BASE_URL}/nfl/v1/games", headers=auth_headers, params={"dates[]": today})

nfl_data = nfl_response.json()
for game in nfl_data["data"]: 
    raw_time = game["date"][11:16]
    raw_hour = int(raw_time[0:2])
    if int(raw_hour) > 12:
        time = f"{int(raw_hour) - 17}{raw_time[2:]} EST"
    else:
        time = f"{int(raw_hour) - 5}{raw_time[2:]} EST"

    
    home_team = game["home_team"]["abbreviation"]
    away_team = game["visitor_team"]["abbreviation"]

    home_score = game["home_team_score"]
    away_score = game["visitor_team_score"]
    status = game["status"]
    game_line = f"{home_team} vs {away_team}"

    if (home_score == None and away_score == None):
        dt_utc = datetime.fromisoformat(game["date"].replace("Z", "+00:00"))
        dt_est = dt_utc.astimezone(est_tz)
        time_str = dt_est.strftime("%I:%M %p %Z").lstrip("0")
        score_line = f"{time_str}"
    else:
        score_line = f"{home_score} - {away_score} {status}"

    nfl_dict[game_line] = score_line
    

# print(nfl_dict)

# NBA DATA - Stored in basketball_dict
nba_response = requests.get(f"{BASE_URL}/nba/v1/games", headers=auth_headers, params={"dates[]": today})

nba_data = nba_response.json()

# print(nba_data)

for game in nba_data["data"]:
    status = game["status"]
    home_team = game["home_team"]["abbreviation"]
    home_score = game["home_team_score"]

    away_team = game["visitor_team"]["abbreviation"]
    away_score = game["visitor_team_score"]

    game_line = f"{home_team} vs {away_team}"

    if ":" in status:
        dt_utc = datetime.fromisoformat(status.replace("Z", "+00:00"))
        dt_est = dt_utc.astimezone(est_tz)
        time_str = dt_est.strftime("%I:%M %p %Z").lstrip("0")
        # print(time_str)
        score_line = f"{home_score} - {away_score} {time_str}"
    else:
        score_line = f"{home_score} - {away_score} {game["time"]}"

    nba_dict[game_line] = score_line

print(nba_dict)