"""
Adafruit Trinkey Rotary Encoder (SAMD21) - Emulating as joystick axis

1) Buy the parts (https://thepihut.com/products/rotary-encoder-extras):
  * Adafruit SAMD21 Rotary Trinkey
  * Rotary encoder
  * USB A extension lead
2) Download the .uf2 Trinkey firmware from CircuitPython: https://circuitpython.org/board/adafruit_rotary_trinkey_m0/
3) Solder the rotary encoder to the Adafruit Trinkey
4) Connect it to your computer using the USB A extension lead
5) Press the Reset button on the Trinkey twice, it should appear as a USB drive on your computer folder explorer thing
6) Drag and drop the .uf2 file into the Trinkey USB drive, it should magically unmount then reappear as a "CircuitPython" USB drive
7) Download the accompanying boot_custom_joystick.py file to the now appeared CircuitPython USB drive as boot.py
8) Save this code_joystick_axis_emulation.py file as code.py to the now appeared CircuitPython USB drive
9) Go to your flight simulator, configure the Trinkey axis so that wheel up and away trims down, wheel down and toward trims up
10) Start a flight and rotate the knob to trim!
11) Fashion some sort of stand and wheel. Cardboard, wood, or 3D printer, whatever works for you.
"""
import time
import board
import rotaryio
import usb_hid

SENSITIVITY = 512  # Change this to say how much each step will move the trim


# We'll define a small helper class to hold and send our 10-byte report.
# Layout of self._report:
#  bytes 0-1: 16 bits for buttons (we won't use them, so always zero)
#  bytes 2-3: X axis (16-bit signed)
#  bytes 4-5: Y axis (16-bit signed)
#  bytes 6-7: Z axis (16-bit signed)
#  bytes 8-9: Rz axis (16-bit signed)
class CustomGamepad:
    def __init__(self, device):
        self._device = device
        self._report = bytearray(10)
        self._last_report = bytearray(10)

        # Zero everything by default
        self.set_buttons(0)
        self.set_axes(0, 0, 0, 0)
        self.send(always=True)

    def set_buttons(self, buttons_value):
        # buttons_value is an integer with bits for up to 16 buttons
        self._report[0] = buttons_value & 0xFF
        self._report[1] = (buttons_value >> 8) & 0xFF

    def set_axes(self, x, y, z, rz):
        # Each axis is 16-bit signed: -32768..32767
        # We'll store them little-endian
        def put_le16(offset, value):
            self._report[offset]   = value & 0xFF
            self._report[offset+1] = (value >> 8) & 0xFF

        put_le16(2, x)
        put_le16(4, y)
        put_le16(6, z)
        put_le16(8, rz)

    def send(self, always=False):
        # Only send if changed, unless always=True
        if always or self._report != self._last_report:
            self._device.send_report(self._report)
            self._last_report[:] = self._report

def find_my_gamepad():
    # Look for our custom usage_page=0x01, usage=0x05 device
    for tries in range(0, 5):
        for d in usb_hid.devices:
            if d.usage_page == 0x01 and d.usage == 0x05:
                return d
        time.sleep(0.2)
    return None

# Instantiate the rotary
encoder = rotaryio.IncrementalEncoder(board.ROTA, board.ROTB)
last_position = encoder.position

# Range is -32768..+32767
axis_value = 0

# Find the custom HID device
gp_device = find_my_gamepad()
if gp_device is None:
    print("No custom gamepad device found!")
else:
    # Wrap it with our helper class
    gamepad = CustomGamepad(gp_device)

while True:
    current_position = encoder.position
    if current_position != last_position:
        # Each detent = some step in the axis
        delta = current_position - last_position
        axis_value += (delta * SENSITIVITY)  # Tweak 512 to taste (bigger = more sensitive)

        # Clamp to 16-bit range
        if axis_value < -32768:
            axis_value = -32768
        if axis_value > 32767:
            axis_value = 32767

        # Send the updated axis to X (and zero the others)
        if gp_device is not None:
            gamepad.set_axes(axis_value, 0, 0, 0)
            gamepad.send()
        
        last_position = current_position
        print(current_position)  # For debugging

    time.sleep(0.01)
