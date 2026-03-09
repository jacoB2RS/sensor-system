import serial

PORT = "COM3"
BAUD = 921600

START1 = 0xAA
START2 = 0x55

ser = serial.Serial(PORT, BAUD, timeout=1)

print("Listening...")

while True:
    b1 = ser.read(1)
    if not b1:
        continue

    if b1[0] == START1:
        b2 = ser.read(1)
        if b2 and b2[0] == START2:
            header = ser.read(2)

            if len(header) != 2:
                continue

            msg_type = header[0]
            count = header[1]

            print(f"Packet start detected | type={msg_type} count={count}")

