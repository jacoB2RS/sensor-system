import struct
import math
import matplotlib.pyplot as plt

FILE_NAME = "imu_log.bin"
IMU_SAMPLE_SIZE = 21

times = []
roll_accs = []
pitch_accs = []
roll_filters = []
pitch_filters = []

prev_time = None
roll = 0.0
pitch = 0.0

ALPHA = 0.98  # stoler mest på gyro

with open(FILE_NAME, "rb") as f:
    while True:
        data = f.read(IMU_SAMPLE_SIZE)
        if len(data) != IMU_SAMPLE_SIZE:
            break

        node_id, seq, time_us, ax, ay, az, gx, gy, gz = struct.unpack("<BIIhhhhhh", data)

        t = time_us / 1_000_000

        # beregn acc-vinkler
        roll_acc = math.degrees(math.atan2(ay, az))
        pitch_acc = math.degrees(math.atan2(-ax, math.sqrt(ay*ay + az*az)))

        if prev_time is None:
            dt = 0.0
            roll = roll_acc
            pitch = pitch_acc
        else:
            dt = t - prev_time

            # gyro-integrasjon
            roll_gyro = roll + gx * dt
            pitch_gyro = pitch + gy * dt

            # complementary filter
            roll = ALPHA * roll_gyro + (1 - ALPHA) * roll_acc
            pitch = ALPHA * pitch_gyro + (1 - ALPHA) * pitch_acc

        prev_time = t

        times.append(t)
        roll_accs.append(roll_acc)
        pitch_accs.append(pitch_acc)
        roll_filters.append(roll)
        pitch_filters.append(pitch)

print(f"Loaded {len(times)} samples")

plt.figure(figsize=(12, 6))
plt.plot(times, roll_accs, label="roll_acc", alpha=0.5)
plt.plot(times, roll_filters, label="roll_filter")
plt.plot(times, pitch_accs, label="pitch_acc", alpha=0.5)
plt.plot(times, pitch_filters, label="pitch_filter")

plt.xlabel("Time (s)")
plt.ylabel("Angle (degrees)")
plt.title("Complementary filter orientation")
plt.legend()
plt.grid(True)
plt.show()