#include <Wire.h>
#include <ICM_20948.h>
#include <string.h>

#define NODE_ID 1
#define SDA_PIN 21
#define SCL_PIN 22
#define IMU_ADDR 0x69

ICM_20948_I2C imu;

// ===== Struct =====
#pragma pack(push, 1)
struct ImuSample {
  uint8_t  node_id;
  uint32_t seq;
  uint32_t time_us;
  int16_t ax, ay, az;
  int16_t gx, gy, gz;
};
#pragma pack(pop)

// ===== Buffer =====
#define BUFFER_SIZE 200
ImuSample buffer[BUFFER_SIZE];

// ===== counters =====
volatile int writeIndex = 0;
volatile int readIndex = 0;
volatile int count = 0;

uint32_t dropped = 0;
uint32_t seq = 0;

// ===== Sampling-rate =====
static const uint32_t SAMPLE_HZ = 200;
static const uint32_t PERIOD_US = 1000000UL / SAMPLE_HZ;

// ===== Packet config =====
static const uint8_t PACKET_SAMPLES = 5;

// ===== CRC (CRC16-CCITT) =====
uint16_t crc16_ccitt(const uint8_t* data, size_t len) {
  uint16_t crc = 0xFFFF;
  for (size_t i = 0; i < len; i++) {
    crc ^= (uint16_t)data[i] << 8;
    for (int b = 0; b < 8; b++) {
      if (crc & 0x8000) crc = (crc << 1) ^ 0x1021;
      else crc <<= 1;
    }
  }
  return crc;
}

void sendImuPacketCRC() {
  if (count < PACKET_SAMPLES) return;

  // Header: AA 55 type count
  uint8_t hdr[4] = {0xAA, 0x55, 0x01, PACKET_SAMPLES};

  const size_t payloadBytes = PACKET_SAMPLES * sizeof(ImuSample);
  const size_t crcBufLen = 2 + payloadBytes; // type + count + payload

  // Buffer for CRC calculation: [type][count][payload...]
  static uint8_t crcBuf[2 + PACKET_SAMPLES * sizeof(ImuSample)];
  crcBuf[0] = hdr[2];
  crcBuf[1] = hdr[3];

  // Copy N samples from ringbuffer into crcBuf payload - oppfylling av crcBuf frem til vi treffer 5 samples(PACKET_SAMPLES)
  for (uint8_t i = 0; i < PACKET_SAMPLES; i++) {
    ImuSample s = buffer[readIndex];
    readIndex = (readIndex + 1) % BUFFER_SIZE;
    count--;
  
    memcpy(&crcBuf[2 + i * sizeof(ImuSample)], &s, sizeof(ImuSample));   
  }

  uint16_t crc = crc16_ccitt(crcBuf, crcBufLen);

  // Send packet: header + payload + crc16
  Serial.write(hdr, sizeof(hdr));
  Serial.write(&crcBuf[2], payloadBytes);

  // Send CRC explicitly as 2 bytes (little-endian)
  uint8_t crcBytes[2];
  crcBytes[0] = (uint8_t)(crc & 0xFF);
  crcBytes[1] = (uint8_t)((crc >> 8) & 0xFF);
  Serial.write(crcBytes, 2);
}

void setup() {
  Serial.begin(921600);
  delay(200);

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);

  if (imu.begin(Wire, IMU_ADDR) != ICM_20948_Stat_Ok) {
    Serial.println("IMU ikke funnet");
    while (1) delay(1000);
  }

  Serial.println("IMU OK");
}

void loop() {
  // ===== 1) INN: fast 200 Hz sampling =====
  static uint64_t next_us = 0;
  uint64_t now = micros();
  if (now > next_us + PERIOD_US) {
  next_us = now + PERIOD_US;
  }
  if ((int64_t)(now - next_us) >= 0) {
    next_us += PERIOD_US;

    imu.getAGMT();

    if (count < BUFFER_SIZE) {
      ImuSample &s = buffer[writeIndex];

      s.node_id = NODE_ID;
      s.seq = seq++;
      s.time_us = (uint32_t)micros();
      s.ax = imu.accX();
      s.ay = imu.accY();
      s.az = imu.accZ();
      s.gx = imu.gyrX();
      s.gy = imu.gyrY();
      s.gz = imu.gyrZ();

      writeIndex = (writeIndex + 1) % BUFFER_SIZE;
      count++;
    } else {
      dropped++;
    }
  }

  // ===== 2) UT: send pakke (40 Hz) =====
  static uint32_t lastSendMs = 0;
  uint32_t nowMs = millis();

  if (nowMs - lastSendMs >= 25) { // 40 pakker/s
  lastSendMs = nowMs;  
    sendImuPacketCRC();  // -----------------------------------------
  }
}