"""
RP2040 MicroPython Joystick Controller
Reads analog joystick position (X, Y axes) and button state
Suitable for standard analog joysticks with button
"""

import machine
import time

# Pin configuration for joystick
# Adjust these pins according to your hardware setup
JOYSTICK_X_PIN = 26  # ADC0 - X axis (GPIO26)
JOYSTICK_Y_PIN = 27  # ADC1 - Y axis (GPIO27)
JOYSTICK_BUTTON_PIN = 16  # Digital pin for joystick button

# ADC configuration
adc_x = machine.ADC(machine.Pin(JOYSTICK_X_PIN))
adc_y = machine.ADC(machine.Pin(JOYSTICK_Y_PIN))

# Button configuration (with pull-up resistor)
button = machine.Pin(JOYSTICK_BUTTON_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

# Calibration values (adjust based on your joystick)
# Most joysticks have a center value around 32768 (half of 65535)
CENTER_VALUE = 32768
DEADZONE = 2000  # Deadzone to prevent drift at center position (~3% of ADC range)
DIRECTION_THRESHOLD = 30  # Percentage threshold for direction detection

def read_joystick():
    """
    Read joystick position and button state
    Returns: (x, y, button_pressed)
    """
    # Read raw ADC values (0-65535)
    x_raw = adc_x.read_u16()
    y_raw = adc_y.read_u16()
    
    # Button is active low (pressed = 0)
    button_pressed = not button.value()
    
    return x_raw, y_raw, button_pressed

def normalize_axis(raw_value):
    """
    Normalize axis value to range -100 to 100 with deadzone
    """
    # Calculate deviation from center
    deviation = raw_value - CENTER_VALUE
    
    # Apply deadzone
    if abs(deviation) < DEADZONE:
        return 0
    
    # Normalize to -100 to 100 range
    if deviation > 0:
        normalized = int((deviation - DEADZONE) / (CENTER_VALUE - DEADZONE) * 100)
    else:
        normalized = int((deviation + DEADZONE) / (CENTER_VALUE - DEADZONE) * 100)
    
    # Clamp to valid range
    return max(-100, min(100, normalized))

def get_direction(x_norm, y_norm):
    """
    Convert normalized X/Y values to directional string
    """
    direction = []
    
    if y_norm > DIRECTION_THRESHOLD:
        direction.append("UP")
    elif y_norm < -DIRECTION_THRESHOLD:
        direction.append("DOWN")
    
    if x_norm > DIRECTION_THRESHOLD:
        direction.append("RIGHT")
    elif x_norm < -DIRECTION_THRESHOLD:
        direction.append("LEFT")
    
    if not direction:
        return "CENTER"
    
    return " ".join(direction)

def main():
    """
    Main loop - continuously read and display joystick state
    """
    print("RP2040 Joystick Controller Started")
    print("=" * 50)
    print(f"X Axis Pin: GPIO{JOYSTICK_X_PIN}")
    print(f"Y Axis Pin: GPIO{JOYSTICK_Y_PIN}")
    print(f"Button Pin: GPIO{JOYSTICK_BUTTON_PIN}")
    print("=" * 50)
    print()
    
    last_button_state = False
    
    try:
        while True:
            # Read joystick values
            x_raw, y_raw, button_pressed = read_joystick()
            
            # Normalize values
            x_norm = normalize_axis(x_raw)
            y_norm = normalize_axis(y_raw)
            
            # Get direction string
            direction = get_direction(x_norm, y_norm)
            
            # Display output
            print(f"X: {x_raw:5d} ({x_norm:4d}%) | Y: {y_raw:5d} ({y_norm:4d}%) | Direction: {direction:15s} | Button: {'PRESSED' if button_pressed else 'Released'}")
            
            # Detect button press events
            if button_pressed and not last_button_state:
                print(">>> BUTTON PRESS DETECTED! <<<")
            
            last_button_state = button_pressed
            
            # Delay between readings
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nJoystick controller stopped")

# Run main program
if __name__ == "__main__":
    main()
