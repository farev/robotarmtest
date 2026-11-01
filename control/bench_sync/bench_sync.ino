/* Bench sync: two bench motors follow the CAD Simulate pose. Arduino Uno + CNC Shield V3 + A4988.
 * Y socket = shoulder, A socket = base yaw (A routed independently: D12 -> A STEP, D13 -> A DIR).
 * Serial: 115200 baud, newline. POS <shoulder_deg> <base_deg>, ZERO, ENABLE 0|1, PING, STATUS.
 * POS is a joint angle relative to the ready pose; each axis tracks it with a speed and acceleration
 * limit, so a stream of poses (about 25 per second from the app) turns into smooth motion.
 * ZERO: the shafts' current angle is the ready pose. Boots disabled; ENABLE 1 energises both drivers.
 * MICROSTEPS must match the jumper caps under the drivers (A4988: all three = 16).
 * No homing or travel limits: bench motors only, not connected to the arm.
 */
#include <Arduino.h>
#include <stdlib.h>
#include <string.h>

const uint8_t N = 2;
const char *NAMES[N] = {"Y", "A"};
const uint8_t STEP_PINS[N] = {3, 12};   // CNC Shield V3 Y / A STEP
const uint8_t DIR_PINS[N] = {6, 13};    // CNC Shield V3 Y / A DIR
const uint8_t ENABLE_PIN = 8;           // Shared enable, active LOW
const uint32_t BAUD = 115200;
constexpr float MICROSTEPS = 16.0f;
constexpr float STEPS_PER_DEG = 200.0f * MICROSTEPS / 360.0f;
// Motor turns per joint turn. 1 so each shaft mirrors its joint on the bench (the base is direct drive).
constexpr float GEAR[N] = {1.0f, 1.0f};
constexpr float MAX_DEG_S = 360.0f;     // shaft speed limit
constexpr float ACCEL_DEG_S2 = 1500.0f; // shaft acceleration limit
constexpr float LIMIT_DEG = 360.0f;     // POS beyond this is refused
const uint32_t PULSE_HIGH_US = 2;       // A4988 needs >= 1 us

long pos[N] = {0, 0};          // steps
long target[N] = {0, 0};       // steps
float vel[N] = {0, 0};         // steps/s, signed
uint32_t lastStep[N] = {0, 0};
uint32_t lastControl = 0;
bool enabled = false;

void setEnabled(bool on) {
  enabled = on;
  digitalWrite(ENABLE_PIN, on ? LOW : HIGH);
  if (!on) for (uint8_t i = 0; i < N; ++i) { vel[i] = 0; target[i] = pos[i]; }
}

// 1 kHz: pick each axis's speed so it stops on the target (v^2 = 2 a d), within the limits.
void control(float dt) {
  const float vmax = MAX_DEG_S * STEPS_PER_DEG, a = ACCEL_DEG_S2 * STEPS_PER_DEG;
  for (uint8_t i = 0; i < N; ++i) {
    const long err = target[i] - pos[i];
    float want = sqrtf(2.0f * a * fabsf((float)err));
    if (want > vmax) want = vmax;
    if (err < 0) want = -want;
    if (err == 0) want = 0;
    const float dv = a * dt;
    vel[i] = vel[i] < want ? fminf(vel[i] + dv, want) : fmaxf(vel[i] - dv, want);
  }
}

void stepAxes() {
  if (!enabled) return;
  const uint32_t now = micros();
  for (uint8_t i = 0; i < N; ++i) {
    const float v = fabsf(vel[i]);
    if (v < 1.0f || pos[i] == target[i]) continue;
    if ((uint32_t)(now - lastStep[i]) < (uint32_t)(1000000.0f / v)) continue;
    lastStep[i] = now;
    const bool fwd = vel[i] > 0;
    digitalWrite(DIR_PINS[i], fwd ? HIGH : LOW);
    digitalWrite(STEP_PINS[i], HIGH);
    delayMicroseconds(PULSE_HIGH_US);
    digitalWrite(STEP_PINS[i], LOW);
    pos[i] += fwd ? 1 : -1;
  }
}

void status() {
  Serial.print(F("OK STATUS enabled=")); Serial.print(enabled);
  for (uint8_t i = 0; i < N; ++i) {
    Serial.print(' '); Serial.print(NAMES[i]); Serial.print('=');
    Serial.print(pos[i] / (STEPS_PER_DEG * GEAR[i]), 1);
  }
  Serial.println();
}

void handle(char *line) {
  for (char *p = line; *p; ++p) if (*p >= 'a' && *p <= 'z') *p -= 32;
  char *cmd = strtok(line, " \t");
  if (!cmd) return;
  if (!strcmp(cmd, "POS")) {
    float deg[N];
    for (uint8_t i = 0; i < N; ++i) {
      char *arg = strtok(NULL, " \t");
      if (!arg) { Serial.println(F("ERR PARSE POS shoulder_deg base_deg")); return; }
      deg[i] = atof(arg);
      if (fabsf(deg[i]) > LIMIT_DEG) { Serial.println(F("ERR RANGE")); return; }
    }
    if (!enabled) return;                 // quiet: the app streams poses
    for (uint8_t i = 0; i < N; ++i) target[i] = lroundf(deg[i] * GEAR[i] * STEPS_PER_DEG);
  } else if (!strcmp(cmd, "ZERO")) {
    for (uint8_t i = 0; i < N; ++i) { pos[i] = target[i] = 0; vel[i] = 0; }
    Serial.println(F("OK ZERO"));
  } else if (!strcmp(cmd, "ENABLE")) {
    char *arg = strtok(NULL, " \t");
    setEnabled(arg && arg[0] == '1');
    Serial.print(F("OK ENABLE ")); Serial.println(enabled);
  } else if (!strcmp(cmd, "PING")) Serial.println(F("OK PONG"));
  else if (!strcmp(cmd, "STATUS")) status();
  else Serial.println(F("ERR UNKNOWN POS|ZERO|ENABLE|PING|STATUS"));
}

void readSerial() {
  static char buf[48];
  static uint8_t len = 0;
  uint8_t budget = 16;                    // keep stepping under incoming traffic
  while (Serial.available() > 0 && budget--) {
    const char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') { buf[len] = '\0'; if (len) handle(buf); len = 0; return; }
    if (len < sizeof(buf) - 1) buf[len++] = c;
  }
}

void setup() {
  digitalWrite(ENABLE_PIN, HIGH);         // latch before OUTPUT: no LOW glitch
  pinMode(ENABLE_PIN, OUTPUT);
  for (uint8_t i = 0; i < N; ++i) {
    digitalWrite(STEP_PINS[i], LOW); pinMode(STEP_PINS[i], OUTPUT);
    pinMode(DIR_PINS[i], OUTPUT);
  }
  Serial.begin(BAUD);
  Serial.println(F("READY bench_sync proto=1"));
}

void loop() {
  stepAxes();
  readSerial();
  const uint32_t now = micros();
  if ((uint32_t)(now - lastControl) >= 1000) {
    control((now - lastControl) / 1e6f > 0.01f ? 0.001f : (now - lastControl) / 1e6f);
    lastControl = now;
  }
  stepAxes();
}
