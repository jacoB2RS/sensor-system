import serial

PORT = "COM3"
BAUD = 921600

START1 = 0xAA
START2 = 0x55

IMU_SAMPLE_SIZE = 20

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

            payload_len = count * IMU_SAMPLE_SIZE
            payload = ser.read(payload_len)
            crc = ser.read(2)

            if len(payload) != payload_len or len(crc) != 2:
                print("incomplete packet")
                continue
            
            print(
                f"Packet OK so far "
                f"type={msg_type} count={count} "
                f"payload_bytes={len(payload)} crc_bytes={len(crc)}"
            )

            

    

