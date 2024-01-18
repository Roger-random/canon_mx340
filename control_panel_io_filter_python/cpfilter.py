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
    # Main board
    bulk_transfer_remaining = 0
    command_bytes = 2
    command = 0

    # Control panel
    previous_control_panel_byte = CONTROL_PANEL_NO_BUTTON

    # Both
    ack_expected = 0

    while(True):
        if main_board.in_waiting > 0:
            # Read available data
            new_bytes = main_board.read(main_board.in_waiting)
            for new_byte in new_bytes:
                if bulk_transfer_remaining > 0:
                    bulk_transfer_remaining -= 1
                    if bulk_transfer_remaining == 0:
                        ack_expected += 1
                        command_bytes = 2
                elif command_bytes > 0:
                    if command_bytes == 2:
                        command = new_byte
                        command_bytes -= 1
                    elif command_bytes == 1:
                        if command == 0x06:
                            print("INFO: Bulk transfer", new_byte)
                            bulk_transfer_remaining = new_byte
                        else:
                            command = (command, new_byte)
                            print("COMMAND", command)
                        ack_expected += 1
                        command_bytes = 2
                    else:
                        print("ERROR: Invalid count of command bytes",command_bytes)
                else:
                    print("ERROR: Unexpected state")

        if (control_panel.in_waiting > 0):
            # Read available data
            new_control_panel_bytes = control_panel.read(control_panel.in_waiting)

            for new_control_panel_byte in new_control_panel_bytes:
                if (new_control_panel_byte == CONTROL_PANEL_ACK):
                    ack_expected -= 1
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
