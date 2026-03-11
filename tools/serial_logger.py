import serial
import struct

PORT = "COM3"
BAUD = 921600

START1 = 0xAA
START2 = 0x55

IMU_SAMPLE_SIZE = 20


def crc16_ccitt(data):
    crc = 0xFFFF
    for byte in data :
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc

def decode_imu_sample(sample_byte):
    return struct.unpack("<IIhhhhhh", sample_byte)

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
            crc_bytes = ser.read(2)

            if len(payload) != payload_len or len(crc_bytes) != 2:
                print("incomplete packet")
                continue

            recv_crc = crc_bytes[0] | (crc_bytes[1] << 8)

            crc_data = bytes([msg_type, count]) + payload
            calc_crc = crc16_ccitt(crc_data)

            if recv_crc != calc_crc:
                print("CRC FAIL - packet dropped")
                continue

            for i in range(count):
                start = i * IMU_SAMPLE_SIZE
                end = start + IMU_SAMPLE_SIZE

                sample_bytes = payload[start:end]

                seq, time_us, ax, ay, az, gx, gy, gz = decode_imu_sample(sample_bytes)

                print(
                    f"seq={seq} t={time_us} "
                    f"ax={ax} ay={ay} az={az} "
                    f"gx={gx} gy={gy} gz={gz}"
                )


            

            

    

