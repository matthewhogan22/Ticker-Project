import argparse
import time

from display import ScoreboardDisplay


DEMO_GAMES = {
    "nfl_upcoming": {
        "sport": "nfl",
        "game": {
            "away_team": "ATL",
            "home_team": "NO",
            "away_score": "0",
            "home_score": "0",
            "away_record": "3-1",
            "home_record": "2-2",
            "away_color": "A71930",
            "away_alternate_color": "000000",
            "home_color": "D3BC8D",
            "home_alternate_color": "101820",
            "status": "Mon, October 5",
            "short_status": "10/05 8:15p",
            "start_time": "2026-10-06T00:15:00Z",
            "state": "pre",
            "possession": "",
            "down_and_distance": "",
            "possession_text": "",
        },
    },

    "nfl_live_away": {
        "sport": "nfl",
        "game": {
            "away_team": "ATL",
            "home_team": "NO",
            "away_score": "17",
            "home_score": "14",
            "away_record": "3-1",
            "home_record": "2-2",
            "away_color": "A71930",
            "away_alternate_color": "000000",
            "home_color": "D3BC8D",
            "home_alternate_color": "101820",
            "status": "3rd Quarter",
            "short_status": "3rd 8:42",
            "start_time": "",
            "state": "in",

            "possession": "ATL",
            "down_and_distance": "2&7",
            "possession_text": "ATL 38",
        },
    },

    "nfl_live_home": {
        "sport": "nfl",
        "game": {
            "away_team": "PIT",
            "home_team": "CLE",
            "away_score": "20",
            "home_score": "23",
            "away_record": "2-2",
            "home_record": "3-1",
            "away_color": "FFB612",
            "away_alternate_color": "101820",
            "home_color": "311D00",
            "home_alternate_color": "FF3C00",
            "status": "4th Quarter",
            "short_status": "4th 1:36",
            "start_time": "",
            "state": "in",

            "possession": "CLE",
            "down_and_distance": "3&4",
            "possession_text": "CLE 46",
        },
    },

    "nfl_red_zone": {
        "sport": "nfl",
        "game": {
            "away_team": "KC",
            "home_team": "BUF",
            "away_score": "27",
            "home_score": "28",
            "away_record": "4-0",
            "home_record": "4-0",
            "away_color": "E31837",
            "away_alternate_color": "FFB81C",
            "home_color": "00338D",
            "home_alternate_color": "C60C30",
            "status": "4th Quarter",
            "short_status": "4th 0:42",
            "start_time": "",
            "state": "in",

            "possession": "KC",
            "down_and_distance": "1&10",
            "possession_text": "BUF 18",
        },
    },

    "nfl_final": {
        "sport": "nfl",
        "game": {
            "away_team": "DAL",
            "home_team": "PHI",
            "away_score": "24",
            "home_score": "31",
            "away_record": "2-2",
            "home_record": "4-0",
            "away_color": "003594",
            "away_alternate_color": "869397",
            "home_color": "004C54",
            "home_alternate_color": "A5ACAF",
            "status": "Final",
            "short_status": "Final",
            "start_time": "",
            "state": "post",

            "possession": "",
            "down_and_distance": "",
            "possession_text": "",
        },
    },

    "mlb_live": {
        "sport": "mlb",
        "game": {
            "away_team": "CHW",
            "home_team": "HOU",
            "away_score": "4",
            "home_score": "3",
            "away_record": "84-78",
            "home_record": "81-81",

            "away_color": "000000",
            "away_alternate_color": "C4CED4",

            "home_color": "002D62",
            "home_alternate_color": "EB6E1F",

            "status": "Bottom 5th",
            "short_status": "Bot 5th",
            "start_time": "",
            "state": "in",

            "inning": 5,
            "inning_half": "bottom",

            "balls": 3,
            "strikes": 0,
            "outs": 2,

            "on_first": True,
            "on_second": True,
            "on_third": False,
        },
    },
}


def show_case(
    display,
    case_name,
    seconds,
):

    demo = DEMO_GAMES[case_name]

    print(
        f"Showing demo: {case_name}"
    )

    display.show_game(
        demo["sport"],
        demo["game"],
        seconds=seconds,
    )


def run_all(
    display,
    seconds,
):

    for case_name in DEMO_GAMES:

        show_case(
            display,
            case_name,
            seconds,
        )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Sports ticker display demo"
        )
    )

    parser.add_argument(
        "case",
        nargs="?",
        default="all",
        choices=[
            "all",
            *DEMO_GAMES.keys(),
        ],
        help="Demo case to display",
    )

    parser.add_argument(
        "--seconds",
        type=float,
        default=8,
        help=(
            "Seconds to display each demo"
        ),
    )

    parser.add_argument(
        "--loop",
        action="store_true",
        help=(
            "Continuously loop through demos"
        ),
    )

    args = parser.parse_args()

    display = ScoreboardDisplay()

    if args.loop:

        while True:

            if args.case == "all":

                run_all(
                    display,
                    args.seconds,
                )

            else:

                show_case(
                    display,
                    args.case,
                    args.seconds,
                )

    else:

        if args.case == "all":

            run_all(
                display,
                args.seconds,
            )

        else:

            show_case(
                display,
                args.case,
                args.seconds,
            )


if __name__ == "__main__":
    main()