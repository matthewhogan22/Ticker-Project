Inspiration from: https://learn.adafruit.com/rgb-matrix-panels-with-raspberry-pi-5/basic-test

# 🏈⚾ Sports Ticker

A Raspberry Pi-powered live sports scoreboard displayed on a **64×32 RGB LED matrix**.

The ticker retrieves live game data from ESPN and renders a compact scoreboard designed specifically for a HUB75 RGB LED matrix. It supports multiple sports, live game situations, team colors, scores, records, game clocks, baseball bases/counts, football down-and-distance, and more.

A small web interface is also included for controlling ticker settings without editing configuration files directly.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Supported Sports](#supported-sports)
- [Hardware](#hardware)
- [Hardware Links](#hardware-links)
- [Hardware Wiring](#hardware-wiring)
- [Project Structure](#project-structure)
- [Raspberry Pi Setup](#raspberry-pi-setup)
- [Clone the Repository](#clone-the-repository)
- [Python Dependencies](#python-dependencies)
- [Install the RGB Matrix Library](#install-the-rgb-matrix-library)
- [Install Matrix Fonts](#install-matrix-fonts)
- [Matrix Configuration](#matrix-configuration)
- [Run the Ticker Manually](#run-the-ticker-manually)
- [Web Interface](#web-interface)
- [Systemd Services](#systemd-services)
- [Starting the Services](#starting-the-services)
- [Useful Service Commands](#useful-service-commands)
- [Updating the Ticker](#updating-the-ticker)
- [Testing the LED Matrix](#testing-the-led-matrix)
- [Running on Windows](#running-on-windows)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [How the Project Works](#how-the-project-works)
- [Future Improvements](#future-improvements)
- [Credits](#credits)

---

# Overview

This project turns a Raspberry Pi and HUB75 RGB LED matrix into a live sports ticker.

The system:

1. Retrieves game information from ESPN.
2. Normalizes the data into a common game format.
3. Determines which games should currently be displayed.
4. Renders the game onto a 64×32 LED matrix.
5. Rotates through games automatically.
6. Provides a web interface for changing ticker settings.
7. Automatically starts when the Raspberry Pi boots.

The ticker is designed to run continuously as a dedicated scoreboard appliance.

---

# Features

Current features include:

- Live ESPN sports data
- Live scores
- Upcoming games
- Completed games
- Team abbreviations
- Team colors
- Team records
- Game clock
- Period / quarter / inning
- Game status
- Automatic game rotation
- Eastern Time conversion
- Configurable brightness
- Configurable sports
- Web-based settings interface
- Automatic startup using `systemd`
- Console fallback when RGB matrix hardware is unavailable
- MLB-specific scoreboard information
- NFL-specific scoreboard information

### MLB

MLB games can display:

- Away and home teams
- Scores
- Inning
- Top / bottom of inning
- Balls
- Strikes
- Outs
- Occupied bases
- Game status

### NFL

NFL games can display:

- Away and home teams
- Scores
- Quarter
- Game clock
- Down and distance
- Field position
- Team possession
- Game status

Example field information:

```text
3 & 7
BUF 38
```

---

# Supported Sports

The project currently focuses primarily on:

| Sport | League | Status |
|---|---|---|
| Football | NFL | ✅ Supported |
| Baseball | MLB | ✅ Supported |

Additional ESPN-supported leagues can be added through `sports_info.py`.

Possible future leagues include:

- NCAA Football
- NBA
- NHL
- NCAA Basketball
- MLS

---

# Hardware

The current build uses:

| Component | Purpose |
|---|---|
| Raspberry Pi 4 Model B | Runs the ticker software |
| Adafruit RGB Matrix Bonnet | Interfaces the Pi GPIO pins with the HUB75 matrix |
| 64×32 HUB75 RGB LED Matrix | Displays the scoreboard |
| 5V high-current power supply | Powers the LED matrix |
| Raspberry Pi USB-C power supply | Powers the Raspberry Pi |
| HUB75 ribbon cable | Sends display data to the LED matrix |
| Matrix power cable | Supplies 5V power to the LED matrix |
| MicroSD card | Raspberry Pi OS and ticker software |
| Network connection | Retrieves live sports data |

---

# Hardware Links

Recommended/current hardware:

- **Raspberry Pi 4 Model B**  
  Raspberry Pi official product page

- **Adafruit RGB Matrix Bonnet for Raspberry Pi — Product 3211**  
  Adafruit official product page

- **64×32 RGB LED Matrix — 4 mm Pitch — Product 2278**  
  Adafruit official product page

- **Official Raspberry Pi USB-C Power Supply**  
  Recommended for powering the Raspberry Pi separately from the matrix.

> [!IMPORTANT]
> The LED matrix should use a proper **5V high-current power supply**. Do not attempt to power the LED panel directly from the Raspberry Pi's normal USB power source.

A 64×32 panel can require several amps depending on brightness and how many LEDs are illuminated.

---

# Hardware Wiring

The basic signal path is:

```text
Internet
   │
   ▼
Raspberry Pi 4
   │
   │ GPIO
   ▼
Adafruit RGB Matrix Bonnet
   │
   │ HUB75 Ribbon Cable
   ▼
64×32 RGB LED Matrix
```

Power is supplied separately:

```text
Raspberry Pi PSU
      │
      ▼
Raspberry Pi

5V Matrix PSU
      │
      ▼
RGB Matrix / Matrix Bonnet
```

The HUB75 ribbon cable connects:

```text
RGB Matrix Bonnet
       │
       ▼
Matrix INPUT
```

Make sure the cable is connected to the **INPUT** side of the panel rather than the OUTPUT connector.

---

# Project Structure

The project is organized approximately as follows:

```text
Ticker-Project/
│
├── main.py
├── sports_info.py
├── display.py
├── settings.py
├── settings.json
├── web_server.py
├── requirements.txt
├── .gitignore
│
├── templates/
│   └── index.html
│
└── static/
    └── style.css
```

### `main.py`

Main ticker process.

Responsible for:

- Loading settings
- Fetching games
- Cycling through games
- Sending games to the display
- Refreshing game information

### `sports_info.py`

Handles communication with ESPN.

Responsible for:

- ESPN API requests
- Parsing games
- Team information
- Scores
- Records
- Game state
- MLB information
- NFL information
- Converting ESPN data into the format used by the display

### `display.py`

Handles rendering to the LED matrix.

Responsible for:

- Matrix initialization
- Fonts
- Colors
- Scores
- Team names
- Baseball base indicators
- Balls / strikes / outs
- NFL down and distance
- NFL field position
- Game clock
- Layout

### `settings.py`

Handles application settings.

### `settings.json`

Stores configurable ticker settings.

### `web_server.py`

Runs the web-based configuration interface.

### `templates/index.html`

Main web control-panel page.

### `static/style.css`

Styles the web interface.

---

# Raspberry Pi Setup

The project is designed for Raspberry Pi OS.

Update the Pi first:

```bash
sudo apt update
sudo apt upgrade -y
```

Install the required system packages:

```bash
sudo apt install -y \
    git \
    python3 \
    python3-pip \
    python3-dev \
    python3-pillow \
    python3-setuptools \
    cython3
```

Verify Python:

```bash
python3 --version
```

Verify Git:

```bash
git --version
```

---

# Clone the Repository

Move into your home directory:

```bash
cd ~
```

Clone the repository:

```bash
git clone https://github.com/matthewhogan22/Ticker-Project.git
```

Enter the project directory:

```bash
cd Ticker-Project
```

Check the files:

```bash
ls
```

You should see files similar to:

```text
main.py
sports_info.py
display.py
settings.py
settings.json
web_server.py
requirements.txt
templates/
static/
```

---

# Python Dependencies

Install the project's Python packages:

```bash
pip3 install -r requirements.txt
```

The application uses packages including:

```text
requests
Flask
Pillow
tzdata
```

If necessary, they can also be installed individually:

```bash
pip3 install requests Flask Pillow tzdata
```

---

# Install the RGB Matrix Library

The display uses the `rpi-rgb-led-matrix` project.

Project:

```text
hzeller/rpi-rgb-led-matrix
```

The current library supports Python installation directly from GitHub.

Install required development dependencies:

```bash
sudo apt-get install -y \
    python-dev-is-python3 \
    python3-pil \
    cython3
```

Then install the library:

```bash
pip install git+https://github.com/hzeller/rpi-rgb-led-matrix
```

Alternatively, the repository can be cloned manually:

```bash
cd ~
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git
cd rpi-rgb-led-matrix
```

Build the examples:

```bash
make -C examples-api-use
```

---

# Install Matrix Fonts

The ticker expects the RGB matrix BDF fonts to exist here:

```text
/usr/local/share/sports-ticker/fonts/
```

Create the directory:

```bash
sudo mkdir -p /usr/local/share/sports-ticker/fonts
```

The ticker currently uses:

```text
6x10.bdf
4x6.bdf
```

If the RGB matrix repository is located at:

```text
~/rpi-rgb-led-matrix
```

copy the fonts with:

```bash
sudo cp ~/rpi-rgb-led-matrix/fonts/6x10.bdf \
    /usr/local/share/sports-ticker/fonts/
```

```bash
sudo cp ~/rpi-rgb-led-matrix/fonts/4x6.bdf \
    /usr/local/share/sports-ticker/fonts/
```

Verify:

```bash
ls -l /usr/local/share/sports-ticker/fonts/
```

Expected:

```text
4x6.bdf
6x10.bdf
```

---

# Matrix Configuration

The current display configuration is:

```python
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = "adafruit-hat"
options.gpio_slowdown = 4
options.brightness = 30
options.drop_privileges = False
```

### Resolution

```text
64 × 32 pixels
```

### Hardware mapping

```text
adafruit-hat
```

This is required for the Adafruit RGB Matrix Bonnet/HAT GPIO layout.

### GPIO slowdown

```text
4
```

This value has worked reliably with the Raspberry Pi 4 used for this project.

### Brightness

Default:

```text
30%
```

Lower brightness:

- reduces power consumption
- reduces heat
- is easier to read indoors

---

# Run the Ticker Manually

Move into the project directory:

```bash
cd ~/Ticker-Project
```

Run:

```bash
sudo python3 main.py
```

`sudo` is normally required for direct GPIO access.

Stop the program with:

```text
Ctrl + C
```

---

# Web Interface

The project includes a Flask web server for changing ticker settings.

Run it manually:

```bash
cd ~/Ticker-Project
python3 web_server.py
```

The interface can then be accessed from another device on the same network using the Raspberry Pi's IP address and configured Flask port.

Find the Pi's IP:

```bash
hostname -I
```

Example:

```text
192.168.1.100
```

Then open the corresponding address in a browser.

---

# Systemd Services

Two services are used so the ticker automatically starts with the Raspberry Pi.

```text
sports-ticker.service
sports-ticker-web.service
```

## Main ticker

```text
sports-ticker.service
```

Runs:

```text
main.py
```

Because the RGB matrix requires GPIO access, the ticker process runs with the permissions needed to access the matrix hardware.

## Web interface

```text
sports-ticker-web.service
```

Runs:

```text
web_server.py
```

---

# Starting the Services

Whenever a service definition is created or changed:

```bash
sudo systemctl daemon-reload
```

Enable the ticker at boot:

```bash
sudo systemctl enable sports-ticker.service
```

Enable the web interface at boot:

```bash
sudo systemctl enable sports-ticker-web.service
```

Start the ticker:

```bash
sudo systemctl start sports-ticker.service
```

Start the web server:

```bash
sudo systemctl start sports-ticker-web.service
```

---

# Useful Service Commands

## Check ticker status

```bash
sudo systemctl status sports-ticker.service
```

## Check web server status

```bash
sudo systemctl status sports-ticker-web.service
```

## Restart ticker

```bash
sudo systemctl restart sports-ticker.service
```

## Restart web server

```bash
sudo systemctl restart sports-ticker-web.service
```

## Restart both

```bash
sudo systemctl restart sports-ticker.service
sudo systemctl restart sports-ticker-web.service
```

## Stop ticker

```bash
sudo systemctl stop sports-ticker.service
```

## Stop web server

```bash
sudo systemctl stop sports-ticker-web.service
```

## Start ticker

```bash
sudo systemctl start sports-ticker.service
```

## Start web server

```bash
sudo systemctl start sports-ticker-web.service
```

## Disable ticker at startup

```bash
sudo systemctl disable sports-ticker.service
```

## Disable web server at startup

```bash
sudo systemctl disable sports-ticker-web.service
```

---

# Viewing Logs

## Live ticker logs

```bash
sudo journalctl -u sports-ticker.service -f
```

## Live web-server logs

```bash
sudo journalctl -u sports-ticker-web.service -f
```

## Recent ticker logs

```bash
sudo journalctl -u sports-ticker.service -n 100
```

## Recent web-server logs

```bash
sudo journalctl -u sports-ticker-web.service -n 100
```

## Logs since boot

```bash
sudo journalctl -u sports-ticker.service -b
```

---

# Updating the Ticker

The project is deployed through Git.

Move into the repository:

```bash
cd ~/Ticker-Project
```

Check the current state:

```bash
git status
```

Download the newest version:

```bash
git pull
```

Restart the ticker:

```bash
sudo systemctl restart sports-ticker.service
```

Restart the web server:

```bash
sudo systemctl restart sports-ticker-web.service
```

The normal deployment sequence is therefore:

```bash
cd ~/Ticker-Project
git pull
sudo systemctl restart sports-ticker.service
sudo systemctl restart sports-ticker-web.service
```

Check everything afterward:

```bash
sudo systemctl status sports-ticker.service
sudo systemctl status sports-ticker-web.service
```

---

# Testing the LED Matrix

Before debugging the ticker itself, verify that the RGB panel works.

Move into the matrix library:

```bash
cd ~/rpi-rgb-led-matrix
```

Build the examples if necessary:

```bash
make -C examples-api-use
```

Run a matrix demo:

```bash
sudo examples-api-use/demo \
    --led-rows=32 \
    --led-cols=64 \
    --led-chain=1 \
    --led-gpio-mapping=adafruit-hat \
    --led-slowdown-gpio=4 \
    -D0
```

If the demo renders properly, the following are likely working:

- Raspberry Pi GPIO
- RGB Matrix Bonnet
- HUB75 ribbon cable
- Matrix power supply
- LED panel
- Matrix driver

This is useful for separating a **hardware problem** from a **ticker software problem**.

---

# Running on Windows

The sports-data portion of the application can also be run on Windows for development.

Install Python dependencies:

```powershell
pip install -r requirements.txt
```

Then run:

```powershell
python sports_info.py
```

or:

```powershell
python main.py
```

The actual RGB matrix library is Raspberry Pi-specific.

If `rgbmatrix` cannot be imported, the application can fall back to **console mode**.

You may see:

```text
rgbmatrix library not found.
Running in console mode.
```

This allows much of the ticker logic to be tested without the physical LED panel.

---

# Windows Time Zone Error

Python's `zoneinfo` package may require timezone data on Windows.

If an error similar to this occurs:

```text
ZoneInfoNotFoundError
```

install:

```powershell
pip install tzdata
```

Then rerun the application.

---

# Configuration

Ticker settings are stored in:

```text
settings.json
```

They are loaded and managed through:

```text
settings.py
```

The web interface can modify configurable settings without manually editing the JSON file.

Possible settings include things such as:

- Enabled sports
- Brightness
- Game rotation behavior
- Display timing
- Refresh timing

---

# ESPN Data

Game data is retrieved from ESPN's public site API.

The project requests scoreboard endpoints similar to:

```text
site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard
```

`sports_info.py` converts ESPN's responses into data that can be consumed by `display.py`.

The system intentionally separates:

```text
ESPN
  │
  ▼
sports_info.py
  │
  ▼
Normalized Game Data
  │
  ▼
main.py
  │
  ▼
display.py
  │
  ▼
64×32 LED Matrix
```

This makes it easier to change either the data source or the display layout independently.

---

# How the Project Works

The basic application flow is:

```text
                    ┌──────────────────┐
                    │      ESPN        │
                    │  Scoreboard API  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  sports_info.py  │
                    │                  │
                    │ Fetch + Parse    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │     main.py      │
                    │                  │
                    │ Game Rotation    │
                    │ Refresh Logic    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │    display.py    │
                    │                  │
                    │ Scoreboard       │
                    │ Rendering        │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   RGB Matrix     │
                    │     64 × 32      │
                    └──────────────────┘
```

The configuration system operates alongside it:

```text
Browser
   │
   ▼
web_server.py
   │
   ▼
settings.py
   │
   ▼
settings.json
   │
   ▼
main.py
```

---

# Troubleshooting

## Service name typo

The correct ticker service is:

```text
sports-ticker.service
```

Not:

```text
sports-tikcer.service
```

If you receive:

```text
Unit sports-tikcer.service not loaded
```

check the spelling.

---

## Ticker will not start

Check:

```bash
sudo systemctl status sports-ticker.service
```

Then:

```bash
sudo journalctl -u sports-ticker.service -n 100
```

---

## Web interface will not start

Check:

```bash
sudo systemctl status sports-ticker-web.service
```

Then:

```bash
sudo journalctl -u sports-ticker-web.service -n 100
```

---

## Code changed but display did not

Pull the newest code:

```bash
cd ~/Ticker-Project
git pull
```

Then restart:

```bash
sudo systemctl restart sports-ticker.service
```

If web files changed too:

```bash
sudo systemctl restart sports-ticker-web.service
```

---

## `rgbmatrix library not found`

If you see:

```text
rgbmatrix library not found.
Running in console mode.
```

the Python RGB matrix bindings are not available in the current environment.

Verify:

```bash
python3 -c "from rgbmatrix import RGBMatrix; print('rgbmatrix OK')"
```

If the import fails, reinstall the library.

---

## Matrix displays garbage or corrupted pixels

The Raspberry Pi 4 can drive the GPIO interface too quickly for some panels.

This project uses:

```python
options.gpio_slowdown = 4
```

Make sure that setting has not been changed.

---

## Nothing appears on the panel

Verify:

1. Panel has 5V power.
2. Raspberry Pi is powered.
3. HUB75 cable is connected to the panel's INPUT.
4. Bonnet is seated correctly on the Pi.
5. Matrix test program works.
6. `sports-ticker.service` is running.
7. Matrix dimensions are configured as 64×32.
8. Hardware mapping is `adafruit-hat`.

Check:

```bash
sudo systemctl status sports-ticker.service
```

---

## Font not found

The program expects:

```text
/usr/local/share/sports-ticker/fonts/6x10.bdf
/usr/local/share/sports-ticker/fonts/4x6.bdf
```

Check:

```bash
ls -l /usr/local/share/sports-ticker/fonts/
```

If they are missing:

```bash
sudo mkdir -p /usr/local/share/sports-ticker/fonts
```

Then copy them from:

```text
rpi-rgb-led-matrix/fonts/
```

---

## Check that ESPN is reachable

Test internet connectivity:

```bash
ping -c 4 espn.com
```

Test HTTPS connectivity:

```bash
curl -I https://site.api.espn.com
```

---

## Find Raspberry Pi IP Address

```bash
hostname -I
```

---

## Check network connection

```bash
ip addr
```

or:

```bash
nmcli device status
```

---

## Restart the Raspberry Pi

```bash
sudo reboot
```

---

## Shut down safely

```bash
sudo shutdown -h now
```

Do not simply disconnect power from the Raspberry Pi while the operating system is running.

---

# Helpful Commands Cheat Sheet

### Update repository

```bash
cd ~/Ticker-Project
git pull
```

### Restart everything

```bash
sudo systemctl restart sports-ticker.service
sudo systemctl restart sports-ticker-web.service
```

### Check everything

```bash
sudo systemctl status sports-ticker.service
sudo systemctl status sports-ticker-web.service
```

### Watch ticker logs

```bash
sudo journalctl -u sports-ticker.service -f
```

### Watch web logs

```bash
sudo journalctl -u sports-ticker-web.service -f
```

### Find Pi IP

```bash
hostname -I
```

### Reboot Pi

```bash
sudo reboot
```

### Shutdown Pi

```bash
sudo shutdown -h now
```

---

# Current Display Specifications

| Setting | Value |
|---|---|
| Matrix Width | 64 pixels |
| Matrix Height | 32 pixels |
| Chain Length | 1 |
| Parallel Chains | 1 |
| GPIO Mapping | `adafruit-hat` |
| GPIO Slowdown | `4` |
| Default Brightness | `30` |
| Main Font | `6x10.bdf` |
| Small Font | `4x6.bdf` |
| Pi | Raspberry Pi 4 |
| Display Interface | HUB75 |
| Time Zone | Eastern Time |

---

# Adding a Second Panel

The RGB matrix library supports chained HUB75 panels.

For example, two horizontally chained 64×32 panels would provide:

```text
128 × 32
```

and would generally require changing:

```python
options.chain_length = 1
```

to:

```python
options.chain_length = 2
```

The second panel connects approximately as:

```text
Raspberry Pi
     │
     ▼
RGB Matrix Bonnet
     │
     ▼
Panel 1 INPUT

Panel 1 OUTPUT
     │
     ▼
Panel 2 INPUT
```

Power requirements increase when additional panels are added, so the matrix power supply must be sized appropriately.

---

# Development Workflow

Development can be done on another computer and pushed to GitHub.

Typical workflow:

```bash
git status
git add .
git commit -m "Update scoreboard layout"
git push
```

Then on the Raspberry Pi:

```bash
cd ~/Ticker-Project
git pull
sudo systemctl restart sports-ticker.service
```

If the web interface changed:

```bash
sudo systemctl restart sports-ticker-web.service
```

---

# Future Improvements

Potential future additions include:

- NBA support
- NHL support
- NCAA football support
- NCAA basketball support
- Soccer / MLS support
- Team logos
- Multiple chained panels
- 128×32 display mode
- 128×64 display mode
- Web-based sport selection
- Web-based brightness adjustment
- Additional scoreboard layouts
- Weather rotation
- News / headline rotation
- Custom messages
- Remote software updates
- Automatic health monitoring
- Wi-Fi setup interface

---

# Software Used

This project makes use of:

- Python
- Flask
- Requests
- Pillow
- Raspberry Pi OS
- `rpi-rgb-led-matrix`
- ESPN site API
- HTML
- CSS
- JavaScript
- systemd

---

# Credits

### RGB Matrix Driver

The LED matrix is controlled using:

```text
hzeller/rpi-rgb-led-matrix
```

The library provides high-performance Raspberry Pi GPIO control for HUB75 RGB LED matrix panels.

### Sports Data

Sports scoreboard information is retrieved from ESPN's site API.

### Hardware

The current hardware design uses:

- Raspberry Pi 4 Model B
- Adafruit RGB Matrix Bonnet
- 64×32 HUB75 RGB LED Matrix

---

# Disclaimer

This is an independent hobby/project implementation.

ESPN, NFL, MLB, team names, logos, and related marks are the property of their respective owners. This project is not affiliated with or endorsed by ESPN, the NFL, MLB, or participating teams.

---

# License

```text
Apache 2.0
```
