from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for
)

from settings import (
    load_settings,
    save_settings
)


app = Flask(
    __name__
)

TEAM_OPTIONS = {

    "nfl": [
        ("ARI", "Arizona Cardinals"),
        ("ATL", "Atlanta Falcons"),
        ("BAL", "Baltimore Ravens"),
        ("BUF", "Buffalo Bills"),
        ("CAR", "Carolina Panthers"),
        ("CHI", "Chicago Bears"),
        ("CIN", "Cincinnati Bengals"),
        ("CLE", "Cleveland Browns"),
        ("DAL", "Dallas Cowboys"),
        ("DEN", "Denver Broncos"),
        ("DET", "Detroit Lions"),
        ("GB", "Green Bay Packers"),
        ("HOU", "Houston Texans"),
        ("IND", "Indianapolis Colts"),
        ("JAX", "Jacksonville Jaguars"),
        ("KC", "Kansas City Chiefs"),
        ("LV", "Las Vegas Raiders"),
        ("LAC", "Los Angeles Chargers"),
        ("LAR", "Los Angeles Rams"),
        ("MIA", "Miami Dolphins"),
        ("MIN", "Minnesota Vikings"),
        ("NE", "New England Patriots"),
        ("NO", "New Orleans Saints"),
        ("NYG", "New York Giants"),
        ("NYJ", "New York Jets"),
        ("PHI", "Philadelphia Eagles"),
        ("PIT", "Pittsburgh Steelers"),
        ("SEA", "Seattle Seahawks"),
        ("SF", "San Francisco 49ers"),
        ("TB", "Tampa Bay Buccaneers"),
        ("TEN", "Tennessee Titans"),
        ("WSH", "Washington Commanders"),
    ],

    "nba": [
        ("ATL", "Atlanta Hawks"),
        ("BOS", "Boston Celtics"),
        ("BKN", "Brooklyn Nets"),
        ("CHA", "Charlotte Hornets"),
        ("CHI", "Chicago Bulls"),
        ("CLE", "Cleveland Cavaliers"),
        ("DAL", "Dallas Mavericks"),
        ("DEN", "Denver Nuggets"),
        ("DET", "Detroit Pistons"),
        ("GSW", "Golden State Warriors"),
        ("HOU", "Houston Rockets"),
        ("IND", "Indiana Pacers"),
        ("LAC", "LA Clippers"),
        ("LAL", "Los Angeles Lakers"),
        ("MEM", "Memphis Grizzlies"),
        ("MIA", "Miami Heat"),
        ("MIL", "Milwaukee Bucks"),
        ("MIN", "Minnesota Timberwolves"),
        ("NO", "New Orleans Pelicans"),
        ("NYK", "New York Knicks"),
        ("OKC", "Oklahoma City Thunder"),
        ("ORL", "Orlando Magic"),
        ("PHI", "Philadelphia 76ers"),
        ("PHX", "Phoenix Suns"),
        ("POR", "Portland Trail Blazers"),
        ("SAC", "Sacramento Kings"),
        ("SAS", "San Antonio Spurs"),
        ("TOR", "Toronto Raptors"),
        ("UTA", "Utah Jazz"),
        ("WSH", "Washington Wizards"),
    ],

    "mlb": [
        ("ARI", "Arizona Diamondbacks"),
        ("ATH", "Athletics"),
        ("ATL", "Atlanta Braves"),
        ("BAL", "Baltimore Orioles"),
        ("BOS", "Boston Red Sox"),
        ("CHC", "Chicago Cubs"),
        ("CHW", "Chicago White Sox"),
        ("CIN", "Cincinnati Reds"),
        ("CLE", "Cleveland Guardians"),
        ("COL", "Colorado Rockies"),
        ("DET", "Detroit Tigers"),
        ("HOU", "Houston Astros"),
        ("KC", "Kansas City Royals"),
        ("LAA", "Los Angeles Angels"),
        ("LAD", "Los Angeles Dodgers"),
        ("MIA", "Miami Marlins"),
        ("MIL", "Milwaukee Brewers"),
        ("MIN", "Minnesota Twins"),
        ("NYM", "New York Mets"),
        ("NYY", "New York Yankees"),
        ("PHI", "Philadelphia Phillies"),
        ("PIT", "Pittsburgh Pirates"),
        ("SD", "San Diego Padres"),
        ("SEA", "Seattle Mariners"),
        ("SF", "San Francisco Giants"),
        ("STL", "St. Louis Cardinals"),
        ("TB", "Tampa Bay Rays"),
        ("TEX", "Texas Rangers"),
        ("TOR", "Toronto Blue Jays"),
        ("WSH", "Washington Nationals"),
    ],
}


@app.route("/")
def index():

    settings = (
        load_settings()
    )

    return render_template(
        "index.html",
        settings=settings,
        team_options=TEAM_OPTIONS
    )


@app.route(
    "/save",
    methods=["POST"]
)
def save():

    settings = (
        load_settings()
    )

    # ---------------------------------------------
    # SPORTS
    # ---------------------------------------------

    settings["sports"] = {

        "nfl":
            "nfl"
            in request.form,

        "ncaaf":
            "ncaaf"
            in request.form,

        "nba":
            "nba"
            in request.form,

        "mlb":
            "mlb"
            in request.form,
    }

    # ---------------------------------------------
    # FAVORITE TEAMS
    # ---------------------------------------------

    valid_favorite_modes = {
        "all",
        "prioritize",
        "favorites_only"
    }


    settings.setdefault(
        "favorites",
        {}
    )


    for sport in (
        "nfl",
        "nba",
        "mlb"
    ):

        favorite_mode = request.form.get(
            f"{sport}_favorite_mode",
            "all"
        )

        if (
            favorite_mode
            not in valid_favorite_modes
        ):

            favorite_mode = "all"


        favorite_teams = request.form.getlist(
            f"{sport}_favorite_teams"
        )


        # Normalize values.
        favorite_teams = [
            team.strip().upper()
            for team in favorite_teams
            if team.strip()
        ]


        settings["favorites"][sport] = {

            "mode":
                favorite_mode,

            "teams":
                favorite_teams,

        }

    # ---------------------------------------------
    # NCAAF FAVORITES
    # ---------------------------------------------

    ncaaf_mode = request.form.get(
        "ncaaf_favorite_mode",
        "all"
    )

    if ncaaf_mode not in valid_favorite_modes:
        ncaaf_mode = "all"


    ncaaf_text = request.form.get(
        "ncaaf_favorite_teams_text",
        ""
    )


    ncaaf_teams = [
        team.strip().upper()
        for team in ncaaf_text.split(",")
        if team.strip()
    ]


    settings["favorites"]["ncaaf"] = {
        "mode": ncaaf_mode,
        "teams": ncaaf_teams,
    }

    # ---------------------------------------------
    # DISPLAY OPTIONS
    # ---------------------------------------------

    game_filter = request.form.get(
        "game_filter",
        "live_upcoming"
    )

    valid_filters = {
        "all",
        "live_upcoming",
        "live"
    }

    if game_filter not in valid_filters:
        game_filter = "live_upcoming"

    settings[
        "display"
    ][
        "game_filter"
    ] = game_filter

    try:

        seconds_per_game = int(
            request.form.get(
                "seconds_per_game",
                8
            )
        )

    except ValueError:

        seconds_per_game = 8

    # Keep it reasonable.
    seconds_per_game = max(
        2,
        min(
            seconds_per_game,
            60
        )
    )

    settings[
        "display"
    ][
        "seconds_per_game"
    ] = seconds_per_game

    # ---------------------------------------------
    # SAVE
    # ---------------------------------------------

    save_settings(
        settings
    )

    return redirect(
        url_for(
            "index",
            saved="1"
        )
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )