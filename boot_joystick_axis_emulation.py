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
7) Download this boot_joystick_axis_emulation.py file to the now appeared CircuitPython USB drive as boot.py
8) Save the accompanying code_joystick_axis_emulation.py file as code.py to the now appeared CircuitPython USB drive
9) Go to your flight simulator, configure the keyboard keys it so that Numpad+ causes trim nose up, and Numpad- causes trim nose down
10) Start a flight and rotate the knob to trim!
11) Fashion some sort of stand and wheel. Cardboard, wood, or 3D printer, whatever works for you.
"""
import usb_hid
import usb_cdc

# This descriptor reports 16 buttons + 4 axes, each axis is 16-bit signed (-32768..32767).
GAMEPAD_REPORT_DESCRIPTOR = bytes(
    [
        0x05, 0x01,        # Usage Page (Generic Desktop)
        0x09, 0x05,        # Usage (Gamepad)
        0xA1, 0x01,        # Collection (Application)

        # ------------------------------------------------- 
        # 16 Buttons (2 bytes)
        0x05, 0x09,        #  Usage Page (Button)
        0x19, 0x01,        #  Usage Minimum (Button 1)
        0x29, 0x10,        #  Usage Maximum (Button 16)
        0x15, 0x00,        #  Logical Min (0)
        0x25, 0x01,        #  Logical Max (1)
        0x95, 0x10,        #  Report Count (16 buttons)
        0x75, 0x01,        #  Report Size (1 bit)
        0x81, 0x02,        #  Input (Data,Var,Abs)

        # -------------------------------------------------
        # 4 Axes, each 16-bit signed
        0x05, 0x01,        #  Usage Page (Generic Desktop)
        0x09, 0x30,        #  Usage X
        0x09, 0x31,        #  Usage Y
        0x09, 0x32,        #  Usage Z
        0x09, 0x35,        #  Usage Rz
        0x16, 0x00, 0x80,  #  Logical Min (-32768)
        0x26, 0xFF, 0x7F,  #  Logical Max (32767)
        0x75, 0x10,        #  Report Size (16 bits)
        0x95, 0x04,        #  Report Count (4 axes)
        0x81, 0x02,        #  Input (Data,Var,Abs)

        0xC0               # End Collection
    ]
)

# Create a custom HID device with a 10-byte IN report:
#  - 2 bytes for the 16 button bits
#  - 8 bytes for 4 x 16-bit axes
gamepad_device = usb_hid.Device(
    report_descriptor=GAMEPAD_REPORT_DESCRIPTOR,
    usage_page=0x01,  # Generic Desktop
    usage=0x05,       # Gamepad
    in_report_len=10, # 2 bytes buttons + 8 bytes axes
    out_report_len=1  # Not used here, but must be >= 1
)

# Enable just our custom “gamepad” (and keep default USB-CDC serial for debugging).
usb_hid.enable((gamepad_device,))
# If you want the REPL console to remain available, do not disable usb_cdc.
# If you also want to disable MIDI, do it separately, e.g.: import usb_midi; usb_midi.disable()

# print("BOOTED ;-D")
