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
    idle_count = 0
    multibyte_wait = 0
    wait_max = 0
    while(True):
        if (control_panel.in_waiting == 0):
            idle_count += 1
        else:
            if control_panel.in_waiting > 1:
                multibyte_wait += 1
                if control_panel.in_waiting > wait_max:
                    wait_max = control_panel.in_waiting
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
                print(hex(last_byte) + " * " + str(last_byte_count) + "    0x20 ACK " + str(ack_count) + "   IDLE " + str(idle_count) + "    Multibyte wait " + str(multibyte_wait) + " max " + str(wait_max))
                last_byte = new_byte
                last_byte_count = 1
                ack_count = 0
                idle_count = 0
                multibyte_wait = 0
                wait_max = 0
