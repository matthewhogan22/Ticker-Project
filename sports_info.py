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
# GENERAL HELPERS
# ---------------------------------------------------------

def get_competition(game):

    competitions = game.get(
        "competitions",
        []
    )

    if not competitions:
        return {}

    return competitions[0]


def get_competitors(game):

    competition = get_competition(
        game
    )

    competitors = competition.get(
        "competitors",
        []
    )

    home_team = None
    away_team = None

    for competitor in competitors:

        if competitor.get(
            "homeAway"
        ) == "home":

            home_team = competitor

        elif competitor.get(
            "homeAway"
        ) == "away":

            away_team = competitor

    # Fallback if ESPN ever omits homeAway.
    if home_team is None and competitors:
        home_team = competitors[0]

    if (
        away_team is None
        and len(competitors) > 1
    ):
        away_team = competitors[1]

    return home_team, away_team


def get_record(team):

    if not team:
        return ""

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

    if not team:
        return "FFFFFF"

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


def get_team_alternate_color(team):

    if not team:
        return ""

    team_data = team.get(
        "team",
        {}
    )

    alternate_color = team_data.get(
        "alternateColor"
    )

    if not alternate_color:
        return ""

    return alternate_color


def get_game_state(game):

    competition = get_competition(
        game
    )

    status = competition.get(
        "status",
        {}
    )

    status_type = status.get(
        "type",
        {}
    )

    return status_type.get(
        "state",
        ""
    )


def get_status(game):

    competition = get_competition(
        game
    )

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


def get_short_status(game):

    competition = get_competition(
        game
    )

    status = competition.get(
        "status",
        {}
    )

    status_type = status.get(
        "type",
        {}
    )

    short_detail = status_type.get(
        "shortDetail"
    )

    if short_detail:
        return short_detail

    return get_status(
        game
    )


def get_game_time(game):

    raw_time = game.get(
        "date"
    )

    if not raw_time:
        return ""

    try:

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

    except ValueError:
        return ""


def get_score(team):

    if not team:
        return "0"

    score = team.get(
        "score"
    )

    if score is None:
        return "0"

    return str(
        score
    )

def add_baseball_information(
    game,
    game_data
):

    competition = get_competition(
        game
    )

    situation = competition.get(
        "situation",
        {}
    ) or {}

    status = competition.get(
        "status",
        {}
    )

    # -----------------------------------------------------
    # OUTS
    # -----------------------------------------------------

    game_data["outs"] = situation.get(
        "outs",
        0
    )

    # -----------------------------------------------------
    # BASE RUNNERS
    # -----------------------------------------------------

    game_data["on_first"] = bool(
        situation.get(
            "onFirst",
            False
        )
    )

    game_data["on_second"] = bool(
        situation.get(
            "onSecond",
            False
        )
    )

    game_data["on_third"] = bool(
        situation.get(
            "onThird",
            False
        )
    )

    # -----------------------------------------------------
    # BALLS / STRIKES
    # -----------------------------------------------------

    game_data["balls"] = situation.get(
        "balls",
        0
    )

    game_data["strikes"] = situation.get(
        "strikes",
        0
    )

    # -----------------------------------------------------
    # INNING
    # -----------------------------------------------------

    period = status.get(
        "period"
    )

    if period is None:

        period = competition.get(
            "status",
            {}
        ).get(
            "period",
            0
        )

    game_data["inning"] = period or 0

    # ESPN short status usually contains things like:
    #
    # Top 7th
    # Bot 4th
    # Mid 6th
    #
    # We'll use it to determine the inning half.

    short_status = (
        game_data
        .get(
            "short_status",
            ""
        )
        .lower()
    )

    if (
        "top" in short_status
        or "mid" in short_status
    ):

        game_data[
            "inning_half"
        ] = "top"

    elif (
        "bot" in short_status
        or "bottom" in short_status
        or "end" in short_status
    ):

        game_data[
            "inning_half"
        ] = "bottom"

    else:

        game_data[
            "inning_half"
        ] = ""

    return game_data


# ---------------------------------------------------------
# BASIC GAME OBJECT
# ---------------------------------------------------------

def build_basic_game(game):

    home, away = get_competitors(
        game
    )

    if home is None or away is None:
        return None

    home_team_data = home.get(
        "team",
        {}
    )

    away_team_data = away.get(
        "team",
        {}
    )

    home_name = home_team_data.get(
        "abbreviation",
        "HOME"
    )

    away_name = away_team_data.get(
        "abbreviation",
        "AWAY"
    )

    game_data = {

        "home_team": home_name,

        "away_team": away_name,

        "home_id": str(
            home.get(
                "id",
                ""
            )
        ),

        "away_id": str(
            away.get(
                "id",
                ""
            )
        ),

        "home_score": get_score(
            home
        ),

        "away_score": get_score(
            away
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

        "home_alternate_color": get_team_alternate_color(
            home
        ),

        "away_alternate_color": get_team_alternate_color(
            away
        ),

        "status": get_status(
            game
        ),

        "short_status": get_short_status(
            game
        ),

        "game_time": get_game_time(
            game
        ),

        # Keep the original ESPN UTC timestamp.
        # display.py will format this for the panel.
        "start_time": game.get(
            "date",
            ""
        ),

        # ESPN states:
        #
        # pre  = upcoming
        # in   = live
        # post = finished
        "state": get_game_state(
            game
        ),
    }

    return game_data


# ---------------------------------------------------------
# FOOTBALL INFORMATION
# ---------------------------------------------------------

def add_football_information(
    game,
    game_data
):

    competition = get_competition(
        game
    )

    situation = competition.get(
        "situation"
    )

    game_data[
        "possession"
    ] = ""

    game_data[
        "down_and_distance"
    ] = ""

    game_data[
        "possession_text"
    ] = ""

    if not situation:
        return game_data

    possession_id = situation.get(
        "possession"
    )

    if possession_id:

        if (
            game_data["home_id"]
            == str(possession_id)
        ):

            game_data[
                "possession"
            ] = game_data[
                "home_team"
            ]

        elif (
            game_data["away_id"]
            == str(possession_id)
        ):

            game_data[
                "possession"
            ] = game_data[
                "away_team"
            ]

    down = situation.get(
        "down"
    )

    distance = situation.get(
        "distance"
    )

    possession_text = situation.get(
        "possessionText",
        ""
    )

    game_data[
        "possession_text"
    ] = possession_text

    if (
        down is not None
        and distance is not None
        and down != 0
    ):

        game_data[
            "down_and_distance"
        ] = (
            f"{down}&{distance}"
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

        if game_data is None:
            continue

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

        if game_data is None:
            continue

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

        if game_data is None:
            continue

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

        if game_data is None:
            continue

        game_data = add_baseball_information(
            game,
            game_data
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
                f"Error loading "
                f"{sport}: {exc}"
            )