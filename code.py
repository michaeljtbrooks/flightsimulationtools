"""
Adafruit Trinkey Rotary Encoder (SAMD21)

1) Buy the parts (https://thepihut.com/products/rotary-encoder-extras):
  * Adafruit SAMD21 Rotary Trinkey
  * Rotary encoder
  * USB A extension lead
2) Download the .uf2 Trinkey firmware from CircuitPython: https://circuitpython.org/board/adafruit_rotary_trinkey_m0/
3) Solder the rotary encoder to the Adafruit Trinkey
4) Connect it to your computer using the USB A extension lead
5) Press the Reset button on the Trinkey twice, it should appear as a USB drive on your computer folder explorer thing
6) Drag and drop the .uf2 file into the Trinkey USB drive, it should magically unmount then reappear as a "CircuitPython" USB drive
7) Save this code.py file onto the now appeared CircuitPython USB drive
8) Go to your flight simulator, configure the keyboard keys it so that Numpad+ causes trim nose up, and Numpad- causes trim nose down
9) Start a flight and rotate the knob to trim!
10) Fashion some sort of stand and wheel. Cardboard, wood, or 3D printer, whatever works for you.
"""
import time
import board
import rotaryio
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

# Constants
key_presses_per_wheel_click = 8
trim_up_keyboard_button = Keycode.KEYPAD_PLUS
trim_down_keyboard_button = Keycode.KEYPAD_MINUS

# Runtime vars
key_presses_left = {
    trim_up_keyboard_button: 0,
    trim_down_keyboard_button: 0,
}

# Create a Keyboard object
keyboard = Keyboard(usb_hid.devices)

# Set up the rotary encoder
encoder = rotaryio.IncrementalEncoder(board.ROTA, board.ROTB)
last_position = encoder.position

while True:
    # Rotary encoder movement detection:
    position = encoder.position
    if position != last_position:
        if position > last_position:
            # Rotated clockwise -> Trim Up
            key_presses_left[trim_up_keyboard_button] = key_presses_per_wheel_click
            key_presses_left[trim_down_keyboard_button] = 0
            # print("Trim up!")
        else:
            # Rotated anticlockwise -> Trim Down
            key_presses_left[trim_up_keyboard_button] = 0
            key_presses_left[trim_down_keyboard_button] = key_presses_per_wheel_click
            # print("Trim down!")
        last_position = position
    
    # Action - now happens throughout main loop timedelta
    if key_presses_left[trim_up_keyboard_button] > 0:
        keyboard.press(trim_up_keyboard_button)
        keyboard.release_all()
        key_presses_left[trim_up_keyboard_button] = key_presses_left[trim_up_keyboard_button] - 1
        # print("    up")
    elif key_presses_left[trim_down_keyboard_button] > 0:
        keyboard.press(trim_down_keyboard_button)
        keyboard.release_all()
        key_presses_left[trim_down_keyboard_button] = key_presses_left[trim_down_keyboard_button] - 1
        # print("    down")

    # Tick
    time.sleep(0.005)
