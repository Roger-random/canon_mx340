import board
import asyncio
import digitalio

# Direct-wired buttons
from keypad import Keys

# K13988 chip and passthrough to LCD
import canon_mx340

# Blink "In Use/Memory" LED
async def inuse_blinker(k13988):
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

# Blink "WiFi" LED
async def wifi_blinker(k13988):
    print("Starting wifi_blinker()")
    while True:
        await k13988.wifi_led(True)
        await asyncio.sleep(0.5)
        await k13988.wifi_led(False)
        await asyncio.sleep(0.5)

# Test FrameBuffer support by writing name of pressed key
async def write_keycode_string(k13988, framebuffer, key_number):
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

# Print key events to serial console
async def printkeys(k13988):
    print("Starting printkeys()")

    framebuffer = canon_mx340.K13988_FrameBuffer(k13988.get_frame_buffer_bytearray())
    await write_keycode_string(k13988, framebuffer, canon_mx340.Keycode.NONE)

    while True:
        key = k13988.get_key_event()
        if key:
            if key.pressed:
                await write_keycode_string(k13988, framebuffer, key.key_number)
            else:
                await write_keycode_string(k13988, framebuffer, canon_mx340.Keycode.NONE)
        await asyncio.sleep(0)

# Verify functionality of direct-wired components:
# * Buttons: "On" and "Stop"
# * LEDs: "On" and "Alarm"
async def direct_wired(k13988):
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
    print("Starting main()")
    async with canon_mx340.K13988(board.GP0, board.GP1, board.GP2) as k13988:
        await asyncio.gather(
            inuse_blinker(k13988),
            wifi_blinker(k13988),
            direct_wired(k13988),
            printkeys(k13988))

asyncio.run(main())
