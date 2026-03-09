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
            print("Packet start detected")

