from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    redirect,
    url_for
)

from settings import (
    add_tracked_bet,
    delete_tracked_bet,
    get_tracked_bet,
    get_tracked_bets,
    load_settings,
    save_settings,
    update_tracked_bet,
)

from sports_odds import (
    SportsOddsError,
    get_event_options,
    get_market_options,
)

from bet_tracker import (
    get_bet_progress,
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

# ---------------------------------------------------------
# BETTING API
# ---------------------------------------------------------


@app.get(
    "/api/bets"
)
def api_get_bets():

    return jsonify(
        {
            "ok": True,
            "bets": get_tracked_bets(),
        }
    )


@app.post(
    "/api/bets"
)
def api_add_bet():

    payload = (
        request.get_json(
            silent=True
        )
        or {}
    )

    required_fields = (
        "event_id",
        "odd_id",
        "league",
        "bet_type",
        "selection",
        "side",
        "event_name",
    )

    for field in required_fields:

        if not str(
            payload.get(
                field,
                ""
            )
        ).strip():

            return jsonify(
                {
                    "ok": False,
                    "error":
                        f"Missing required field: {field}",
                }
            ), 400

    valid_bet_types = {
        "spread",
        "moneyline",
        "total",
        "player_prop",
    }

    bet_type = (
        str(
            payload.get(
                "bet_type"
            )
        )
        .strip()
        .lower()
    )

    if bet_type not in valid_bet_types:

        return jsonify(
            {
                "ok": False,
                "error": "Invalid bet type.",
            }
        ), 400

    line = payload.get(
        "line"
    )

    if bet_type != "moneyline":

        try:
            line = float(
                line
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify(
                {
                    "ok": False,
                    "error":
                        "A valid line is required.",
                }
            ), 400

    else:

        line = None

    odds = payload.get(
        "odds"
    )

    if odds not in (
        None,
        ""
    ):

        try:
            odds = int(
                odds
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify(
                {
                    "ok": False,
                    "error":
                        "Odds must be a whole number such as -110 or +150.",
                }
            ), 400

    else:
        odds = None

    bet = {
        "event_id":
            str(
                payload[
                    "event_id"
                ]
            ).strip(),

        "odd_id":
            str(
                payload[
                    "odd_id"
                ]
            ).strip(),

        "league":
            str(
                payload[
                    "league"
                ]
            )
            .strip()
            .upper(),

        "event_name":
            str(
                payload[
                    "event_name"
                ]
            ).strip(),

        "bet_type":
            bet_type,

        "selection":
            str(
                payload[
                    "selection"
                ]
            ).strip(),

        "side":
            str(
                payload[
                    "side"
                ]
            )
            .strip()
            .lower(),

        "stat_id":
            str(
                payload.get(
                    "stat_id",
                    ""
                )
            ).strip(),

        "stat_name":
            str(
                payload.get(
                    "stat_name",
                    ""
                )
            ).strip(),

        "line":
            line,

        "odds":
            odds,

        "sportsbook":
            str(
                payload.get(
                    "sportsbook",
                    ""
                )
            )
            .strip()
            .lower(),

        "active":
            True,
    }

    saved_bet = add_tracked_bet(
        bet
    )

    return jsonify(
        {
            "ok": True,
            "bet": saved_bet,
        }
    ), 201


@app.put(
    "/api/bets/<bet_id>"
)
def api_update_bet(
    bet_id
):

    existing = get_tracked_bet(
        bet_id
    )

    if existing is None:

        return jsonify(
            {
                "ok": False,
                "error": "Bet not found.",
            }
        ), 404

    payload = (
        request.get_json(
            silent=True
        )
        or {}
    )

    allowed_fields = {
        "line",
        "odds",
        "sportsbook",
        "active",
    }

    updates = {}

    for field in allowed_fields:

        if field in payload:

            updates[
                field
            ] = payload[
                field
            ]

    if "line" in updates:

        if updates[
            "line"
        ] in (
            None,
            ""
        ):

            updates[
                "line"
            ] = None

        else:

            try:

                updates[
                    "line"
                ] = float(
                    updates[
                        "line"
                    ]
                )

            except (
                TypeError,
                ValueError
            ):

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            "Invalid line.",
                    }
                ), 400

    if "odds" in updates:

        if updates[
            "odds"
        ] in (
            None,
            ""
        ):

            updates[
                "odds"
            ] = None

        else:

            try:

                updates[
                    "odds"
                ] = int(
                    updates[
                        "odds"
                    ]
                )

            except (
                TypeError,
                ValueError
            ):

                return jsonify(
                    {
                        "ok": False,
                        "error":
                            "Invalid odds.",
                    }
                ), 400

    updated = update_tracked_bet(
        bet_id,
        updates
    )

    return jsonify(
        {
            "ok": True,
            "bet": updated,
        }
    )


@app.delete(
    "/api/bets/<bet_id>"
)
def api_delete_bet(
    bet_id
):

    deleted = delete_tracked_bet(
        bet_id
    )

    if not deleted:

        return jsonify(
            {
                "ok": False,
                "error": "Bet not found.",
            }
        ), 404

    return jsonify(
        {
            "ok": True,
        }
    )


@app.get(
    "/api/bets/status"
)
def api_bet_status():

    results = []

    for bet in get_tracked_bets():

        result = dict(
            bet
        )

        result[
            "progress"
        ] = get_bet_progress(
            bet
        )

        results.append(
            result
        )

    return jsonify(
        {
            "ok": True,
            "bets": results,
        }
    )


@app.get(
    "/api/betting/events"
)
def api_betting_events():

    league = (
        request.args.get(
            "league",
            ""
        )
        .strip()
        .upper()
    )

    valid_leagues = {
        "NFL",
        "NCAAF",
        "NBA",
        "MLB",
    }

    if league not in valid_leagues:

        return jsonify(
            {
                "ok": False,
                "error":
                    "Invalid league.",
            }
        ), 400

    try:

        events = get_event_options(
            league
        )

    except SportsOddsError as exc:

        return jsonify(
            {
                "ok": False,
                "error": str(
                    exc
                ),
            }
        ), 502

    return jsonify(
        {
            "ok": True,
            "events": events,
        }
    )


@app.get(
    "/api/betting/events/<event_id>/markets"
)
def api_betting_markets(
    event_id
):

    try:

        markets = get_market_options(
            event_id
        )

    except SportsOddsError as exc:

        return jsonify(
            {
                "ok": False,
                "error": str(
                    exc
                ),
            }
        ), 502

    return jsonify(
        {
            "ok": True,
            "markets": markets,
        }
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )