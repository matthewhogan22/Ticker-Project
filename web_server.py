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


@app.route("/")
def index():

    settings = (
        load_settings()
    )

    return render_template(
        "index.html",
        settings=settings
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
    # DISPLAY OPTIONS
    # ---------------------------------------------

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