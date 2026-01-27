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
ncaaf_dict = {}

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
    nfl_dict.clear()
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
        
    # print(nfl_dict)

def set_nba_dict():
    nba_dict.clear()
    nba_teams_dict = {}
    nba_data = get_league_data("basketball", "nba")
    games = nba_data["events"]
    for game in games:
        game_dict = {}
        # Team Section
        teams = game["competitions"][0]["competitors"]
        home_raw = teams[0]
        away_raw = teams[1]
        home_team_name = home_raw["team"]["abbreviation"]
        away_team_name = away_raw["team"]["abbreviation"]
        game_name = f"{home_team_name} vs {away_team_name}"
        home_score = home_raw["score"]
        away_score = away_raw["score"]
        game_dict["home_score"] = home_score
        game_dict["away_score"] = away_score
        home_record = home_raw["records"][0]["summary"]
        away_record = away_raw["records"][0]["summary"]
        game_dict["home_record"] = home_record
        game_dict["away_record"] = away_record

        # Status Section
        comp = game["competitions"][0]
        status = comp.get("status")
        time_left = status["type"]["detail"]
        game_dict["status"] = time_left

        # Misc Section
        time = game["date"]
        dt_utc = datetime.fromisoformat(time.replace("Z", "+00:00"))
        dt_est = dt_utc.astimezone(ZoneInfo("America/New_York"))
        tipoff_time = dt_est.strftime("%Y-%m-%d %I:%M %p")
        game_dict["game_time"] = tipoff_time


        nba_dict[game_name] = game_dict

def set_mlb_dict():
    mlb_dict.clear()
    mlb_data = get_league_data("baseball", "mlb")
    games = mlb_data["events"]
    for game in games:
        game_dict = {}
        # Team Section
        teams = game["competitions"][0]["competitors"]
        home_raw = teams[0]
        away_raw = teams[1]
        home_team_name = home_raw["team"]["abbreviation"]
        away_team_name = away_raw["team"]["abbreviation"]
        game_name = f"{home_team_name} vs {away_team_name}"
        home_score = home_raw["score"]
        away_score = away_raw["score"]
        game_dict["home_score"] = home_score
        game_dict["away_score"] = away_score
        home_records = home_raw.get("records", [])
        away_records = away_raw.get("records", [])
        home_record = home_records[0]["summary"] if home_records else None
        away_record = away_records[0]["summary"] if away_records else None
        game_dict["home_record"] = home_record
        game_dict["away_record"] = away_record

        # Status Section
        comp = game["competitions"][0]
        status = comp.get("status")
        time_left = status["type"]["detail"]
        game_dict["status"] = time_left

        # Misc Section
        time = game["date"]
        dt_utc = datetime.fromisoformat(time.replace("Z", "+00:00"))
        dt_est = dt_utc.astimezone(ZoneInfo("America/New_York"))
        tipoff_time = dt_est.strftime("%Y-%m-%d %I:%M %p")
        game_dict["game_time"] = tipoff_time


        mlb_dict[game_name] = game_dict

def get_ncaaf_conf(team_id):
    team = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/{team_id}")
    team_data = team.json()

    team = team_data.get("team", {})
    conf_standing = team.get("standingSummary")
    if not conf_standing:
        return None
    if " in " not in conf_standing:
        return None
    conf_split = conf_standing.split(" in ")
    conf = conf_split[1]
    return conf

def set_ncaaf_dict():
    ncaaf_dict.clear()
    ncaaf_teams_dict = {}
    ncaaf_data = get_league_data("football", "college-football")
    games = ncaaf_data["events"]
    for game in games:
        game_dict = {}
        # Team Section
        home_team_raw = game["competitions"][0]["competitors"][0]
        home_team_id = home_team_raw["id"]
        home_conf = get_ncaaf_conf(home_team_id)
        game_dict["home_conf"] = home_conf
        home_team_name = home_team_raw["team"]["abbreviation"]
        home_score = game["competitions"][0]["competitors"][0]["score"]
        game_dict["home_score"] = home_score

        away_team_raw = game["competitions"][0]["competitors"][1]
        away_team_id = away_team_raw["id"]
        away_conf = get_ncaaf_conf(away_team_id)
        game_dict["away_conf"] = away_conf
        away_team_name = away_team_raw["team"]["abbreviation"]
        away_score = game["competitions"][0]["competitors"][1]["score"]
        game_dict["away_score"] = away_score

        ncaaf_teams_dict[home_team_id] = home_team_name
        ncaaf_teams_dict[away_team_id] = away_team_name
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
            possession_team = ncaaf_teams_dict[possession]
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

        ncaaf_dict[game_name] = game_dict



# set_nba_dict()
# set_nfl_dict()
# set_mlb_dict()
set_ncaaf_dict()
# # print(nba_dict)
# # print(nfl_dict)
# # print(mlb_dict)
print(ncaaf_dict)