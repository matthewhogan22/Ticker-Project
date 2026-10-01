import copy
import json
import os
import tempfile


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    }
}


def load_settings():
    """
    Read settings.json.

    If the file does not exist or contains invalid JSON,
    return the default settings instead.
    """

    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return copy.deepcopy(
            DEFAULT_SETTINGS
        )

    try:
        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            settings = json.load(file)

    except (
        json.JSONDecodeError,
        OSError
    ):
        return copy.deepcopy(
            DEFAULT_SETTINGS
        )

    # Make sure required sections exist.
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

    # Make sure every sport has a value.
    for sport, default_value in DEFAULT_SETTINGS["sports"].items():

        settings["sports"].setdefault(
            sport,
            default_value
        )

    # Make sure every sport has favorite settings.
    for sport, default_value in DEFAULT_SETTINGS["favorites"].items():

        settings["favorites"].setdefault(
            sport,
            copy.deepcopy(default_value)
        )

        settings["favorites"][sport].setdefault(
            "mode",
            default_value["mode"]
        )

        settings["favorites"][sport].setdefault(
            "teams",
            copy.deepcopy(
                default_value["teams"]
            )
        )

    settings["display"].setdefault(
        "seconds_per_game",
        DEFAULT_SETTINGS["display"]["seconds_per_game"]
    )

    settings["display"].setdefault(
        "game_filter",
        DEFAULT_SETTINGS["display"]["game_filter"]
    )

    return settings


def save_settings(settings):
    """
    Save settings safely.

    A temporary file is written first and then replaces
    settings.json. This prevents main.py from reading the
    file halfway through a web-server write.
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

        if os.path.exists(temp_path):
            os.remove(temp_path)