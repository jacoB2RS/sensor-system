import struct
import matplotlib.pyplot as plt

FILE_NAME = "imu_log.bin"
IMU_SAMPLE_SIZE = 21

samples = []

with open(FILE_NAME, "rb") as f:
    while True:
        data = f.read(IMU_SAMPLE_SIZE)
        if len(data) != IMU_SAMPLE_SIZE:
            break

        node_id, seq, time_us, ax, ay, az, gx, gy, gz = struct.unpack("<BIIhhhhhh", data)

        samples.append({
            "node_id": node_id,
            "seq": seq,
            "time_us": time_us,
            "ax": ax,
            "ay": ay,
            "az": az,
            "gx": gx,
            "gy": gy,
            "gz": gz,
        })

print(f"Loaded {len(samples)} samples")

times = [s["time_us"] / 1_000_000 for s in samples]  # sekunder
ax_values = [s["ax"] for s in samples]
ay_values = [s["ay"] for s in samples]
az_values = [s["az"] for s in samples]

plt.figure(figsize=(12, 6))
plt.plot(times, ax_values, label="ax")
plt.plot(times, ay_values, label="ay")
plt.plot(times, az_values, label="az")

plt.xlabel("Time (s)")
plt.ylabel("Acceleration")
plt.title("IMU acceleration over time")
plt.legend()
plt.grid(True)
plt.show()