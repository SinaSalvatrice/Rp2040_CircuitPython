# RP2040 MicroPython Joystick Controller

A MicroPython implementation for reading analog joystick input on RP2040 microcontroller boards (Raspberry Pi Pico, Pico W, etc.).

## Features

- **Analog Joystick Support**: Reads X and Y axis positions using ADC (Analog-to-Digital Converter)
- **Button Input**: Detects joystick button presses
- **Deadzone Calibration**: Prevents drift when joystick is centered
- **Normalized Output**: Converts raw ADC values to -100 to +100 range
- **Direction Detection**: Converts analog values to directional strings (UP, DOWN, LEFT, RIGHT, CENTER)
- **Real-time Monitoring**: Continuous display of joystick position and button state

## Hardware Setup

### Required Components
- RP2040 board (Raspberry Pi Pico/Pico W)
- Analog joystick module (2-axis with button)
- Jumper wires

### Default Pin Configuration
```
X Axis (VRx) → GPIO26 (ADC0)
Y Axis (VRy) → GPIO27 (ADC1)
Button (SW)  → GPIO16 (with internal pull-up)
VCC          → 3.3V
GND          → GND
```

### Wiring Diagram
```
Joystick Module    →    RP2040 (Pico)
─────────────────────────────────────
VCC (3.3V-5V)      →    3.3V (Pin 36)
GND                →    GND (Pin 38)
VRx (X-axis)       →    GPIO26 (Pin 31)
VRy (Y-axis)       →    GPIO27 (Pin 32)
SW (Button)        →    GPIO16 (Pin 21)
```

## Installation

1. Install MicroPython on your RP2040 board:
   - Download the latest MicroPython firmware from [micropython.org](https://micropython.org/download/rp2-pico/)
   - Flash it to your board using the bootloader

2. Copy `code.py` to your RP2040:
   - Connect your board to your computer via USB
   - Copy `code.py` to the board's filesystem
   - The code will run automatically on boot

## Usage

### Running the Code

Once `code.py` is on your RP2040 board, it will automatically start when the board is powered on or reset. You can also run it manually using a MicroPython REPL:

```python
import code
```

### Output Format

The program continuously prints joystick readings in the following format:
```
X: 32768 (   0%) | Y: 32768 (   0%) | Direction: CENTER          | Button: Released
X: 45000 (  37%) | Y: 28000 ( -14%) | Direction: RIGHT           | Button: Released
X: 50000 (  52%) | Y: 15000 ( -54%) | Direction: RIGHT DOWN      | Button: PRESSED
```

### Customization

You can adjust the following parameters in `code.py`:

```python
# Pin Configuration
JOYSTICK_X_PIN = 26        # Change to match your wiring
JOYSTICK_Y_PIN = 27        # Change to match your wiring
JOYSTICK_BUTTON_PIN = 16   # Change to match your wiring

# Calibration
CENTER_VALUE = 32768       # Adjust if your joystick has different center
DEADZONE = 2000            # Increase/decrease deadzone sensitivity
```

### Direction Detection Thresholds

The direction detection uses these thresholds (adjustable in `get_direction()` function):
- **Threshold**: ±30% from center to register a direction
- **CENTER**: When both X and Y are within the threshold
- **UP/DOWN**: When Y exceeds ±30%
- **LEFT/RIGHT**: When X exceeds ±30%
- **Diagonal**: When both X and Y exceed their thresholds

## Code Structure

### Functions

- `read_joystick()`: Reads raw ADC values and button state
- `normalize_axis(raw_value)`: Converts raw ADC (0-65535) to normalized range (-100 to +100)
- `get_direction(x_norm, y_norm)`: Converts normalized values to directional string
- `main()`: Main program loop for continuous monitoring

## Troubleshooting

### Joystick Values Are Inverted
If your joystick axes are reversed, you can invert them in the `normalize_axis()` function by changing:
```python
deviation = CENTER_VALUE - raw_value  # Invert axis
```

### Joystick Drifts When Centered
Increase the `DEADZONE` value:
```python
DEADZONE = 3000  # or higher
```

### Button Not Working
- Check wiring and ensure button is connected to GPIO16
- Try toggling the button logic in `read_joystick()`:
```python
button_pressed = button.value()  # Remove 'not' if button is active high
```

## License

This project is open source and available for educational and personal use.