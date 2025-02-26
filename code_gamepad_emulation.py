"""
Adafruit Trinkey Rotary Encoder (SAMD21) - Emulating as Gamepad axis

1) Buy the parts (https://thepihut.com/products/rotary-encoder-extras):
  * Adafruit SAMD21 Rotary Trinkey
  * Rotary encoder
  * USB A extension lead
2) Download the .uf2 Trinkey firmware from CircuitPython: https://circuitpython.org/board/adafruit_rotary_trinkey_m0/
3) Solder the rotary encoder to the Adafruit Trinkey
4) Connect it to your computer using the USB A extension lead
5) Press the Reset button on the Trinkey twice, it should appear as a USB drive on your computer folder explorer thing
6) Drag and drop the .uf2 file into the Trinkey USB drive, it should magically unmount then reappear as a "CircuitPython" USB drive
1) Stick this file in CIRCUITPY root and rename to code.py
3) Also add boot_gamepad_emulation.py to CIRCUITPY root and rename that to boot.py
4) Also add lib/ to CIRCUITPY root
5) Unplug and replug in your Trinkey
6) Go to X-plane control settings, you'll see an Adafruit Trinkey as a device
7) Calibrate it. The minimum position is about 6 full rotations forward, max position is 12 rotations back (i.e. 6 back from starting point)
"""

import time
import board
import rotaryio
import usb_hid
from lib.adafruit_hid.gamepad import Gamepad

print("Trinkey Rotary Encoder as Gamepad")

# Create the gamepad
gamepad = Gamepad(usb_hid.devices)

# Set up the rotary encoder
encoder = rotaryio.IncrementalEncoder(board.ROTA, board.ROTB)
last_position = encoder.position

# Our 8-bit axis, from -127..127
axis_value = 0

while True:
    current_position = encoder.position
    if current_position != last_position:
        # How many 'clicks' (detents) have we moved?
        delta = current_position - last_position
        axis_value += delta

        # Clamp to -127..127
        if axis_value < -127:
            axis_value = -127
        if axis_value > 127:
            axis_value = 127

        # Move the x-axis to the new position (y, z, r_z remain unchanged)
        gamepad.move_joysticks(x=axis_value)

        # Debug print (optional)
        print(f"Encoder={current_position}, Axis={axis_value}")

        last_position = current_position

    time.sleep(0.01)
