import os
from datetime import (
    datetime,
    timedelta,
    timezone,
)

import requests


# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------

BASE_URL = (
    "https://api.sportsgameodds.com/v2"
)

API_KEY_ENV = (
    "SPORTSGAMEODDS_API_KEY"
)

REQUEST_TIMEOUT = 15


class SportsOddsError(
    RuntimeError
):
    pass


# ---------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------


def get_api_key():

    api_key = os.environ.get(
        API_KEY_ENV,
        ""
    ).strip()

    if not api_key:

        raise SportsOddsError(
            "SPORTSGAMEODDS_API_KEY is not configured."
        )

    return api_key


def api_get(
    path,
    params=None
):

    url = (
        f"{BASE_URL}/{path.lstrip('/')}"
    )

    headers = {
        "x-api-key":
            get_api_key()
    }

    response = requests.get(
        url,
        params=params or {},
        headers=headers,
        timeout=REQUEST_TIMEOUT
    )

    try:

        response.raise_for_status()

    except requests.HTTPError as exc:

        message = (
            f"SportsGameOdds request failed "
            f"with HTTP {response.status_code}."
        )

        try:

            payload = response.json()

            if payload:
                message = (
                    f"{message} {payload}"
                )

        except ValueError:
            pass

        raise SportsOddsError(
            message
        ) from exc

    try:

        payload = response.json()

    except ValueError as exc:

        raise SportsOddsError(
            "SportsGameOdds returned invalid JSON."
        ) from exc

    return payload


def get_response_data(
    payload
):

    data = payload.get(
        "data",
        []
    )

    if isinstance(
        data,
        list
    ):
        return data

    return []


def get_team_name(
    team,
    short=False
):

    if not team:
        return ""

    names = team.get(
        "names",
        {}
    ) or {}

    if short:

        return (
            names.get(
                "short"
            )
            or names.get(
                "medium"
            )
            or names.get(
                "long"
            )
            or team.get(
                "name"
            )
            or ""
        )

    return (
        names.get(
            "long"
        )
        or names.get(
            "medium"
        )
        or team.get(
            "name"
        )
        or names.get(
            "short"
        )
        or ""
    )


def safe_float(
    value
):

    if value in (
        None,
        ""
    ):
        return None

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError
    ):
        return None


def prettify_stat(
    stat_id
):

    if not stat_id:
        return ""

    overrides = {
        "passing_yards":
            "Passing Yards",

        "rushing_yards":
            "Rushing Yards",

        "receiving_yards":
            "Receiving Yards",

        "receptions":
            "Receptions",

        "passing_touchdowns":
            "Passing TDs",

        "rushing_touchdowns":
            "Rushing TDs",

        "receiving_touchdowns":
            "Receiving TDs",

        "rebounds":
            "Rebounds",

        "assists":
            "Assists",

        "steals":
            "Steals",

        "blocks":
            "Blocks",

        "points":
            "Points",
    }

    if stat_id in overrides:

        return overrides[
            stat_id
        ]

    return (
        stat_id
        .replace(
            "_",
            " "
        )
        .title()
    )


def iso_sort_value(
    value
):

    if not value:

        return datetime.max.replace(
            tzinfo=timezone.utc
        )

    try:

        return datetime.fromisoformat(
            value.replace(
                "Z",
                "+00:00"
            )
        )

    except ValueError:

        return datetime.max.replace(
            tzinfo=timezone.utc
        )


# ---------------------------------------------------------
# EVENTS
# ---------------------------------------------------------


def get_events(
    league_id,
    limit=50
):

    league_id = (
        league_id
        .strip()
        .upper()
    )

    now = datetime.now(
        timezone.utc
    )

    starts_after = (
        now
        .isoformat()
        .replace(
            "+00:00",
            "Z"
        )
    )

    starts_before = (
        now
        .replace(
            hour=23,
            minute=59,
            second=59,
            microsecond=0
        )
        + timedelta(
            days=14
        )
    )

    starts_before = (
        starts_before
        .isoformat()
        .replace(
            "+00:00",
            "Z"
        )
    )

    payload = api_get(
        "events",
        {
            "leagueID":
                league_id,

            "oddsAvailable":
                "true",

            "ended":
                "false",

            "cancelled":
                "false",

            "startsAfter":
                starts_after,

            "startsBefore":
                starts_before,

            "limit":
                limit,
        }
    )

    events = get_response_data(
        payload
    )

    events.sort(
        key=lambda event:
            iso_sort_value(
                (
                    event.get(
                        "status",
                        {}
                    )
                    or {}
                ).get(
                    "startsAt"
                )
            )
    )

    return events


def get_event(
    event_id,
    odd_id=None,
    expand_results=True
):

    params = {
        "eventID":
            event_id,

        "expandResults":
            str(
                bool(
                    expand_results
                )
            ).lower(),
    }

    if odd_id:

        params[
            "oddID"
        ] = odd_id

    payload = api_get(
        "events",
        params
    )

    events = get_response_data(
        payload
    )

    if not events:

        return None

    return events[0]


def serialize_event_option(
    event
):

    teams = event.get(
        "teams",
        {}
    ) or {}

    away = teams.get(
        "away",
        {}
    ) or {}

    home = teams.get(
        "home",
        {}
    ) or {}

    status = event.get(
        "status",
        {}
    ) or {}

    away_long = get_team_name(
        away
    )

    home_long = get_team_name(
        home
    )

    away_short = get_team_name(
        away,
        short=True
    )

    home_short = get_team_name(
        home,
        short=True
    )

    return {
        "event_id":
            event.get(
                "eventID",
                ""
            ),

        "league":
            event.get(
                "leagueID",
                ""
            ),

        "away_name":
            away_long,

        "home_name":
            home_long,

        "away_short":
            away_short,

        "home_short":
            home_short,

        "away_team_id":
            away.get(
                "teamID",
                ""
            ),

        "home_team_id":
            home.get(
                "teamID",
                ""
            ),

        "starts_at":
            status.get(
                "startsAt",
                ""
            ),

        "started":
            bool(
                status.get(
                    "started",
                    False
                )
            ),

        "ended":
            bool(
                status.get(
                    "ended",
                    False
                )
            ),

        "finalized":
            bool(
                status.get(
                    "finalized",
                    False
                )
            ),

        "status":
            (
                status.get(
                    "displayLong"
                )
                or status.get(
                    "displayShort"
                )
                or ""
            ),

        "display_name":
            (
                f"{away_long} @ "
                f"{home_long}"
            ),
    }


def get_event_options(
    league_id
):

    return [
        serialize_event_option(
            event
        )
        for event in get_events(
            league_id
        )
    ]


# ---------------------------------------------------------
# MARKET NORMALIZATION
# ---------------------------------------------------------


def get_market_category(
    odd
):

    stat_id = odd.get(
        "statID",
        ""
    )

    entity_id = odd.get(
        "statEntityID",
        ""
    )

    bet_type = odd.get(
        "betTypeID",
        ""
    )

    period_id = odd.get(
        "periodID",
        ""
    )

    # First version only tracks full-game bets.
    if period_id != "game":

        return None

    if (
        stat_id == "points"
        and bet_type == "ml"
        and entity_id in {
            "home",
            "away"
        }
    ):
        return "moneyline"

    if (
        stat_id == "points"
        and bet_type == "sp"
        and entity_id in {
            "home",
            "away"
        }
    ):
        return "spread"

    if (
        stat_id == "points"
        and bet_type == "ou"
        and entity_id == "all"
    ):
        return "total"

    if (
        bet_type == "ou"
        and entity_id
        not in {
            "",
            "home",
            "away",
            "all"
        }
    ):
        return "player_prop"

    return None


def get_consensus_line(
    odd,
    category
):

    if category == "spread":

        candidates = (
            "bookSpread",
            "fairSpread",
            "spread"
        )

    elif category in {
        "total",
        "player_prop"
    }:

        candidates = (
            "bookOverUnder",
            "fairOverUnder",
            "overUnder"
        )

    else:

        return None

    for key in candidates:

        value = safe_float(
            odd.get(
                key
            )
        )

        if value is not None:
            return value

    # Fallback: use the first bookmaker line
    # only for display assistance.
    by_bookmaker = odd.get(
        "byBookmaker",
        {}
    ) or {}

    for bookmaker in (
        by_bookmaker.values()
    ):

        if not isinstance(
            bookmaker,
            dict
        ):
            continue

        if category == "spread":

            value = safe_float(
                bookmaker.get(
                    "spread"
                )
            )

        else:

            value = safe_float(
                bookmaker.get(
                    "overUnder"
                )
            )

        if value is not None:
            return value

    return None


def get_consensus_odds(
    odd
):

    for key in (
        "bookOdds",
        "fairOdds",
        "odds"
    ):

        value = odd.get(
            key
        )

        if value not in (
            None,
            ""
        ):
            return str(
                value
            )

    return ""


def build_market_label(
    odd,
    category,
    home_name,
    away_name,
    players
):

    side = odd.get(
        "sideID",
        ""
    )

    entity_id = odd.get(
        "statEntityID",
        ""
    )

    stat_id = odd.get(
        "statID",
        ""
    )

    current_line = get_consensus_line(
        odd,
        category
    )

    if category == "moneyline":

        if side == "home":
            return f"{home_name} Moneyline"

        return f"{away_name} Moneyline"

    if category == "spread":

        team_name = (
            home_name
            if side == "home"
            else away_name
        )

        if current_line is None:
            return f"{team_name} Spread"

        line_text = (
            f"+{current_line:g}"
            if current_line > 0
            else f"{current_line:g}"
        )

        return (
            f"{team_name} {line_text}"
        )

    if category == "total":

        side_name = (
            side.title()
        )

        if current_line is None:
            return (
                f"Game Total {side_name}"
            )

        return (
            f"{side_name} "
            f"{current_line:g}"
        )

    if category == "player_prop":

        player = players.get(
            entity_id,
            {}
        ) or {}

        player_name = (
            player.get(
                "name"
            )
            or (
                (
                    player.get(
                        "firstName",
                        ""
                    )
                    + " "
                    + player.get(
                        "lastName",
                        ""
                    )
                ).strip()
            )
            or entity_id
        )

        stat_name = prettify_stat(
            stat_id
        )

        side_name = (
            side.title()
        )

        if current_line is None:

            return (
                f"{player_name} - "
                f"{stat_name} "
                f"{side_name}"
            )

        return (
            f"{player_name} - "
            f"{stat_name} "
            f"{side_name} "
            f"{current_line:g}"
        )

    return odd.get(
        "oddID",
        ""
    )


def get_market_options(
    event_id
):

    event = get_event(
        event_id,
        expand_results=False
    )

    if not event:
        return []

    teams = event.get(
        "teams",
        {}
    ) or {}

    home = teams.get(
        "home",
        {}
    ) or {}

    away = teams.get(
        "away",
        {}
    ) or {}

    home_name = get_team_name(
        home
    )

    away_name = get_team_name(
        away
    )

    players = event.get(
        "players",
        {}
    ) or {}

    odds = event.get(
        "odds",
        {}
    ) or {}

    markets = []

    for (
        odd_id,
        odd
    ) in odds.items():

        if not isinstance(
            odd,
            dict
        ):
            continue

        category = get_market_category(
            odd
        )

        if category is None:
            continue

        side = odd.get(
            "sideID",
            ""
        )

        stat_entity_id = odd.get(
            "statEntityID",
            ""
        )

        selection = ""

        if category in {
            "spread",
            "moneyline"
        }:

            selection = (
                home_name
                if side == "home"
                else away_name
            )

        elif category == "total":

            selection = (
                f"{side.title()} "
                f"Game Total"
            )

        elif category == "player_prop":

            player = players.get(
                stat_entity_id,
                {}
            ) or {}

            selection = (
                player.get(
                    "name"
                )
                or stat_entity_id
            )

        bookmaker_ids = sorted(
            (
                odd.get(
                    "byBookmaker",
                    {}
                )
                or {}
            ).keys()
        )

        markets.append(
            {
                "odd_id":
                    odd_id,

                "category":
                    category,

                "label":
                    build_market_label(
                        odd,
                        category,
                        home_name,
                        away_name,
                        players
                    ),

                "selection":
                    selection,

                "side":
                    side,

                "stat_id":
                    odd.get(
                        "statID",
                        ""
                    ),

                "stat_name":
                    prettify_stat(
                        odd.get(
                            "statID",
                            ""
                        )
                    ),

                "stat_entity_id":
                    stat_entity_id,

                "current_line":
                    get_consensus_line(
                        odd,
                        category
                    ),

                "current_odds":
                    get_consensus_odds(
                        odd
                    ),

                "bookmakers":
                    bookmaker_ids,

                "scoring_supported":
                    bool(
                        odd.get(
                            "scoringSupported",
                            False
                        )
                    ),
            }
        )

    category_order = {
        "spread": 0,
        "moneyline": 1,
        "total": 2,
        "player_prop": 3,
    }

    markets.sort(
        key=lambda market: (
            category_order.get(
                market[
                    "category"
                ],
                99
            ),
            market[
                "label"
            ].lower()
        )
    )

    return markets