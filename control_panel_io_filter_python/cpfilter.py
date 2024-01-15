import serial

with serial.Serial(port='/dev/cu.usbserial-AO002W1A',
                   baudrate=250000,
                   bytesize=serial.EIGHTBITS,
                   parity=serial.PARITY_EVEN,
                   stopbits=1,
                   timeout=0.1) as control_panel:
    last_byte = 0x80 # Default "no button pressed"
    ack_count = 0
    while(True):
        if (control_panel.in_waiting > 0):
            # Read available data
            new_bytes = control_panel.read(control_panel.in_waiting)

            for new_byte in new_bytes:
                if (new_byte == 0x20):
                    # Keep count of ACK
                    ack_count += 1
                elif (new_byte != last_byte):
                    print(hex(new_byte), end=' ')
                    if new_byte == 0x80:
                        print("button released")
                    elif new_byte == 0x40:
                        print("expected but unknown")
                    elif new_byte >= 0x89 and new_byte <=0xCC:
                        print("button scan code")
                    else:
                        print("-- NOVEL VALUE? --")
                    last_byte = new_byte
