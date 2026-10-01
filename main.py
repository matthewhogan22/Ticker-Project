import time

from display import ScoreboardDisplay

from settings import (
    get_active_bets,
    load_settings,
)

from sports_info import (
    get_sport_games,
)

from bet_tracker import (
    get_bet_progress,
)


SPORT_ORDER = [
    "nfl",
    "ncaaf",
    "nba",
    "mlb",
]


# ---------------------------------------------------------
# GAME FILTERING
# ---------------------------------------------------------


def should_show_game(
    game,
    game_filter
):

    state = game.get(
        "state",
        ""
    )

    if game_filter == "all":
        return True

    if game_filter == "live":
        return state == "in"

    if game_filter == "live_upcoming":
        return state in (
            "pre",
            "in"
        )

    return True


# ---------------------------------------------------------
# FAVORITES
# ---------------------------------------------------------


def is_favorite_game(
    game,
    favorite_teams
):

    favorite_teams = {
        str(team).upper()
        for team in favorite_teams
    }

    away_team = str(
        game.get(
            "away_team",
            ""
        )
    ).upper()

    home_team = str(
        game.get(
            "home_team",
            ""
        )
    ).upper()

    return (
        away_team in favorite_teams
        or home_team in favorite_teams
    )


def apply_team_preferences(
    games,
    favorite_teams,
    favorite_mode
):

    game_items = list(
        games.items()
    )

    if (
        favorite_mode
        == "favorites_only"
    ):

        return [
            (
                game_name,
                game
            )
            for (
                game_name,
                game
            )
            in game_items
            if is_favorite_game(
                game,
                favorite_teams
            )
        ]

    if (
        favorite_mode
        == "prioritize"
    ):

        favorite_games = []
        other_games = []

        for (
            game_name,
            game
        ) in game_items:

            item = (
                game_name,
                game
            )

            if is_favorite_game(
                game,
                favorite_teams
            ):

                favorite_games.append(
                    item
                )

            else:

                other_games.append(
                    item
                )

        return (
            favorite_games
            + other_games
        )

    return game_items


# ---------------------------------------------------------
# ENABLED SPORTS
# ---------------------------------------------------------


def get_enabled_sports(
    settings
):

    enabled = []

    sports_settings = (
        settings.get(
            "sports",
            {}
        )
    )

    for sport in SPORT_ORDER:

        if sports_settings.get(
            sport,
            False
        ):

            enabled.append(
                sport
            )

    return enabled


# ---------------------------------------------------------
# BET HELPERS
# ---------------------------------------------------------


def normalize_name(
    value
):

    return (
        str(
            value or ""
        )
        .strip()
        .lower()
        .replace(
            ".",
            ""
        )
        .replace(
            "-",
            " "
        )
    )

def bet_matches_game(
    bet,
    sport,
    game
):

    bet_league = (
        str(
            bet.get(
                "league",
                ""
            )
        )
        .strip()
        .lower()
    )

    if bet_league != sport.lower():
        return False

    bet_away = (
        str(
            bet.get(
                "away_team",
                ""
            )
        )
        .strip()
        .upper()
    )

    bet_home = (
        str(
            bet.get(
                "home_team",
                ""
            )
        )
        .strip()
        .upper()
    )

    game_away = (
        str(
            game.get(
                "away_team",
                ""
            )
        )
        .strip()
        .upper()
    )

    game_home = (
        str(
            game.get(
                "home_team",
                ""
            )
        )
        .strip()
        .upper()
    )

    return (
        bet_away == game_away
        and bet_home == game_home
    )


def get_bets_for_game(
    sport,
    game
):

    bets = get_active_bets()

    return [
        bet
        for bet in bets
        if bet_matches_game(
            bet,
            sport,
            game
        )
    ]


def should_show_bet(
    bet,
    progress
):
    """
    Do not show API errors as ticker screens.

    Pending bets are allowed because it can be useful
    to see the line before the game starts.
    """

    state = progress.get(
        "state",
        ""
    )

    return state not in {
        "error",
    }


# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------


def main():

    print(
        "Starting Sports Ticker..."
    )

    display = ScoreboardDisplay(
        brightness=30
    )

    while True:

        # Reload settings every cycle.
        settings = load_settings()

        enabled_sports = (
            get_enabled_sports(
                settings
            )
        )

        seconds_per_game = (
            settings
            .get(
                "display",
                {}
            )
            .get(
                "seconds_per_game",
                8
            )
        )

        # ---------------------------------------------
        # NOTHING ENABLED
        # ---------------------------------------------

        if not enabled_sports:

            display.show_message(
                "NO SPORTS",
                "ENABLED",
                seconds=3
            )

            time.sleep(
                2
            )

            continue

        # ---------------------------------------------
        # RUN ENABLED SPORTS
        # ---------------------------------------------

        for sport in enabled_sports:

            print(
                f"Updating {sport.upper()}..."
            )

            try:

                games = get_sport_games(
                    sport
                )

            except Exception as exc:

                print(
                    f"Error updating "
                    f"{sport}: {exc}"
                )

                continue

            if not games:

                print(
                    f"No {sport.upper()} "
                    f"games found."
                )

                continue

            sport_favorites = (
                settings
                .get(
                    "favorites",
                    {}
                )
                .get(
                    sport,
                    {}
                )
            )

            favorite_mode = (
                sport_favorites.get(
                    "mode",
                    "all"
                )
            )

            favorite_teams = (
                sport_favorites.get(
                    "teams",
                    []
                )
            )

            ordered_games = (
                apply_team_preferences(
                    games,
                    favorite_teams,
                    favorite_mode
                )
            )

            # -----------------------------------------
            # GAME ROTATION
            # -----------------------------------------

            for (
                game_name,
                game
            ) in ordered_games:

                latest_settings = (
                    load_settings()
                )

                sport_enabled = (
                    latest_settings
                    .get(
                        "sports",
                        {}
                    )
                    .get(
                        sport,
                        False
                    )
                )

                if not sport_enabled:
                    break

                game_filter = (
                    latest_settings
                    .get(
                        "display",
                        {}
                    )
                    .get(
                        "game_filter",
                        "live_upcoming"
                    )
                )

                seconds_per_game = (
                    latest_settings
                    .get(
                        "display",
                        {}
                    )
                    .get(
                        "seconds_per_game",
                        8
                    )
                )

                # -------------------------------------
                # FIND TRACKED BETS FIRST
                # -------------------------------------

                game_bets = (
                    get_bets_for_game(
                        sport,
                        game
                    )
                )

                show_normal_game = (
                    should_show_game(
                        game,
                        game_filter
                    )
                )

                # If the normal game is filtered out
                # AND there are no tracked bets for it,
                # there is nothing to display.
                if (
                    not show_normal_game
                    and not game_bets
                ):
                    continue

                # -------------------------------------
                # NORMAL GAME SCREEN
                # -------------------------------------

                if show_normal_game:

                    print(
                        f"Showing: {game_name}"
                    )

                    display.show_game(
                        sport,
                        game,
                        seconds=seconds_per_game
                    )

                # -------------------------------------
                # TRACKED BETS FOR THIS GAME
                # -------------------------------------

                for bet in game_bets:

                    try:

                        progress = (
                            get_bet_progress(
                                bet
                            )
                        )

                    except Exception as exc:

                        print(
                            "Error getting bet "
                            f"progress: {exc}"
                        )

                        continue

                    if not should_show_bet(
                        bet,
                        progress
                    ):
                        continue

                    print(
                        "Showing bet: "
                        f"{bet.get('selection', '')} "
                        f"{bet.get('line', '')} "
                        f"| "
                        f"{progress.get('message', '')}"
                    )

                    display.show_bet(
                        bet,
                        progress,
                        seconds=seconds_per_game
                    )

        # Tiny pause before rebuilding scoreboard data.
        time.sleep(
            1
        )


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\nSports ticker stopped."
        )