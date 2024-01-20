import serial

known_commands = {
    (( 0x04, 0x4D ), ( 0x04, 0xC8 ), ( 0x04, 0x30 ), ( 0x6, 0xC4 ),
     ( 0x04, 0xCD ), ( 0x04, 0xC8 ), ( 0x04, 0x30 ), ( 0x6, 0xC4 ),
     ( 0x04, 0x2D ), ( 0x04, 0xC8 ), ( 0x04, 0x30 ), ( 0x6, 0xC4 ),
     ( 0x04, 0xAD ), ( 0x04, 0xC8 ), ( 0x04, 0x30 ), ( 0x6, 0xC4 ),
     ( 0x04, 0x6D ), ( 0x04, 0xC8 ), ( 0x04, 0x30 ), ( 0x6, 0xC4 )):
     "LCD screen update",
    (( 0x04, 0x75 )) : "LCD sleep",
    (( 0x04, 0xF5 )) : "LCD wake",
    (( 0x0E, 0xFB )) : "LED update:  (WiFi) ON   (In Use/Memory) ON",
    (( 0x0E, 0xFF )) : "LED update:  (WiFi) ON   (In Use/Memory) OFF",
    (( 0x0E, 0xF9 )) : "LED update:  (WiFi) OFF  (In Use/Memory) ON",
    (( 0x0E, 0xFD )) : "LED update:  (WiFi) OFF  (In Use/Memory) OFF",
}

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
    awaiting_command = True
    command = 0
    command_sequence = list()
    main_board_idle_count = 0 # Counter for bad timekeeping

    # Control panel
    previous_control_panel_byte = CONTROL_PANEL_NO_BUTTON

    # Both
    ack_expected = 0

    while(True):
        if main_board.in_waiting > 0:
            main_board_idle_count = 0
            # Read available data
            new_bytes = main_board.read(main_board.in_waiting)
            for new_byte in new_bytes:
                if bulk_transfer_remaining > 0:
                    bulk_transfer_remaining -= 1
                    if bulk_transfer_remaining == 0:
                        ack_expected += 1
                        awaiting_command = True
                elif awaiting_command:
                    # New byte is our next command
                    command = new_byte
                    awaiting_command = False
                else:
                    command_sequence.append((command, new_byte))
                    if command == 0x06:
                        # 0x06 is a bulk transfer command, its parameter is length in bytes.
                        bulk_transfer_remaining = new_byte
                    ack_expected += 1
                    awaiting_command = True

                    candidate_command = tuple(command_sequence)
                    if len(command_sequence) == 1:
                        # Stumbled across a Python special case I don't understand
                        # turning single length lists into tuples. This is a
                        # workaround until I learn how to do this properly.
                        candidate_command = tuple(command_sequence[0])

                    if candidate_command in known_commands:
                        print(known_commands[candidate_command])
                        command_sequence.clear()

        elif main_board_idle_count > 10000 and len(command_sequence)>0:
            print("UNKNOWN COMMAND ",end='')
            for step in command_sequence:
                print("(",hex(step[0]), ',', hex(step[1]),"), ",end='')
            print("")
            command_sequence.clear()
        else:
            main_board_idle_count += 1

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
