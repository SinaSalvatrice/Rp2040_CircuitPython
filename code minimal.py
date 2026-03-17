import time
import board
import digitalio
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from rotaryio import IncrementalEncoder

try:
    import neopixel
    HAS_RGB = True
except ImportError:
    HAS_RGB = False

try:
    import displayio
    import terminalio
    from adafruit_display_text import label
    import adafruit_ssd1306
    import busio
    HAS_DISPLAY = True
except ImportError:
    HAS_DISPLAY = False


# =========================================================
# CONFIG
# =========================================================

# -------- MATRIX PINS --------
# ANPASSEN!
ROW_PINS = [board.GP2, board.GP3, board.GP4]
COL_PINS = [board.GP5, board.GP6, board.GP7]

# -------- ENCODER PINS --------
ENC_A = board.GP8
ENC_B = board.GP9
ENC_BTN = board.GP10

# -------- RGB --------
RGB_PIN = board.GP13
NUM_PIXELS = 1   # auf 9 ändern, wenn du 9 LEDs hast

# -------- DISPLAY OPTIONAL --------
USE_DISPLAY = False

# Falls OLED:
# SDA_PIN = board.GP0
# SCL_PIN = board.GP1
# OLED_ADDR = 0x3C
# SCREEN_WIDTH = 128
# SCREEN_HEIGHT = 64

# -------- TIMING --------
SCAN_DELAY = 0.001
LOOP_DELAY = 0.005
DEBOUNCE_TIME = 0.02
ENC_BTN_DEBOUNCE = 0.03

# -------- LAYER --------
L_BASE = 0
L_EDIT = 1
L_NAV = 2
L_MEDIA = 3
NUM_LAYERS = 4


# =========================================================
# HID
# =========================================================

kbd = Keyboard(usb_hid.devices)


# =========================================================
# MATRIX SETUP
# =========================================================

rows = []
for pin in ROW_PINS:
    r = digitalio.DigitalInOut(pin)
    r.direction = digitalio.Direction.OUTPUT
    r.value = True
    rows.append(r)

cols = []
for pin in COL_PINS:
    c = digitalio.DigitalInOut(pin)
    c.direction = digitalio.Direction.INPUT
    c.pull = digitalio.Pull.UP
    cols.append(c)

ROWS = len(ROW_PINS)
COLS = len(COL_PINS)

last_state = [[False for _ in range(COLS)] for _ in range(ROWS)]
last_change = [[0.0 for _ in range(COLS)] for _ in range(ROWS)]


# =========================================================
# ENCODER SETUP
# =========================================================

encoder = IncrementalEncoder(ENC_A, ENC_B)
last_encoder_pos = encoder.position

enc_btn = digitalio.DigitalInOut(ENC_BTN)
enc_btn.direction = digitalio.Direction.INPUT
enc_btn.pull = digitalio.Pull.UP

last_enc_btn = enc_btn.value
last_enc_btn_time = 0.0


# =========================================================
# RGB SETUP
# =========================================================

pixels = None
if HAS_RGB:
    pixels = neopixel.NeoPixel(RGB_PIN, NUM_PIXELS, brightness=0.2, auto_write=True)


# =========================================================
# DISPLAY SETUP
# =========================================================

display_label = None

if USE_DISPLAY and HAS_DISPLAY:
    try:
        displayio.release_displays()
        i2c = busio.I2C(board.GP1, board.GP0)
        display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
        display = adafruit_ssd1306.SSD1306(display_bus, width=128, height=64)

        splash = displayio.Group()
        display.root_group = splash

        display_label = label.Label(
            terminalio.FONT,
            text="boot",
            x=8,
            y=16
        )
        splash.append(display_label)
    except Exception as e:
        print("Display init failed:", e)
        display_label = None


# =========================================================
# KEYMAPS
# 3x3: [row][col]
# =========================================================

keymaps = {
    L_BASE: [
        [Keycode.Q,        Keycode.W,        Keycode.E],
        [Keycode.A,        Keycode.S,        Keycode.D],
        [Keycode.Z,        Keycode.X,        Keycode.C],
    ],
    L_EDIT: [
        [Keycode.CONTROL,  Keycode.C,        Keycode.V],
        [Keycode.X,        Keycode.Z,        Keycode.Y],
        [Keycode.A,        Keycode.BACKSPACE, Keycode.ENTER],
    ],
    L_NAV: [
        [Keycode.UP_ARROW,    Keycode.PAGE_UP,   Keycode.HOME],
        [Keycode.LEFT_ARROW,  Keycode.DOWN_ARROW, Keycode.RIGHT_ARROW],
        [Keycode.END,         Keycode.PAGE_DOWN, Keycode.ENTER],
    ],
    L_MEDIA: [
        [Keycode.F1,       Keycode.F2,       Keycode.F3],
        [Keycode.F4,       Keycode.F5,       Keycode.F6],
        [Keycode.F7,       Keycode.F8,       Keycode.F9],
    ],
}

layer_names = {
    L_BASE: "BASE",
    L_EDIT: "EDIT",
    L_NAV: "NAV",
    L_MEDIA: "MEDIA",
}

current_layer = L_BASE


# =========================================================
# HELPERS
# =========================================================

def set_rgb_for_layer(layer):
    if pixels is None:
        return

    # RGB absichtlich simpel
    if layer == L_BASE:
        color = (0, 0, 40)
    elif layer == L_EDIT:
        color = (40, 0, 0)
    elif layer == L_NAV:
        color = (0, 40, 0)
    elif layer == L_MEDIA:
        color = (40, 20, 0)
    else:
        color = (10, 10, 10)

    pixels.fill(color)


def update_display():
    if display_label is not None:
        display_label.text = "Layer: {}".format(layer_names.get(current_layer, "?"))


def release_all_keys():
    kbd.release_all()


def key_for(layer, row, col):
    return keymaps[layer][row][col]


def tap_keycode(kc):
    kbd.press(kc)
    time.sleep(0.01)
    kbd.release(kc)


def encoder_action(delta):
    global current_layer

    if current_layer == L_BASE:
        if delta > 0:
