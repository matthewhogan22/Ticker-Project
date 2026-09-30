import os
import time

from datetime import datetime
from zoneinfo import ZoneInfo


try:

    from rgbmatrix import (
        RGBMatrix,
        RGBMatrixOptions,
        graphics
    )

    RGB_MATRIX_AVAILABLE = True

except ImportError:

    RGB_MATRIX_AVAILABLE = False


# ---------------------------------------------------------
# GENERAL CONSTANTS
# ---------------------------------------------------------

EASTERN = ZoneInfo(
    "America/New_York"
)


# ---------------------------------------------------------
# COLOR HELPERS
# ---------------------------------------------------------

def hex_to_rgb(
    hex_color
):

    if not hex_color:

        return (
            255,
            255,
            255
        )

    hex_color = (
        str(hex_color)
        .replace("#", "")
        .strip()
    )

    if len(hex_color) != 6:

        return (
            255,
            255,
            255
        )

    try:

        return tuple(

            int(
                hex_color[
                    i:i + 2
                ],
                16
            )

            for i in (
                0,
                2,
                4
            )
        )

    except ValueError:

        return (
            255,
            255,
            255
        )


def readable_team_rgb(
    hex_color
):

    r, g, b = hex_to_rgb(
        hex_color
    )

    # Perceived brightness.
    #
    # Dark team colors such as black,
    # navy, dark green, etc. are difficult
    # or impossible to see on the black
    # LED matrix background.

    brightness = (
        (r * 299)
        + (g * 587)
        + (b * 114)
    ) / 1000

    if brightness < 75:

        return (
            255,
            255,
            255
        )

    return (
        r,
        g,
        b
    )


# ---------------------------------------------------------
# GAME TIME FORMATTING
# ---------------------------------------------------------

def parse_start_time(
    game
):

    raw_start = game.get(
        "start_time",
        ""
    )

    if not raw_start:
        return None

    try:

        start_utc = datetime.fromisoformat(
            raw_start.replace(
                "Z",
                "+00:00"
            )
        )

        return start_utc.astimezone(
            EASTERN
        )

    except (
        ValueError,
        TypeError
    ):

        return None


def format_clock_time(
    dt
):

    # %-I removes the leading zero on Linux:
    #
    # 08:15 PM -> 8:15p

    return (
        dt.strftime(
            "%-I:%M%p"
        )
        .lower()
        .replace(
            "pm",
            "p"
        )
        .replace(
            "am",
            "a"
        )
    )


def format_upcoming_game(
    game
):

    start = parse_start_time(
        game
    )

    if start is None:

        return game.get(
            "short_status",
            game.get(
                "status",
                ""
            )
        )

    now = datetime.now(
        EASTERN
    )

    time_text = format_clock_time(
        start
    )

    # Today:
    #
    # 8:15p

    if (
        start.date()
        == now.date()
    ):

        return time_text

    # Tomorrow or later:
    #
    # 10/01 8:15p

    date_text = start.strftime(
        "%m/%d"
    )

    return (
        f"{date_text} "
        f"{time_text}"
    )


# ---------------------------------------------------------
# FONT LOCATION
# ---------------------------------------------------------

def find_font(
    filename
):

    # We moved these here because the RGB
    # matrix application is running as root
    # and we want a predictable system-wide
    # font location.

    font_path = (
        "/usr/local/share/"
        "sports-ticker/fonts/"
        f"{filename}"
    )

    if not os.path.isfile(
        font_path
    ):

        raise FileNotFoundError(
            "Could not find RGB matrix font: "
            f"{font_path}"
        )

    return font_path


# ---------------------------------------------------------
# SCOREBOARD DISPLAY
# ---------------------------------------------------------

class ScoreboardDisplay:

    def __init__(
        self,
        brightness=30
    ):

        self.console_mode = (
            not RGB_MATRIX_AVAILABLE
        )

        if self.console_mode:

            print(
                "rgbmatrix library not found."
            )

            print(
                "Running in console mode."
            )

            return

        # -------------------------------------------------
        # MATRIX SETTINGS
        # -------------------------------------------------

        options = RGBMatrixOptions()

        options.rows = 32

        options.cols = 64

        options.chain_length = 1

        options.parallel = 1

        options.hardware_mapping = (
            "adafruit-hat"
        )

        # Value proven to work on your Pi 4.
        options.gpio_slowdown = 4

        options.brightness = (
            brightness
        )

        # Required for this current project layout
        # because main.py/settings.json live in the
        # user's home directory.
        options.drop_privileges = False

        self.matrix = RGBMatrix(
            options=options
        )

        self.canvas = (
            self.matrix
            .CreateFrameCanvas()
        )

        # -------------------------------------------------
        # FONTS
        # -------------------------------------------------

        self.font = graphics.Font()

        self.font.LoadFont(
            find_font(
                "6x10.bdf"
            )
        )

        self.small_font = (
            graphics.Font()
        )

        self.small_font.LoadFont(
            find_font(
                "4x6.bdf"
            )
        )

        # -------------------------------------------------
        # STANDARD COLORS
        # -------------------------------------------------

        self.white = graphics.Color(
            255,
            255,
            255
        )

        self.gray = graphics.Color(
            130,
            130,
            130
        )

        self.dim_gray = graphics.Color(
            80,
            80,
            80
        )

        self.yellow = graphics.Color(
            255,
            220,
            0
        )

        self.green = graphics.Color(
            0,
            255,
            80
        )


    # -----------------------------------------------------
    # BASIC HELPERS
    # -----------------------------------------------------

    def get_color(
        self,
        hex_color
    ):

        rgb = readable_team_rgb(
            hex_color
        )

        return graphics.Color(
            *rgb
        )


    def shorten(
        self,
        value,
        length
    ):

        value = str(
            value or ""
        )

        if len(value) <= length:
            return value

        return value[:length]


    def draw_text(
        self,
        font,
        x,
        y,
        color,
        text
    ):

        graphics.DrawText(
            self.canvas,
            font,
            x,
            y,
            color,
            str(text)
        )


    def swap(
        self
    ):

        self.canvas = (
            self.matrix
            .SwapOnVSync(
                self.canvas
            )
        )


    def pause_frame(
        self,
        seconds
    ):

        end_time = (
            time.time()
            + seconds
        )

        while (
            time.time()
            < end_time
        ):

            time.sleep(
                0.05
            )


    # -----------------------------------------------------
    # GENERIC GAME DISPATCH
    # -----------------------------------------------------

    def show_game(
        self,
        sport,
        game,
        seconds=8
    ):

        if self.console_mode:

            print(
                "\n"
                f"[{sport.upper()}] "
                f"{game['away_team']} "
                f"{game['away_score']} "
                f"@ "
                f"{game['home_team']} "
                f"{game['home_score']} "
                f"| "
                f"{game['short_status']}"
            )

            time.sleep(
                min(
                    seconds,
                    2
                )
            )

            return

        sport = sport.lower()

        if sport in (
            "nfl",
            "ncaaf"
        ):

            self.show_football_game(
                sport,
                game,
                seconds
            )

        elif sport == "nba":

            self.show_basketball_game(
                game,
                seconds
            )

        elif sport == "mlb":

            self.show_baseball_game(
                game,
                seconds
            )

        else:

            self.show_generic_game(
                sport,
                game,
                seconds
            )


    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    def draw_header(
        self,
        league,
        text
    ):

        league = self.shorten(
            league.upper(),
            5
        )

        text = self.shorten(
            text,
            12
        )

        self.draw_text(
            self.small_font,
            1,
            6,
            self.white,
            league
        )

        # League labels have different widths.
        if league == "NCAAF":

            x = 23

        elif league == "MLB":

            x = 17

        elif league == "NBA":

            x = 17

        else:

            x = 17

        self.draw_text(
            self.small_font,
            x,
            6,
            self.gray,
            text
        )


    # -----------------------------------------------------
    # TEAM LINE
    # -----------------------------------------------------

    def draw_team_line(
        self,
        y,
        team,
        score,
        record,
        color,
        show_score=True
    ):

        team = self.shorten(
            team,
            4
        )

        record = self.shorten(
            record,
            7
        )

        self.draw_text(
            self.font,
            1,
            y,
            color,
            team
        )

        if show_score:

            score_text = str(
                score
            )

            # Right-ish aligned scoring area.
            score_x = (
                58
                - (
                    len(score_text)
                    * 6
                )
            )

            self.draw_text(
                self.font,
                score_x,
                y,
                self.white,
                score_text
            )

        else:

            self.draw_text(
                self.small_font,
                34,
                y - 2,
                self.gray,
                record
            )


    # -----------------------------------------------------
    # FOOTBALL
    # -----------------------------------------------------

    def show_football_game(
        self,
        sport,
        game,
        seconds
    ):

        state = game.get(
            "state",
            ""
        )

        away_color = self.get_color(
            game.get(
                "away_color"
            )
        )

        home_color = self.get_color(
            game.get(
                "home_color"
            )
        )

        self.canvas.Clear()

        # ---------------------------------------------
        # UPCOMING FOOTBALL
        # ---------------------------------------------

        if state == "pre":

            header = format_upcoming_game(
                game
            )

            self.draw_header(
                sport,
                header
            )

            self.draw_team_line(
                17,
                game.get(
                    "away_team",
                    ""
                ),
                "",
                game.get(
                    "away_record",
                    ""
                ),
                away_color,
                show_score=False
            )

            self.draw_team_line(
                29,
                game.get(
                    "home_team",
                    ""
                ),
                "",
                game.get(
                    "home_record",
                    ""
                ),
                home_color,
                show_score=False
            )

        # ---------------------------------------------
        # LIVE FOOTBALL
        # ---------------------------------------------

        elif state == "in":

            header = self.shorten(
                game.get(
                    "short_status",
                    ""
                ),
                12
            )

            self.draw_header(
                sport,
                header
            )

            self.draw_team_line(
                17,
                game.get(
                    "away_team",
                    ""
                ),
                game.get(
                    "away_score",
                    ""
                ),
                "",
                away_color
            )

            self.draw_team_line(
                29,
                game.get(
                    "home_team",
                    ""
                ),
                game.get(
                    "home_score",
                    ""
                ),
                "",
                home_color
            )

            # Small possession indicator.
            possession = game.get(
                "possession",
                ""
            )

            if possession:

                if (
                    possession
                    == game.get(
                        "away_team"
                    )
                ):

                    self.draw_text(
                        self.small_font,
                        27,
                        16,
                        self.yellow,
                        ">"
                    )

                elif (
                    possession
                    == game.get(
                        "home_team"
                    )
                ):

                    self.draw_text(
                        self.small_font,
                        27,
                        28,
                        self.yellow,
                        ">"
                    )

        # ---------------------------------------------
        # FINAL FOOTBALL
        # ---------------------------------------------

        else:

            self.draw_header(
                sport,
                "FINAL"
            )

            self.draw_team_line(
                17,
                game.get(
                    "away_team",
                    ""
                ),
                game.get(
                    "away_score",
                    ""
                ),
                "",
                away_color
            )

            self.draw_team_line(
                29,
                game.get(
                    "home_team",
                    ""
                ),
                game.get(
                    "home_score",
                    ""
                ),
                "",
                home_color
            )

        self.swap()

        self.pause_frame(
            seconds
        )


    # -----------------------------------------------------
    # NBA
    # -----------------------------------------------------

    def show_basketball_game(
        self,
        game,
        seconds
    ):

        state = game.get(
            "state",
            ""
        )

        away_color = self.get_color(
            game.get(
                "away_color"
            )
        )

        home_color = self.get_color(
            game.get(
                "home_color"
            )
        )

        self.canvas.Clear()

        # ---------------------------------------------
        # UPCOMING NBA
        # ---------------------------------------------

        if state == "pre":

            self.draw_header(
                "NBA",
                format_upcoming_game(
                    game
                )
            )

            self.draw_team_line(
                17,
                game.get(
                    "away_team",
                    ""
                ),
                "",
                game.get(
                    "away_record",
                    ""
                ),
                away_color,
                show_score=False
            )

            self.draw_team_line(
                29,
                game.get(
                    "home_team",
                    ""
                ),
                "",
                game.get(
                    "home_record",
                    ""
                ),
                home_color,
                show_score=False
            )

        # ---------------------------------------------
        # LIVE NBA
        # ---------------------------------------------

        elif state == "in":

            self.draw_header(
                "NBA",
                game.get(
                    "short_status",
                    ""
                )
            )

            self.draw_team_line(
                17,
                game.get(
                    "away_team",
                    ""
                ),
                game.get(
                    "away_score",
                    ""
                ),
                "",
                away_color
            )

            self.draw_team_line(
                29,
                game.get(
                    "home_team",
                    ""
                ),
                game.get(
                    "home_score",
                    ""
                ),
                "",
                home_color
            )

        # ---------------------------------------------
        # FINAL NBA
        # ---------------------------------------------

        else:

            self.draw_header(
                "NBA",
                "FINAL"
            )

            self.draw_team_line(
                17,
                game.get(
                    "away_team",
                    ""
                ),
                game.get(
                    "away_score",
                    ""
                ),
                "",
                away_color
            )

            self.draw_team_line(
                29,
                game.get(
                    "home_team",
                    ""
                ),
                game.get(
                    "home_score",
                    ""
                ),
                "",
                home_color
            )

        self.swap()

        self.pause_frame(
            seconds
        )


    # -----------------------------------------------------
    # MLB
    # -----------------------------------------------------

    def show_baseball_game(
        self,
        game,
        seconds
    ):

        state = game.get(
            "state",
            ""
        )

        away_color = self.get_color(
            game.get(
                "away_color"
            )
        )

        home_color = self.get_color(
            game.get(
                "home_color"
            )
        )

        self.canvas.Clear()

        # ---------------------------------------------
        # UPCOMING MLB
        # ---------------------------------------------

        if state == "pre":

            self.draw_header(
                "MLB",
                format_upcoming_game(
                    game
                )
            )

            self.draw_team_line(
                17,
                game.get(
                    "away_team",
                    ""
                ),
                "",
                game.get(
                    "away_record",
                    ""
                ),
                away_color,
                show_score=False
            )

            self.draw_team_line(
                29,
                game.get(
                    "home_team",
                    ""
                ),
                "",
                game.get(
                    "home_record",
                    ""
                ),
                home_color,
                show_score=False
            )

        # ---------------------------------------------
        # LIVE MLB
        # ---------------------------------------------

        elif state == "in":

            # ESPN commonly returns statuses such as:
            #
            # Top 7th
            # Bottom 3rd
            # Mid 5th
            #
            # shortDetail is typically compact enough
            # for the 64px header.

            self.draw_header(
                "MLB",
                game.get(
                    "short_status",
                    ""
                )
            )

            self.draw_team_line(
                17,
                game.get(
                    "away_team",
                    ""
                ),
                game.get(
                    "away_score",
                    ""
                ),
                "",
                away_color
            )

            self.draw_team_line(
                29,
                game.get(
                    "home_team",
                    ""
                ),
                game.get(
                    "home_score",
                    ""
                ),
                "",
                home_color
            )

        # ---------------------------------------------
        # FINAL MLB
        # ---------------------------------------------

        else:

            self.draw_header(
                "MLB",
                "FINAL"
            )

            self.draw_team_line(
                17,
                game.get(
                    "away_team",
                    ""
                ),
                game.get(
                    "away_score",
                    ""
                ),
                "",
                away_color
            )

            self.draw_team_line(
                29,
                game.get(
                    "home_team",
                    ""
                ),
                game.get(
                    "home_score",
                    ""
                ),
                "",
                home_color
            )

        self.swap()

        self.pause_frame(
            seconds
        )


    # -----------------------------------------------------
    # FALLBACK GENERIC SCREEN
    # -----------------------------------------------------

    def show_generic_game(
        self,
        sport,
        game,
        seconds
    ):

        self.canvas.Clear()

        self.draw_header(
            sport,
            game.get(
                "short_status",
                ""
            )
        )

        away_color = self.get_color(
            game.get(
                "away_color"
            )
        )

        home_color = self.get_color(
            game.get(
                "home_color"
            )
        )

        self.draw_team_line(
            17,
            game.get(
                "away_team",
                ""
            ),
            game.get(
                "away_score",
                ""
            ),
            "",
            away_color
        )

        self.draw_team_line(
            29,
            game.get(
                "home_team",
                ""
            ),
            game.get(
                "home_score",
                ""
            ),
            "",
            home_color
        )

        self.swap()

        self.pause_frame(
            seconds
        )


    # -----------------------------------------------------
    # MESSAGE SCREEN
    # -----------------------------------------------------

    def show_message(
        self,
        line1,
        line2="",
        seconds=2
    ):

        if self.console_mode:

            print(
                line1,
                line2
            )

            time.sleep(
                seconds
            )

            return

        self.canvas.Clear()

        self.draw_text(
            self.font,
            1,
            13,
            self.white,
            self.shorten(
                line1,
                10
            )
        )

        self.draw_text(
            self.font,
            1,
            27,
            self.white,
            self.shorten(
                line2,
                10
            )
        )

        self.swap()

        self.pause_frame(
            seconds
        )