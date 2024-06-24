# MIT License

# Copyright (c) 2023 Roger Cheng

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Canon MX340
============================================================
Application as demonstration/test of Canon MX340 communication library

For control panel connector pinout see:
https://newscrewdriver.com/2023/12/21/canon-pixma-mx340-control-panel-connector-to-main-board-pinout/

Draws text to LCD using `font5x8.bin` from
https://github.com/adafruit/Adafruit_CircuitPython_framebuf/tree/main/examples

This file uses board names of a Raspberry Pi Pico. Conversion to use another
CircuitPython microcontroller should be a matter of updating board pin names.
(Example: board.GP0 to board.TX, etc.)
"""

import board
import asyncio
import digitalio
import time

# Direct-wired buttons
from keypad import Keys

# PNG load and parsing
from displayio import Bitmap, Palette
import adafruit_imageload
cat_squid_filename = "tinycatsquid.bmp"
screen_saver_timeout = 10

# K13988 chip and passthrough to LCD
import canon_mx340

async def inuse_blinker(k13988):
    """Blink "In Use/Memory" LED"""
    print("Starting inuse_blinker()")
    while True:
        await k13988.in_use_led(True)
        await asyncio.sleep(0.1)
        await k13988.in_use_led(False)
        await asyncio.sleep(0.1)
        await k13988.in_use_led(True)
        await asyncio.sleep(0.1)
        await k13988.in_use_led(False)
        await asyncio.sleep(1)

async def wifi_blinker(k13988):
    """Blink "WiFi" LED"""
    print("Starting wifi_blinker()")
    while True:
        await k13988.wifi_led(True)
        await asyncio.sleep(0.5)
        await k13988.wifi_led(False)
        await asyncio.sleep(0.5)

async def write_keycode_string(k13988, framebuffer, key_number):
    """Test FrameBuffer support by writing name of pressed key on LCD"""
    text_size = 2
    if key_number in canon_mx340.keycode_string:
        key_name = canon_mx340.keycode_string[key_number]
    else:
        # Every once in a while this happens and I haven't figured out why yet
        key_name = "0x{0:X}".format(key_number)
        print("Unexpected key number {0}".format(key_name))
    text_x = round((196-(len(key_name)*(6*text_size)))/2)
    text_y = round((34 - (9*text_size))/2)

    framebuffer.fill(0)
    framebuffer.text(key_name, text_x, text_y, 1, font_name="lib/font5x8.bin", size=text_size)
    await k13988.refresh()

class Cat_Squid_Screen_Saver:
    def __init__(self, k13988, framebuffer):
        self.k13988 = k13988
        self.framebuffer = framebuffer
        self.screen_saver_frame_period = 0.25
        self.screen_saver_next_update = time.monotonic()
        self.cat_squid_positions = [(20,5), (40,5), (40,15), (20,15)]
        self.cat_squid_current_position = 0

    def load(self):
        cat_squid_bitmap, _ = adafruit_imageload.load(cat_squid_filename)

        # Just a quick hack for fun, so hard-coded for a three-color bitmap.
        # 0 == transparent
        # 1 == black
        # 2 == white

        print("loaded {0}: {1} x {2}".format(cat_squid_filename, cat_squid_bitmap.width, cat_squid_bitmap.height))
        for y in range(cat_squid_bitmap.height):
            line = ""
            for x in range(cat_squid_bitmap.width):
                pixel = cat_squid_bitmap[x,y]
                if pixel == 0:
                    line = line + " "
                elif pixel == 1:
                    line = line + "X"
                elif pixel == 2:
                    line = line + "."
                else:
                    line = line + str(pixel)
            print(line)

    async def loop(self):
        if time.monotonic() > self.screen_saver_next_update:
            self.screen_saver_next_update = time.monotonic() + self.screen_saver_frame_period

            self.framebuffer.fill(1)
            self.framebuffer.text(
                "Cat & Squid",
                self.cat_squid_positions[self.cat_squid_current_position][0], # X coordinate
                self.cat_squid_positions[self.cat_squid_current_position][1], # Y coordinate
                0,
                font_name="lib/font5x8.bin",
                size=2)
            self.cat_squid_current_position = (self.cat_squid_current_position + 1) % len(self.cat_squid_positions)
            await self.k13988.refresh()

async def printkeys(k13988):
    """Poll for key events and show information to LCD screen"""
    print("Starting printkeys()")

    framebuffer = canon_mx340.K13988_FrameBuffer(k13988.get_frame_buffer_bytearray())
    screen_saver = Cat_Squid_Screen_Saver(k13988, framebuffer)

    # Clear screen to display "(None)"
    await write_keycode_string(k13988, framebuffer, canon_mx340.Keycode.NONE)

    # Load bitmap for "screen saver"
    try:
        screen_saver.load()
    except:
        print("Unable to load {0}".format(cat_squid_filename))

    # Enter key input response loop
    last_active_time = time.time()
    while True:
        key = k13988.get_key_event()
        if key:
            if key.pressed:
                await write_keycode_string(k13988, framebuffer, key.key_number)
            else:
                await write_keycode_string(k13988, framebuffer, canon_mx340.Keycode.NONE)
            last_active_time = time.time()
        elif time.time() > (last_active_time + screen_saver_timeout):
            await screen_saver.loop()

        await asyncio.sleep(0)

async def direct_wired(k13988):
    """
    Verify functionality of direct-wired components:
    Power button toggles Power LED, Stop button toggles Alarm LED
    """
    alarm_led = digitalio.DigitalInOut(board.GP3)
    alarm_led.switch_to_output(False)

    power_led = digitalio.DigitalInOut(board.GP4)
    power_led.switch_to_output(False)

    keys = Keys((board.GP5, board.GP6), value_when_pressed=False, pull=True)

    while True:
        event = keys.events.get()
        if event and event.pressed:
            if event.key_number == 0:
                power_led.value = not power_led.value
            elif event.key_number == 1:
                alarm_led.value = not alarm_led.value
            else:
                print("Unexpected key number {0} received".format(event.key_number))
        await asyncio.sleep(0)

async def main():
    """Test app entry point"""
    print("Starting main()")
    async with canon_mx340.K13988(board.GP0, board.GP1, board.GP2) as k13988:
        await asyncio.gather(
            inuse_blinker(k13988),
            wifi_blinker(k13988),
            direct_wired(k13988),
            printkeys(k13988))

asyncio.run(main())
