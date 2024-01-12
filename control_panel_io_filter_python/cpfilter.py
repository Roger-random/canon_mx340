import serial

with serial.Serial(port='/dev/cu.usbserial-AO002W1A',
                   baudrate=250000,
                   bytesize=serial.EIGHTBITS,
                   parity=serial.PARITY_EVEN,
                   stopbits=1,
                   timeout=0.1) as control_panel:
    # Set up with first byte
    last_byte = control_panel.read()[0]
    last_byte_count = 1
    ack_count = 0
    while(True):
        # Read next byte
        new_byte = control_panel.read()[0]

        if (new_byte == 0x20):
            # Keep count of ACK
            ack_count += 1
        elif (new_byte == last_byte and last_byte_count < 100):
            # Keep count if byte unchanged for <100 repeats
            last_byte_count += 1
        else:
            # Print out a status line of button matrix report byte + count of ACK
            print(hex(last_byte) + " * " + str(last_byte_count) + "    0x20 ACK " + str(ack_count))
            last_byte = new_byte
            last_byte_count = 1
