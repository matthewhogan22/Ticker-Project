import copy
import json
import os
import tempfile
import uuid


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

SETTINGS_FILE = os.path.join(
    BASE_DIR,
    "settings.json"
)


DEFAULT_SETTINGS = {
    "sports": {
        "nfl": True,
        "ncaaf": True,
        "nba": True,
        "mlb": True,
    },

    "favorites": {
        "nfl": {
            "mode": "all",
            "teams": [],
        },
        "ncaaf": {
            "mode": "all",
            "teams": [],
        },
        "nba": {
            "mode": "all",
            "teams": [],
        },
        "mlb": {
            "mode": "all",
            "teams": [],
        },
    },

    "display": {
        "seconds_per_game": 8,
        "game_filter": "live_upcoming",
    },

    "tracked_bets": [],
}


def load_settings():
    """
    Read settings.json.

    If the file does not exist or contains invalid JSON,
    return the default settings instead.
    """

    if not os.path.exists(
        SETTINGS_FILE
    ):
        save_settings(
            DEFAULT_SETTINGS
        )

        return copy.deepcopy(
            DEFAULT_SETTINGS
        )

    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            settings = json.load(
                file
            )

    except (
        json.JSONDecodeError,
        OSError
    ):
        return copy.deepcopy(
            DEFAULT_SETTINGS
        )

    # ---------------------------------------------
    # REQUIRED SECTIONS
    # ---------------------------------------------

    settings.setdefault(
        "sports",
        {}
    )

    settings.setdefault(
        "display",
        {}
    )

    settings.setdefault(
        "favorites",
        {}
    )

    settings.setdefault(
        "tracked_bets",
        []
    )

    # ---------------------------------------------
    # SPORTS
    # ---------------------------------------------

    for (
        sport,
        default_value
    ) in DEFAULT_SETTINGS[
        "sports"
    ].items():

        settings[
            "sports"
        ].setdefault(
            sport,
            default_value
        )

    # ---------------------------------------------
    # FAVORITES
    # ---------------------------------------------

    for (
        sport,
        default_value
    ) in DEFAULT_SETTINGS[
        "favorites"
    ].items():

        settings[
            "favorites"
        ].setdefault(
            sport,
            copy.deepcopy(
                default_value
            )
        )

        settings[
            "favorites"
        ][
            sport
        ].setdefault(
            "mode",
            default_value[
                "mode"
            ]
        )

        settings[
            "favorites"
        ][
            sport
        ].setdefault(
            "teams",
            copy.deepcopy(
                default_value[
                    "teams"
                ]
            )
        )

    # ---------------------------------------------
    # DISPLAY
    # ---------------------------------------------

    settings[
        "display"
    ].setdefault(
        "seconds_per_game",
        DEFAULT_SETTINGS[
            "display"
        ][
            "seconds_per_game"
        ]
    )

    settings[
        "display"
    ].setdefault(
        "game_filter",
        DEFAULT_SETTINGS[
            "display"
        ][
            "game_filter"
        ]
    )

    return settings


def save_settings(
    settings
):
    """
    Save settings safely.

    A temporary file is written first and then replaces
    settings.json. This prevents the ticker from reading
    the file halfway through a web-server write.
    """

    directory = os.path.dirname(
        SETTINGS_FILE
    )

    os.makedirs(
        directory,
        exist_ok=True
    )

    fd, temp_path = tempfile.mkstemp(
        dir=directory,
        prefix="settings_",
        suffix=".json"
    )

    try:

        with os.fdopen(
            fd,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                settings,
                file,
                indent=4
            )

        os.replace(
            temp_path,
            SETTINGS_FILE
        )

    finally:

        if os.path.exists(
            temp_path
        ):
            os.remove(
                temp_path
            )


# ---------------------------------------------------------
# TRACKED BETS
# ---------------------------------------------------------


def get_tracked_bets():
    """
    Return all saved tracked bets.
    """

    settings = load_settings()

    return copy.deepcopy(
        settings.get(
            "tracked_bets",
            []
        )
    )


def get_active_bets():
    """
    Return bets which have not been manually disabled.
    """

    return [
        bet
        for bet in get_tracked_bets()
        if bet.get(
            "active",
            True
        )
    ]


def get_tracked_bet(
    bet_id
):
    """
    Return one bet by ID.
    """

    for bet in get_tracked_bets():

        if bet.get(
            "id"
        ) == bet_id:

            return bet

    return None


def add_tracked_bet(
    bet
):
    """
    Add a bet and assign an ID.
    """

    settings = load_settings()

    stored_bet = copy.deepcopy(
        bet
    )

    stored_bet[
        "id"
    ] = str(
        uuid.uuid4()
    )

    stored_bet.setdefault(
        "active",
        True
    )

    settings[
        "tracked_bets"
    ].append(
        stored_bet
    )

    save_settings(
        settings
    )

    return copy.deepcopy(
        stored_bet
    )


def update_tracked_bet(
    bet_id,
    updates
):
    """
    Update an existing tracked bet.
    """

    settings = load_settings()

    for bet in settings.get(
        "tracked_bets",
        []
    ):

        if bet.get(
            "id"
        ) != bet_id:

            continue

        bet.update(
            copy.deepcopy(
                updates
            )
        )

        # Never allow the bet ID itself to change.
        bet[
            "id"
        ] = bet_id

        save_settings(
            settings
        )

        return copy.deepcopy(
            bet
        )

    return None


def delete_tracked_bet(
    bet_id
):
    """
    Delete one tracked bet.
    """

    settings = load_settings()

    original_count = len(
        settings.get(
            "tracked_bets",
            []
        )
    )

    settings[
        "tracked_bets"
    ] = [
        bet
        for bet in settings.get(
            "tracked_bets",
            []
        )
        if bet.get(
            "id"
        ) != bet_id
    ]

    if (
        len(
            settings[
                "tracked_bets"
            ]
        )
        == original_count
    ):
        return False

    save_settings(
        settings
    )

    return True