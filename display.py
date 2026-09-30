import glob
import os
import time


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
                hex_color[i:i + 2],
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


# ---------------------------------------------------------
# FONT LOCATION
# ---------------------------------------------------------

def find_font(filename):

    font_path = (
        f"/usr/local/share/"
        f"sports-ticker/fonts/"
        f"{filename}"
    )

    if not os.path.isfile(font_path):

        raise FileNotFoundError(
            f"Could not find RGB matrix font: {font_path}"
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

        options = RGBMatrixOptions()

        # One 64x32 panel
        options.rows = 32
        options.cols = 64

        options.chain_length = 1

        options.parallel = 1

        options.hardware_mapping = (
            "adafruit-hat"
        )

        options.gpio_slowdown = 4

        options.brightness = (
            brightness
        )

        self.matrix = RGBMatrix(
            options=options
        )

        self.canvas = (
            self.matrix
            .CreateFrameCanvas()
        )

        # Main font
        self.font = graphics.Font()

        self.font.LoadFont(
            find_font(
                "6x10.bdf"
            )
        )

        # Small header font
        self.small_font = (
            graphics.Font()
        )

        self.small_font.LoadFont(
            find_font(
                "4x6.bdf"
            )
        )

        self.white = (
            graphics.Color(
                255,
                255,
                255
            )
        )

        self.gray = (
            graphics.Color(
                120,
                120,
                120
            )
        )


    # -----------------------------------------------------
    # INTERNAL HELPERS
    # -----------------------------------------------------

    def get_color(
        self,
        hex_color
    ):

        rgb = hex_to_rgb(
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


    # -----------------------------------------------------
    # GAME SCREEN
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
                f"| {game['status']}"
            )

            time.sleep(
                min(
                    seconds,
                    2
                )
            )

            return

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

        end_time = (
            time.time()
            + seconds
        )

        while (
            time.time()
            < end_time
        ):

            self.canvas.Clear()

            # ---------------------------------------------
            # HEADER
            # ---------------------------------------------

            graphics.DrawText(
                self.canvas,
                self.small_font,
                1,
                6,
                self.white,
                sport.upper()
            )

            status = self.shorten(
                game.get(
                    "status",
                    ""
                ),
                11
            )

            graphics.DrawText(
                self.canvas,
                self.small_font,
                18,
                6,
                self.gray,
                status
            )

            # ---------------------------------------------
            # AWAY TEAM
            # ---------------------------------------------

            away_team = self.shorten(
                game.get(
                    "away_team",
                    ""
                ),
                4
            )

            graphics.DrawText(
                self.canvas,
                self.font,
                1,
                17,
                away_color,
                away_team
            )

            graphics.DrawText(
                self.canvas,
                self.font,
                42,
                17,
                self.white,
                str(
                    game.get(
                        "away_score",
                        ""
                    )
                )
            )

            # ---------------------------------------------
            # HOME TEAM
            # ---------------------------------------------

            home_team = self.shorten(
                game.get(
                    "home_team",
                    ""
                ),
                4
            )

            graphics.DrawText(
                self.canvas,
                self.font,
                1,
                29,
                home_color,
                home_team
            )

            graphics.DrawText(
                self.canvas,
                self.font,
                42,
                29,
                self.white,
                str(
                    game.get(
                        "home_score",
                        ""
                    )
                )
            )

            self.canvas = (
                self.matrix
                .SwapOnVSync(
                    self.canvas
                )
            )

            time.sleep(
                0.05
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

        end_time = (
            time.time()
            + seconds
        )

        while (
            time.time()
            < end_time
        ):

            self.canvas.Clear()

            graphics.DrawText(
                self.canvas,
                self.font,
                1,
                13,
                self.white,
                self.shorten(
                    line1,
                    10
                )
            )

            graphics.DrawText(
                self.canvas,
                self.font,
                1,
                27,
                self.white,
                self.shorten(
                    line2,
                    10
                )
            )

            self.canvas = (
                self.matrix
                .SwapOnVSync(
                    self.canvas
                )
            )

            time.sleep(
                0.05
            )