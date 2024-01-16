import serial

serial_parameters = {
    "baudrate":250000,
    "bytesize":serial.EIGHTBITS,
    "parity":serial.PARITY_EVEN,
    "stopbits":serial.STOPBITS_ONE
}

CONTROL_PANEL_ACK       = 0x20  # Acknowledgement of main board commands
CONTROL_PANEL_NO_BUTTON = 0x80  # Default scan code for "no button pressed"

with serial.Serial(
    port='/dev/cu.usbserial-ABSCE0EZ', **serial_parameters) as main_board, serial.Serial(
    port='/dev/cu.usbserial-AO002W1A', **serial_parameters) as control_panel:
    previous_control_panel_byte = CONTROL_PANEL_NO_BUTTON
    idle_count = 0
    mb_count = 0
    while(True):
        if main_board.in_waiting > 0:
            # Read available data
            new_bytes = main_board.read(main_board.in_waiting)
            for new_byte in new_bytes:
                mb_count += 1
        elif mb_count > 0:
            idle_count += 1

        if idle_count > 100000:
            print("Main board sent",str(mb_count),"bytes")
            mb_count = 0
            idle_count = 0

        if (control_panel.in_waiting > 0):
            # Read available data
            new_control_panel_bytes = control_panel.read(control_panel.in_waiting)

            for new_control_panel_byte in new_control_panel_bytes:
                if (new_control_panel_byte == CONTROL_PANEL_ACK):
                    None # Ignore ACK for now
                elif (new_control_panel_byte != previous_control_panel_byte):
                    print(hex(new_control_panel_byte), end=' ')
                    if new_control_panel_byte == CONTROL_PANEL_NO_BUTTON:
                        print("button released")
                    elif new_control_panel_byte == 0x40:
                        print("expected but unknown")
                    elif new_control_panel_byte >= 0x89 and new_control_panel_byte <=0xCC:
                        print("button scan code")
                    else:
                        print("-- NOVEL VALUE? --")
                    previous_control_panel_byte = new_control_panel_byte
