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


def lighten_rgb(
    rgb,
    target_brightness=90
):

    r, g, b = rgb

    current = color_brightness(
        rgb
    )

    if current >= target_brightness:
        return rgb

    blend_amount = 0.10

    while blend_amount <= 0.90:

        new_rgb = (
            int(
                r + (
                    255 - r
                ) * blend_amount
            ),
            int(
                g + (
                    255 - g
                ) * blend_amount
            ),
            int(
                b + (
                    255 - b
                ) * blend_amount
            )
        )

        if (
            color_brightness(
                new_rgb
            )
            >= target_brightness
        ):

            return new_rgb

        blend_amount += 0.10

    return (
        200,
        200,
        200
    )

def color_brightness(
    rgb
):

    r, g, b = rgb

    return (
        (r * 299)
        + (g * 587)
        + (b * 114)
    ) / 1000


def color_distance(
    rgb1,
    rgb2
):

    r1, g1, b1 = rgb1
    r2, g2, b2 = rgb2

    return (
        (
            r1 - r2
        ) ** 2
        +
        (
            g1 - g2
        ) ** 2
        +
        (
            b1 - b2
        ) ** 2
    ) ** 0.5


def normalize_team_color(
    hex_color
):

    rgb = hex_to_rgb(
        hex_color
    )

    return lighten_rgb(
        rgb,
        target_brightness=90
    )


def build_team_color_options(
    primary_hex,
    alternate_hex=""
):

    options = []

    # Primary color
    if primary_hex:

        primary = hex_to_rgb(
            primary_hex
        )

        options.append(
            {
                "rgb": normalize_team_color(
                    primary_hex
                ),
                "source": "primary",
                "original_brightness":
                    color_brightness(
                        primary
                    )
            }
        )

    # Alternate color
    if alternate_hex:

        alternate = hex_to_rgb(
            alternate_hex
        )

        options.append(
            {
                "rgb": normalize_team_color(
                    alternate_hex
                ),
                "source": "alternate",
                "original_brightness":
                    color_brightness(
                        alternate
                    )
            }
        )

    # Absolute fallback
    if not options:

        options.append(
            {
                "rgb": (
                    255,
                    255,
                    255
                ),
                "source": "fallback",
                "original_brightness": 255
            }
        )

    return options


def get_matchup_rgb_colors(
    away_primary,
    away_alternate,
    home_primary,
    home_alternate
):

    away_options = (
        build_team_color_options(
            away_primary,
            away_alternate
        )
    )

    home_options = (
        build_team_color_options(
            home_primary,
            home_alternate
        )
    )

    best_pair = None
    best_score = -1

    for away_option in away_options:

        for home_option in home_options:

            away_rgb = (
                away_option["rgb"]
            )

            home_rgb = (
                home_option["rgb"]
            )

            contrast = color_distance(
                away_rgb,
                home_rgb
            )

            away_brightness = (
                color_brightness(
                    away_rgb
                )
            )

            home_brightness = (
                color_brightness(
                    home_rgb
                )
            )

            # Start with color separation.
            score = contrast

            # Reward colors that are clearly readable.
            score += min(
                away_brightness,
                140
            ) * 0.20

            score += min(
                home_brightness,
                140
            ) * 0.20

            # Slight preference for primary colors.
            if (
                away_option["source"]
                == "primary"
            ):

                score += 12

            if (
                home_option["source"]
                == "primary"
            ):

                score += 12

            # Penalize very similar colors.
            if contrast < 70:

                score -= 100

            # Stronger penalty if they are extremely similar.
            if contrast < 40:

                score -= 200

            if score > best_score:

                best_score = score

                best_pair = (
                    away_rgb,
                    home_rgb
                )

    return best_pair

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

    def get_matchup_colors(
        self,
        game
    ):

        away_rgb, home_rgb = (
            get_matchup_rgb_colors(

                game.get(
                    "away_color",
                    ""
                ),

                game.get(
                    "away_alternate_color",
                    ""
                ),

                game.get(
                    "home_color",
                    ""
                ),

                game.get(
                    "home_alternate_color",
                    ""
                )
            )
        )

        away_color = graphics.Color(
            *away_rgb
        )

        home_color = graphics.Color(
            *home_rgb
        )

        return (
            away_color,
            home_color
        )

    def draw_pixel_block(
        self,
        x,
        y,
        rgb,
        size=3
    ):

        r, g, b = rgb

        for dx in range(size):

            for dy in range(size):

                self.canvas.SetPixel(
                    x + dx,
                    y + dy,
                    r,
                    g,
                    b
                )

    def draw_filled_circle(
        self,
        cx,
        cy,
        rgb,
        radius=1
    ):

        r, g, b = rgb

        for dx in range(
            -radius,
            radius + 1
        ):

            for dy in range(
                -radius,
                radius + 1
            ):

                if (
                    dx * dx
                    + dy * dy
                    <= radius * radius
                ):

                    self.canvas.SetPixel(
                        cx + dx,
                        cy + dy,
                        r,
                        g,
                        b
                    )

    def draw_base_diamond(
        self,
        on_first,
        on_second,
        on_third
    ):

        empty = (
            70,
            70,
            70
        )

        occupied = (
            255,
            220,
            0
        )

        # 3x3 base markers with more room on the right side.

        # Second base
        second_color = (
            occupied
            if on_second
            else empty
        )

        self.draw_pixel_block(
            49,
            9,
            second_color,
            size=3
        )

        # Third base
        third_color = (
            occupied
            if on_third
            else empty
        )

        self.draw_pixel_block(
            43,
            15,
            third_color,
            size=3
        )

        # First base
        first_color = (
            occupied
            if on_first
            else empty
        )

        self.draw_pixel_block(
            55,
            15,
            first_color,
            size=3
        )

    def draw_out_indicators(
        self,
        outs
    ):

        on_color = (
            255,
            220,
            0
        )

        off_color = (
            255,
            255,
            255
        )

        # 0 outs:
        # left white, right white
        #
        # 1 out:
        # left white, right yellow
        #
        # 2 outs:
        # left yellow, right yellow

        left_color = off_color
        right_color = off_color

        if outs == 1:

            right_color = on_color

        elif outs >= 2:

            left_color = on_color
            right_color = on_color

        self.draw_filled_circle(
            53,
            28,
            left_color,
            radius=1
        )

        self.draw_filled_circle(
            60,
            28,
            right_color,
            radius=1
        )

    def format_inning(
        self,
        game
    ):

        inning = game.get(
            "inning",
            0
        )

        inning_half = game.get(
            "inning_half",
            ""
        )

        if not inning:

            return self.shorten(
                game.get(
                    "short_status",
                    ""
                ),
                8
            )

        if inning_half == "top":

            return (
                f"^ {inning}"
            )

        if inning_half == "bottom":

            return (
                f"v {inning}"
            )

        return str(
            inning
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

        away_color, home_color = (
            self.get_matchup_colors(
                game
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

        away_color, home_color = (
            self.get_matchup_colors(
                game
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

        away_color, home_color = (
            self.get_matchup_colors(
                game
            )
        )

        self.canvas.Clear()

        # -----------------------------------------------------
        # UPCOMING MLB
        # -----------------------------------------------------

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

        # -----------------------------------------------------
        # LIVE MLB
        # -----------------------------------------------------

        elif state == "in":

            inning_text = self.format_inning(
                game
            )

            # Header
            self.draw_header(
                "MLB",
                inning_text
            )

            # Away team
            self.draw_text(
                self.font,
                1,
                17,
                away_color,
                self.shorten(
                    game.get(
                        "away_team",
                        ""
                    ),
                    4
                )
            )

            self.draw_text(
                self.font,
                29,
                17,
                self.white,
                str(
                    game.get(
                        "away_score",
                        ""
                    )
                )
            )

            # Home team
            self.draw_text(
                self.font,
                1,
                29,
                home_color,
                self.shorten(
                    game.get(
                        "home_team",
                        ""
                    ),
                    4
                )
            )

            self.draw_text(
                self.font,
                29,
                29,
                self.white,
                str(
                    game.get(
                        "home_score",
                        ""
                    )
                )
            )

            # -------------------------------------------------
            # BASE RUNNERS
            # -------------------------------------------------

            self.draw_base_diamond(

                game.get(
                    "on_first",
                    False
                ),

                game.get(
                    "on_second",
                    False
                ),

                game.get(
                    "on_third",
                    False
                )
            )

            # -------------------------------------------------
            # BALLS / STRIKES
            # -------------------------------------------------

            balls = game.get(
                "balls",
                0
            )

            strikes = game.get(
                "strikes",
                0
            )

            count_text = (
                f"{balls}-{strikes}"
            )

            self.draw_text(
                self.small_font,
                37,
                31,
                self.gray,
                count_text
            )

            # -------------------------------------------------
            # OUTS
            # -------------------------------------------------

            outs = game.get(
                "outs",
                0
            )

            self.draw_out_indicators(
                outs
            )

        # -----------------------------------------------------
        # FINAL MLB
        # -----------------------------------------------------

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

        away_color, home_color = (
            self.get_matchup_colors(
                game
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