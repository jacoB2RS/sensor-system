import serial

PORT = "COM3"      # Bytt til riktig port senere
BAUD = 921600

ser = serial.Serial(PORT, BAUD, timeout=1)

print(f"Connected to {PORT} at {BAUD} baud")

while True:
    data = ser.read(32)   # les opptil 32 bytes
    if data:
        print(f"Read {len(data)} bytes: {data}")
