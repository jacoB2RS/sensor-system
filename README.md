# Sensor System

Wearable IMU sensor system built with ESP32 + ICM-20948 for motion analysis.

Goal: build a multi-node IMU system that streams motion data in real time and can be used for technique analysis in sports (initial focus: cross-country skiing).

The system is designed to support:
- deterministic sampling
- multiple sensor nodes
- real-time streaming
- offline analysis
- machine learning for technique segmentation and error detection

---

# System Overview

Pipeline:

IMU → ESP32 → binary packets → Python tools → analysis / visualization

ESP32 collects IMU data and sends packets over serial (later BLE).

Python tools receive the packets, decode them, and can log or visualize the motion data.

---

# Hardware

Current node:

- ESP32 Dev Module (ESP32-D0WD-V3)
- ICM-20948 IMU
- I2C
  - SDA → GPIO21
  - SCL → GPIO22
- Power
  - VIN → 3V3
  - GND → GND

Sampling rate target:

200 Hz

---

# Packet Protocol

Binary packet format:
AA 55 | type | count | payload | crc16

| Field | Size | Description |
|------|------|-------------|
| AA 55 | 2 bytes | start marker |
| type | 1 byte | message type |
| count | 1 byte | number of samples |
| payload | N × ImuSample | sensor data |
| crc16 | 2 bytes | CRC16-CCITT |

Message types:

| Type | Meaning |
|-----|--------|
| 0x01 | IMU samples |

---

## ImuSample Layout

Each sample is **20 bytes**.

```c
struct ImuSample {
  uint32_t seq;
  uint32_t time_us;
  int16_t ax, ay, az;
  int16_t gx, gy, gz;
};
``` 

---

# Repository Structure

sensor-system
│
├─ firmware/ # ESP32 firmware
│
├─ tools/
│ ├─ serial_logger.py
│ ├─ ble_receiver.py
│ └─ plot_imu.py
│
└─ README.md

---

# Python Tools

Located in:

tools/


### serial_logger.py

Reads binary packets from ESP32 over USB serial.

Responsibilities:
- detect packet start (`AA55`)
- parse packet header
- verify CRC
- decode `ImuSample`
- print or log data

---

### ble_receiver.py

Future BLE receiver for streaming from ESP32.

---

### plot_imu.py

Tool for plotting IMU data.

Used for quick visualization and debugging.

---

# Running the Serial Receiver

Install dependencies:

pip install pyserial


Run:

python tools/serial_logger.py


Make sure the correct COM port and baud rate are configured.

---

# Project Status

Current stage:

- Single-node IMU streaming over serial
- Binary packet protocol implemented
- Python receiver implemented

Next steps:

- BLE streaming
- Multi-node system
- Motion reconstruction

