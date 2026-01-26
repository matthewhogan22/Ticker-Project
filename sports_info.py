import requests
from datetime import date, datetime
import os
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
import time

utc_time = datetime.now(ZoneInfo('UTC')) 

# Data Holders for all Games
nfl_dict = {}
nba_dict = {}
mlb_dict = {}

# Base variables needed across the whole code

def get_league_data(sport, league):
    response = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard")
    return response.json()

# Gets NFL Data - stored in nfl_dict
# Current fields gathered
#   Home Team and ID
#   Away Team and ID
#   Team with Current Possession of Ball
#   Status of Game (Either Time and Quarter, Final, or Time of Game)
#   Down, Distance, and Yard Line
def set_nfl_dict():
    nfl_teams_dict = {}
    nfl_data = get_league_data("football", "nfl")
    games = nfl_data["events"]
    for game in games:
        game_dict = {}
        # Team Section
        home_team_raw = game["competitions"][0]["competitors"][0]
        home_team_id = home_team_raw["id"]
        home_team_name = home_team_raw["team"]["abbreviation"]
        home_score = game["competitions"][0]["competitors"][0]["score"]
        game_dict["home_score"] = home_score

        away_team_raw = game["competitions"][0]["competitors"][1]
        away_team_id = away_team_raw["id"]
        away_team_name = away_team_raw["team"]["abbreviation"]
        away_score = game["competitions"][0]["competitors"][1]["score"]
        game_dict["away_score"] = away_score

        nfl_teams_dict[home_team_id] = home_team_name
        nfl_teams_dict[away_team_id] = away_team_name
        comp = game["competitions"][0]
        game_name = f"{home_team_name} vs {away_team_name}"

        home_team_record = game["competitions"][0]["competitors"][0]["records"][0]["summary"]
        away_team_record = game["competitions"][0]["competitors"][1]["records"][0]["summary"]
        game_dict["home_record"] = home_team_record
        game_dict["away_record"] = away_team_record

        # Situation Section
        situation = comp.get("situation")
        possession = situation.get("possession") if situation else None
        if possession != None:
            possession_team = nfl_teams_dict[possession]
        else:
            possession_team = "N/A"
        game_dict["possession"] = possession_team
        down = situation.get("down") if situation else None 
        distance = situation.get("distance") if situation else None
        yard_line = situation.get("possessionText") if situation else None
        down_and_dist = f"{down} & {distance} - {yard_line}"
        game_dict["down_and_dist"] = down_and_dist

        # Status Section
        status = comp.get("status")
        time_left = status["type"]["detail"]
        game_dict["status"] = time_left

        # Misc Section
        time = game["date"]
        dt_utc = datetime.fromisoformat(time.replace("Z", "+00:00"))
        dt_est = dt_utc.astimezone(ZoneInfo("America/New_York"))
        kickoff_time = dt_est.strftime("%Y-%m-%d %I:%M %p")
        game_dict["game_time"] = kickoff_time

        nfl_dict[game_name] = game_dict
        
    print(nfl_dict)

set_nfl_dict()