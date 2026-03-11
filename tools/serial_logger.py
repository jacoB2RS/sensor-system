import serial
import struct

PORT = "COM3"
BAUD = 921600

START1 = 0xAA
START2 = 0x55

IMU_SAMPLE_SIZE = 20
TYPE_IMU = 0x01

OUTPUT_FILE = "imu_log.bin"


def crc16_ccitt(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc


def decode_imu_sample(sample_bytes):
    return struct.unpack("<IIhhhhhh", sample_bytes)


ser = serial.Serial(PORT, BAUD, timeout=1)

print("Listening...")

with open(OUTPUT_FILE, "wb") as f:
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
                crc_bytes = ser.read(2)

                if len(payload) != payload_len or len(crc_bytes) != 2:
                    print("Incomplete packet")
                    continue

                recv_crc = crc_bytes[0] | (crc_bytes[1] << 8)

                crc_data = bytes([msg_type, count]) + payload
                calc_crc = crc16_ccitt(crc_data)

                if recv_crc != calc_crc:
                    print("CRC FAIL - packet dropped")
                    continue

                if msg_type != TYPE_IMU:
                    continue

                # NYTT: skriv raw payload til fil
                f.write(payload)

                # valgfritt: vis bare første sample i pakken
                if count > 0:
                    first_sample = payload[:IMU_SAMPLE_SIZE]
                    seq, time_us, ax, ay, az, gx, gy, gz = decode_imu_sample(first_sample)

                    print(
                        f"Logged {count} samples | "
                        f"seq={seq} ax={ax} ay={ay} az={az}"
                    )

            

    

