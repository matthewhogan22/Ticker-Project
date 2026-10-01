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

    def draw_down_and_distance(
        self,
        x,
        y,
        down_and_distance
    ):

        if not down_and_distance:
            return

        try:

            down_text, distance_text = (
                down_and_distance.split(
                    "&",
                    1
                )
            )

        except ValueError:

            self.draw_text(
                self.small_font,
                x,
                y,
                self.gray,
                down_and_distance
            )

            return

        self.draw_text(
            self.small_font,
            x,
            y,
            self.gray,
            down_text
        )

        self.draw_text(
            self.small_font,
            x + 4,
            y,
            self.gray,
            "&"
        )

        # Normal next character would start at x + 8.
        # We use x + 9 to create one extra LED pixel.
        self.draw_text(
            self.small_font,
            x + 9,
            y,
            self.gray,
            distance_text
        )

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

            possession = game.get(
                "possession",
                ""
            )

            down_and_distance = (
                game.get(
                    "down_and_distance",
                    ""
                )
            )

            possession_text = (
                game.get(
                    "possession_text",
                    ""
                )
            )

            away_team = game.get(
                "away_team",
                ""
            )

            home_team = game.get(
                "home_team",
                ""
            )

            # -----------------------------------------
            # AWAY TEAM
            # -----------------------------------------

            self.draw_text(
                self.font,
                1,
                17,
                away_color,
                self.shorten(
                    away_team,
                    4
                )
            )

            # Score in same region as MLB.
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

            # -----------------------------------------
            # HOME TEAM
            # -----------------------------------------

            self.draw_text(
                self.font,
                1,
                29,
                home_color,
                self.shorten(
                    home_team,
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

            # -----------------------------------------
            # POSSESSION INDICATOR
            # -----------------------------------------

            if possession == away_team:

                self.draw_text(
                    self.small_font,
                    24,
                    16,
                    self.yellow,
                    ">"
                )

            elif possession == home_team:

                self.draw_text(
                    self.small_font,
                    24,
                    28,
                    self.yellow,
                    ">"
                )

            # -----------------------------------------
            # DOWN AND DISTANCE
            # -----------------------------------------

            self.draw_down_and_distance(
                45,
                16,
                down_and_distance
            )

            # -----------------------------------------
            # FIELD POSITION
            # -----------------------------------------

            if possession_text:

                try:

                    field_team, yard_line = (
                        possession_text.rsplit(
                            " ",
                            1
                        )
                    )

                    # Move the whole field-position display
                    # 3 pixels to the right.
                    field_x = 43

                    self.draw_text(
                        self.small_font,
                        field_x,
                        28,
                        self.gray,
                        field_team
                    )

                    # 4x6 font is roughly 4 pixels per character.
                    #
                    # Put the yard line immediately after the
                    # abbreviation, plus 1 extra pixel of spacing.
                    yard_x = (
                        field_x
                        + (
                            len(field_team)
                            * 4
                        )
                        + 1
                    )

                    self.draw_text(
                        self.small_font,
                        yard_x,
                        28,
                        self.gray,
                        yard_line
                    )

                except ValueError:

                    self.draw_text(
                        self.small_font,
                        43,
                        28,
                        self.gray,
                        self.shorten(
                            possession_text,
                            6
                        )
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
    # TRACKED BET SCREEN
    # -----------------------------------------------------

    def show_bet(
        self,
        bet,
        progress,
        seconds=8
    ):

        # -------------------------------------------------
        # CONSOLE MODE
        # -------------------------------------------------

        if self.console_mode:

            print(
                "\n[MY BET] "
                f"{bet.get('league', '')} | "
                f"{bet.get('selection', '')} | "
                f"{bet.get('side', '')} "
                f"{bet.get('line', '')} | "
                f"{progress.get('message', '')}"
            )

            time.sleep(
                min(
                    seconds,
                    2
                )
            )

            return

        # -------------------------------------------------
        # PREPARE VALUES
        # -------------------------------------------------

        league = str(
            bet.get(
                "league",
                ""
            )
        ).upper()

        bet_type = str(
            bet.get(
                "bet_type",
                ""
            )
        )

        selection = str(
            bet.get(
                "selection",
                ""
            )
        )

        side = str(
            bet.get(
                "side",
                ""
            )
        ).upper()

        line = bet.get(
            "line"
        )

        stat_name = str(
            bet.get(
                "stat_name",
                ""
            )
        )

        progress_state = str(
            progress.get(
                "state",
                ""
            )
        )

        progress_message = str(
            progress.get(
                "message",
                ""
            )
        )

        current_value = progress.get(
            "value"
        )

        final = bool(
            progress.get(
                "final",
                False
            )
        )

        # -------------------------------------------------
        # STATUS COLOR
        # -------------------------------------------------

        if progress_state in (
            "win",
            "winning"
        ):

            status_color = self.green

        elif progress_state in (
            "loss",
            "losing"
        ):

            status_color = graphics.Color(
                255,
                70,
                70
            )

        elif progress_state in (
            "push",
            "pending"
        ):

            status_color = self.yellow

        elif progress_state == "void":

            status_color = self.gray

        else:

            status_color = self.white

        # -------------------------------------------------
        # CLEAR
        # -------------------------------------------------

        self.canvas.Clear()

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header_text = (
            "FINAL BET"
            if final
            else "MY BET"
        )

        self.draw_header(
            league,
            header_text
        )

        # -------------------------------------------------
        # PLAYER PROP
        # -------------------------------------------------

        if bet_type == "player_prop":

            # Player name
            player_text = self.shorten(
                selection,
                15
            )

            self.draw_text(
                self.small_font,
                1,
                13,
                self.white,
                player_text
            )

            # Stat name
            stat_text = self.shorten(
                stat_name,
                15
            )

            self.draw_text(
                self.small_font,
                1,
                20,
                self.gray,
                stat_text
            )

            # ---------------------------------------------
            # VALUE / LINE
            # ---------------------------------------------

            if current_value is not None:

                current_text = self.format_bet_number(
                    current_value
                )

                line_text = self.format_bet_number(
                    line
                )

                value_line = (
                    f"{current_text}/{line_text}"
                )

            else:

                line_text = self.format_bet_number(
                    line
                )

                value_line = (
                    f"{side} {line_text}"
                )

            self.draw_text(
                self.font,
                1,
                31,
                status_color,
                self.shorten(
                    value_line,
                    10
                )
            )

            # Show shortened status on the right.
            status_short = (
                self.format_bet_status(
                    bet,
                    progress
                )
            )

            self.draw_text(
                self.small_font,
                39,
                31,
                status_color,
                self.shorten(
                    status_short,
                    6
                )
            )

        # -------------------------------------------------
        # SPREAD
        # -------------------------------------------------

        elif bet_type == "spread":

            team = self.shorten(
                selection,
                12
            )

            self.draw_text(
                self.font,
                1,
                17,
                self.white,
                team
            )

            line_text = (
                self.format_signed_bet_number(
                    line
                )
            )

            self.draw_text(
                self.font,
                1,
                29,
                self.yellow,
                line_text
            )

            status_text = (
                self.format_bet_status(
                    bet,
                    progress
                )
            )

            self.draw_text(
                self.small_font,
                30,
                29,
                status_color,
                self.shorten(
                    status_text,
                    8
                )
            )

        # -------------------------------------------------
        # MONEYLINE
        # -------------------------------------------------

        elif bet_type == "moneyline":

            team = self.shorten(
                selection,
                12
            )

            self.draw_text(
                self.font,
                1,
                17,
                self.white,
                team
            )

            self.draw_text(
                self.font,
                1,
                29,
                self.yellow,
                "ML"
            )

            status_text = (
                self.format_bet_status(
                    bet,
                    progress
                )
            )

            self.draw_text(
                self.font,
                19,
                29,
                status_color,
                self.shorten(
                    status_text,
                    7
                )
            )

        # -------------------------------------------------
        # GAME TOTAL
        # -------------------------------------------------

        elif bet_type == "total":

            line_text = (
                self.format_bet_number(
                    line
                )
            )

            bet_text = (
                f"{side} {line_text}"
            )

            self.draw_text(
                self.font,
                1,
                17,
                self.white,
                self.shorten(
                    bet_text,
                    10
                )
            )

            if current_value is not None:

                current_text = (
                    self.format_bet_number(
                        current_value
                    )
                )

                self.draw_text(
                    self.small_font,
                    1,
                    27,
                    self.gray,
                    f"TOTAL {current_text}"
                )

            status_text = (
                self.format_bet_status(
                    bet,
                    progress
                )
            )

            self.draw_text(
                self.small_font,
                1,
                32,
                status_color,
                self.shorten(
                    status_text,
                    15
                )
            )

        # -------------------------------------------------
        # GENERIC FALLBACK
        # -------------------------------------------------

        else:

            self.draw_text(
                self.font,
                1,
                17,
                self.white,
                self.shorten(
                    selection,
                    10
                )
            )

            self.draw_text(
                self.small_font,
                1,
                29,
                status_color,
                self.shorten(
                    progress_message,
                    15
                )
            )

        self.swap()

        self.pause_frame(
            seconds
        )


    # -----------------------------------------------------
    # BET DISPLAY HELPERS
    # -----------------------------------------------------

    def format_bet_number(
        self,
        value
    ):

        if value is None:
            return ""

        try:

            number = float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return str(
                value
            )

        if number.is_integer():

            return str(
                int(
                    number
                )
            )

        return (
            f"{number:.1f}"
        )


    def format_signed_bet_number(
        self,
        value
    ):

        if value is None:
            return ""

        try:

            number = float(
                value
            )

        except (
            TypeError,
            ValueError
        ):

            return str(
                value
            )

        text = (
            self.format_bet_number(
                number
            )
        )

        if number > 0:

            return (
                f"+{text}"
            )

        return text


    def format_bet_status(
        self,
        bet,
        progress
    ):

        state = str(
            progress.get(
                "state",
                ""
            )
        )

        final = bool(
            progress.get(
                "final",
                False
            )
        )

        value = progress.get(
            "value"
        )

        line = bet.get(
            "line"
        )

        side = str(
            bet.get(
                "side",
                ""
            )
        ).lower()

        # ---------------------------------------------
        # FINAL STATES
        # ---------------------------------------------

        if final:

            if state == "win":
                return "WIN"

            if state == "loss":
                return "LOSS"

            if state == "push":
                return "PUSH"

            if state == "void":
                return "VOID"

        # ---------------------------------------------
        # PENDING
        # ---------------------------------------------

        if state == "pending":

            return "PENDING"

        # ---------------------------------------------
        # PLAYER PROP / TOTAL
        # ---------------------------------------------

        if (
            value is not None
            and line is not None
            and side in (
                "over",
                "under"
            )
        ):

            try:

                current = float(
                    value
                )

                target = float(
                    line
                )

            except (
                TypeError,
                ValueError
            ):

                return self.shorten(
                    progress.get(
                        "message",
                        ""
                    ),
                    8
                )

            if side == "over":

                difference = (
                    current
                    - target
                )

                if difference > 0:

                    return (
                        "+"
                        + self.format_bet_number(
                            difference
                        )
                    )

                if difference < 0:

                    return (
                        "NEED "
                        + self.format_bet_number(
                            abs(
                                difference
                            )
                        )
                    )

                return "ON LINE"

            difference = (
                target
                - current
            )

            if difference > 0:

                return (
                    "BUF "
                    + self.format_bet_number(
                        difference
                    )
                )

            if difference < 0:

                return (
                    "OVER "
                    + self.format_bet_number(
                        abs(
                            difference
                        )
                    )
                )

            return "ON LINE"

        # ---------------------------------------------
        # SPREAD / MONEYLINE
        # ---------------------------------------------

        if state == "winning":
            return "WINNING"

        if state == "losing":
            return "LOSING"

        if state == "push":
            return "PUSH"

        return self.shorten(
            progress.get(
                "message",
                ""
            ),
            8
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