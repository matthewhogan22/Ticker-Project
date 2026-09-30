import requests

from datetime import datetime
from zoneinfo import ZoneInfo


# ---------------------------------------------------------
# DATA HOLDERS
# ---------------------------------------------------------

nfl_dict = {}
nba_dict = {}
mlb_dict = {}
ncaaf_dict = {}


# ---------------------------------------------------------
# ESPN API
# ---------------------------------------------------------

ESPN_BASE_URL = (
    "https://site.api.espn.com/apis/site/v2/sports"
)


def get_league_data(sport, league):

    url = (
        f"{ESPN_BASE_URL}/"
        f"{sport}/"
        f"{league}/"
        f"scoreboard"
    )

    response = requests.get(
        url,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def get_competitors(game):

    competition = game["competitions"][0]

    competitors = competition["competitors"]

    home_team = None
    away_team = None

    for competitor in competitors:

        if competitor.get("homeAway") == "home":
            home_team = competitor

        elif competitor.get("homeAway") == "away":
            away_team = competitor

    # Fallback in case ESPN does not provide homeAway.
    if home_team is None:
        home_team = competitors[0]

    if away_team is None:
        away_team = competitors[1]

    return home_team, away_team


def get_record(team):

    records = team.get(
        "records",
        []
    )

    if not records:
        return ""

    return records[0].get(
        "summary",
        ""
    )


def get_team_color(team):

    team_data = team.get(
        "team",
        {}
    )

    color = team_data.get(
        "color"
    )

    if not color:
        return "FFFFFF"

    return color


def get_game_time(game):

    raw_time = game.get(
        "date"
    )

    if not raw_time:
        return ""

    dt_utc = datetime.fromisoformat(
        raw_time.replace(
            "Z",
            "+00:00"
        )
    )

    dt_eastern = dt_utc.astimezone(
        ZoneInfo(
            "America/New_York"
        )
    )

    return dt_eastern.strftime(
        "%m/%d %I:%M %p"
    )


def get_status(game):

    competition = game["competitions"][0]

    status = competition.get(
        "status",
        {}
    )

    status_type = status.get(
        "type",
        {}
    )

    return status_type.get(
        "detail",
        ""
    )


def build_basic_game(game):

    home, away = get_competitors(
        game
    )

    home_name = home["team"].get(
        "abbreviation",
        "HOME"
    )

    away_name = away["team"].get(
        "abbreviation",
        "AWAY"
    )

    game_data = {

        "home_team": home_name,

        "away_team": away_name,

        "home_score": home.get(
            "score",
            "0"
        ),

        "away_score": away.get(
            "score",
            "0"
        ),

        "home_record": get_record(
            home
        ),

        "away_record": get_record(
            away
        ),

        "home_color": get_team_color(
            home
        ),

        "away_color": get_team_color(
            away
        ),

        "status": get_status(
            game
        ),

        "game_time": get_game_time(
            game
        ),
    }

    return game_data


# ---------------------------------------------------------
# FOOTBALL HELPERS
# ---------------------------------------------------------

def add_football_information(
    game,
    game_data
):

    competition = game[
        "competitions"
    ][0]

    situation = competition.get(
        "situation"
    )

    game_data["possession"] = ""

    game_data["down_and_distance"] = ""

    if not situation:
        return game_data

    possession_id = situation.get(
        "possession"
    )

    home, away = get_competitors(
        game
    )

    if possession_id:

        if str(home.get("id")) == str(possession_id):

            game_data["possession"] = (
                game_data["home_team"]
            )

        elif str(away.get("id")) == str(possession_id):

            game_data["possession"] = (
                game_data["away_team"]
            )

    possession_text = situation.get(
        "possessionText"
    )

    down = situation.get(
        "down"
    )

    distance = situation.get(
        "distance"
    )

    if (
        down is not None
        and distance is not None
    ):

        game_data[
            "down_and_distance"
        ] = (
            f"{down} & {distance}"
        )

        if possession_text:

            game_data[
                "down_and_distance"
            ] += (
                f" - {possession_text}"
            )

    return game_data


# ---------------------------------------------------------
# NFL
# ---------------------------------------------------------

def set_nfl_dict():

    nfl_dict.clear()

    data = get_league_data(
        "football",
        "nfl"
    )

    games = data.get(
        "events",
        []
    )

    for game in games:

        game_data = build_basic_game(
            game
        )

        game_data = add_football_information(
            game,
            game_data
        )

        game_name = (
            f"{game_data['away_team']} "
            f"at "
            f"{game_data['home_team']}"
        )

        nfl_dict[
            game_name
        ] = game_data

    return nfl_dict


# ---------------------------------------------------------
# COLLEGE FOOTBALL
# ---------------------------------------------------------

def set_ncaaf_dict():

    ncaaf_dict.clear()

    data = get_league_data(
        "football",
        "college-football"
    )

    games = data.get(
        "events",
        []
    )

    for game in games:

        game_data = build_basic_game(
            game
        )

        game_data = add_football_information(
            game,
            game_data
        )

        game_name = (
            f"{game_data['away_team']} "
            f"at "
            f"{game_data['home_team']}"
        )

        ncaaf_dict[
            game_name
        ] = game_data

    return ncaaf_dict


# ---------------------------------------------------------
# NBA
# ---------------------------------------------------------

def set_nba_dict():

    nba_dict.clear()

    data = get_league_data(
        "basketball",
        "nba"
    )

    games = data.get(
        "events",
        []
    )

    for game in games:

        game_data = build_basic_game(
            game
        )

        game_name = (
            f"{game_data['away_team']} "
            f"at "
            f"{game_data['home_team']}"
        )

        nba_dict[
            game_name
        ] = game_data

    return nba_dict


# ---------------------------------------------------------
# MLB
# ---------------------------------------------------------

def set_mlb_dict():

    mlb_dict.clear()

    data = get_league_data(
        "baseball",
        "mlb"
    )

    games = data.get(
        "events",
        []
    )

    for game in games:

        game_data = build_basic_game(
            game
        )

        game_name = (
            f"{game_data['away_team']} "
            f"at "
            f"{game_data['home_team']}"
        )

        mlb_dict[
            game_name
        ] = game_data

    return mlb_dict


# ---------------------------------------------------------
# GENERIC SPORTS FUNCTION
# ---------------------------------------------------------

SPORT_FUNCTIONS = {

    "nfl": set_nfl_dict,

    "ncaaf": set_ncaaf_dict,

    "nba": set_nba_dict,

    "mlb": set_mlb_dict,
}


def get_sport_games(
    sport
):

    function = SPORT_FUNCTIONS.get(
        sport
    )

    if function is None:

        raise ValueError(
            f"Unknown sport: {sport}"
        )

    return function()


# ---------------------------------------------------------
# LOCAL TESTING
# ---------------------------------------------------------

if __name__ == "__main__":

    for sport in SPORT_FUNCTIONS:

        print(
            f"\n--- {sport.upper()} ---"
        )

        try:

            games = get_sport_games(
                sport
            )

            for game_name, game in games.items():

                print(
                    game_name,
                    game
                )

        except Exception as exc:

            print(
                f"Error loading {sport}: {exc}"
            )