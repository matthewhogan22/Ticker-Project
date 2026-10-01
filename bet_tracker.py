from sports_odds import (
    SportsOddsError,
    get_event,
    safe_float,
)


def get_event_scores(
    event
):

    scores = event.get(
        "scores",
        {}
    ) or {}

    home = safe_float(
        scores.get(
            "home"
        )
    )

    away = safe_float(
        scores.get(
            "away"
        )
    )

    # Fallback to team score fields.
    teams = event.get(
        "teams",
        {}
    ) or {}

    if home is None:

        home = safe_float(
            (
                teams.get(
                    "home",
                    {}
                )
                or {}
            ).get(
                "score"
            )
        )

    if away is None:

        away = safe_float(
            (
                teams.get(
                    "away",
                    {}
                )
                or {}
            ).get(
                "score"
            )
        )

    return home, away


def format_number(
    value
):

    if value is None:
        return ""

    if float(
        value
    ).is_integer():

        return str(
            int(
                value
            )
        )

    return (
        f"{value:.1f}"
    )


def progress_result(
    state,
    message,
    value=None,
    final=False
):

    return {
        "state":
            state,

        "message":
            message,

        "value":
            value,

        "final":
            final,
    }


def calculate_spread(
    bet,
    event,
    final
):

    home_score, away_score = (
        get_event_scores(
            event
        )
    )

    if (
        home_score is None
        or away_score is None
    ):

        return progress_result(
            "pending",
            "Waiting for score"
        )

    line = safe_float(
        bet.get(
            "line"
        )
    )

    if line is None:

        return progress_result(
            "error",
            "Missing spread"
        )

    side = bet.get(
        "side"
    )

    if side == "home":

        selected_score = home_score
        opponent_score = away_score

    elif side == "away":

        selected_score = away_score
        opponent_score = home_score

    else:

        return progress_result(
            "error",
            "Invalid spread side"
        )

    margin = (
        selected_score
        - opponent_score
        + line
    )

    amount = abs(
        margin
    )

    amount_text = format_number(
        amount
    )

    if final:

        if margin > 0:

            return progress_result(
                "win",
                "WIN",
                margin,
                True
            )

        if margin < 0:

            return progress_result(
                "loss",
                "LOSS",
                margin,
                True
            )

        return progress_result(
            "push",
            "PUSH",
            0,
            True
        )

    if margin > 0:

        return progress_result(
            "winning",
            f"COVERING +{amount_text}",
            margin
        )

    if margin < 0:

        return progress_result(
            "losing",
            f"BEHIND LINE {amount_text}",
            margin
        )

    return progress_result(
        "push",
        "ON THE NUMBER",
        0
    )


def calculate_moneyline(
    bet,
    event,
    final
):

    home_score, away_score = (
        get_event_scores(
            event
        )
    )

    if (
        home_score is None
        or away_score is None
    ):

        return progress_result(
            "pending",
            "Waiting for score"
        )

    side = bet.get(
        "side"
    )

    if side == "home":

        selected_score = home_score
        opponent_score = away_score

    elif side == "away":

        selected_score = away_score
        opponent_score = home_score

    else:

        return progress_result(
            "error",
            "Invalid moneyline side"
        )

    difference = (
        selected_score
        - opponent_score
    )

    if final:

        if difference > 0:

            return progress_result(
                "win",
                "WIN",
                difference,
                True
            )

        if difference < 0:

            return progress_result(
                "loss",
                "LOSS",
                difference,
                True
            )

        return progress_result(
            "push",
            "TIE",
            0,
            True
        )

    if difference > 0:

        return progress_result(
            "winning",
            "WINNING",
            difference
        )

    if difference < 0:

        return progress_result(
            "losing",
            "TRAILING",
            difference
        )

    return progress_result(
        "push",
        "TIED",
        0
    )


def calculate_total(
    bet,
    event,
    final
):

    home_score, away_score = (
        get_event_scores(
            event
        )
    )

    if (
        home_score is None
        or away_score is None
    ):

        return progress_result(
            "pending",
            "Waiting for score"
        )

    line = safe_float(
        bet.get(
            "line"
        )
    )

    if line is None:

        return progress_result(
            "error",
            "Missing total"
        )

    actual = (
        home_score
        + away_score
    )

    side = bet.get(
        "side"
    )

    if side == "over":

        margin = (
            actual
            - line
        )

    elif side == "under":

        margin = (
            line
            - actual
        )

    else:

        return progress_result(
            "error",
            "Invalid total side"
        )

    if final:

        if margin > 0:

            return progress_result(
                "win",
                "WIN",
                actual,
                True
            )

        if margin < 0:

            return progress_result(
                "loss",
                "LOSS",
                actual,
                True
            )

        return progress_result(
            "push",
            "PUSH",
            actual,
            True
        )

    actual_text = format_number(
        actual
    )

    if side == "over":

        if actual > line:

            return progress_result(
                "winning",
                (
                    f"OVER BY "
                    f"{format_number(actual - line)}"
                ),
                actual
            )

        needed = (
            line
            - actual
        )

        return progress_result(
            "losing",
            (
                f"TOTAL {actual_text} - "
                f"NEEDS "
                f"{format_number(needed)}"
            ),
            actual
        )

    cushion = (
        line
        - actual
    )

    if cushion > 0:

        return progress_result(
            "winning",
            (
                f"TOTAL {actual_text} - "
                f"CUSHION "
                f"{format_number(cushion)}"
            ),
            actual
        )

    if cushion < 0:

        return progress_result(
            "losing",
            (
                f"OVER BY "
                f"{format_number(abs(cushion))}"
            ),
            actual
        )

    return progress_result(
        "push",
        "ON THE NUMBER",
        actual
    )


def calculate_player_prop(
    bet,
    event,
    market,
    final
):

    line = safe_float(
        bet.get(
            "line"
        )
    )

    if line is None:

        return progress_result(
            "error",
            "Missing prop line"
        )

    actual = safe_float(
        market.get(
            "score"
        )
    )

    if actual is None:

        return progress_result(
            "pending",
            "Waiting for stat"
        )

    side = bet.get(
        "side"
    )

    if side == "over":

        margin = (
            actual
            - line
        )

    elif side == "under":

        margin = (
            line
            - actual
        )

    else:

        return progress_result(
            "error",
            "Invalid prop side"
        )

    if final:

        if margin > 0:

            return progress_result(
                "win",
                "WIN",
                actual,
                True
            )

        if margin < 0:

            return progress_result(
                "loss",
                "LOSS",
                actual,
                True
            )

        return progress_result(
            "push",
            "PUSH",
            actual,
            True
        )

    if margin > 0:

        return progress_result(
            "winning",
            (
                f"{format_number(actual)} - "
                f"AHEAD "
                f"{format_number(margin)}"
            ),
            actual
        )

    if margin < 0:

        return progress_result(
            "losing",
            (
                f"{format_number(actual)} - "
                f"NEEDS "
                f"{format_number(abs(margin))}"
            ),
            actual
        )

    return progress_result(
        "push",
        (
            f"{format_number(actual)} - "
            f"ON LINE"
        ),
        actual
    )


def get_bet_progress(
    bet
):
    """
    Fetch one bet's event/market and calculate
    its current progress.
    """

    event_id = bet.get(
        "event_id"
    )

    odd_id = bet.get(
        "odd_id"
    )

    if (
        not event_id
        or not odd_id
    ):

        return progress_result(
            "error",
            "Bet is missing event/market information"
        )

    try:

        event = get_event(
            event_id,
            odd_id=odd_id,
            expand_results=True
        )

    except SportsOddsError as exc:

        return progress_result(
            "error",
            str(
                exc
            )
        )

    if not event:

        return progress_result(
            "error",
            "Event not found"
        )

    status = event.get(
        "status",
        {}
    ) or {}

    if status.get(
        "cancelled",
        False
    ):

        return progress_result(
            "void",
            "EVENT CANCELLED",
            final=True
        )

    if not status.get(
        "started",
        False
    ):

        return progress_result(
            "pending",
            "GAME NOT STARTED"
        )

    final = bool(
        status.get(
            "finalized",
            False
        )
        or status.get(
            "ended",
            False
        )
    )

    market = (
        event.get(
            "odds",
            {}
        )
        or {}
    ).get(
        odd_id,
        {}
    ) or {}

    if market.get(
        "cancelled",
        False
    ):

        return progress_result(
            "void",
            "BET VOID",
            final=True
        )

    bet_type = bet.get(
        "bet_type"
    )

    if bet_type == "spread":

        return calculate_spread(
            bet,
            event,
            final
        )

    if bet_type == "moneyline":

        return calculate_moneyline(
            bet,
            event,
            final
        )

    if bet_type == "total":

        return calculate_total(
            bet,
            event,
            final
        )

    if bet_type == "player_prop":

        return calculate_player_prop(
            bet,
            event,
            market,
            final
        )

    return progress_result(
        "error",
        "Unknown bet type"
    )