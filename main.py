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

            # Reload settings here as well so
            # changes don't require finishing
            # the entire ticker rotation.

            for game_name, game in games.items():

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