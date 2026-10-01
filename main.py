import time

from display import ScoreboardDisplay

from settings import load_settings

from sports_info import (
    get_sport_games
)


SPORT_ORDER = [
    "nfl",
    "ncaaf",
    "nba",
    "mlb",
]

def should_show_game(game, game_filter):

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

    if favorite_mode == "favorites_only":

        return [
            (
                game_name,
                game
            )
            for game_name, game
            in game_items
            if is_favorite_game(
                game,
                favorite_teams
            )
        ]

    if favorite_mode == "prioritize":

        favorite_games = []
        other_games = []

        for game_name, game in game_items:

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


def get_enabled_sports(
    settings
):

    enabled = []

    sports_settings = settings.get(
        "sports",
        {}
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


def main():

    print(
        "Starting Sports Ticker..."
    )

    display = ScoreboardDisplay(
        brightness=30
    )

    while True:

        # Reload settings every cycle.
        # This means changes from the website
        # automatically take effect.

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

            favorite_mode = sport_favorites.get(
                "mode",
                "all"
            )

            favorite_teams = sport_favorites.get(
                "teams",
                []
            )

            ordered_games = apply_team_preferences(
                games,
                favorite_teams,
                favorite_mode
            )

            # Reload settings here as well so
            # changes don't require finishing
            # the entire ticker rotation.

            for game_name, game in ordered_games:

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

                # User may have disabled this sport
                # while it was currently cycling.
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

                if not should_show_game(
                    game,
                    game_filter
                ):
                    continue

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

                print(
                    f"Showing: {game_name}"
                )

                display.show_game(
                    sport,
                    game,
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