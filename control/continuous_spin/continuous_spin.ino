/* Continuous free-shaft bench rotation: Arduino Uno + CNC Shield V3 + A4988.
 * Adapted from the Mechy serial_commands skeleton; keep mechy_control.h beside it.
 * Serial: 115200 baud, newline. START A (or X/Y/Z), STOP, SPEED <rpm>, PING, STATUS, STREAM 0|1.
 * MICROSTEPS must match the MS1/MS2/MS3 jumper caps under the drivers (A4988: none = 1,
 * all three = 16). Speeds are shaft RPM for a 200 step/rev (1.8 deg) motor.
 * Boots disabled. START explicitly enables motion; STOP releases ALL drivers.
 * A requires independent routing: D12 -> A STEP, D13 -> A DIR, not X/Y/Z cloning.
 * Shared D8 enables every socket; an A socket jumpered to clone X/Y/Z also moves.
 * No homing or travel limits: disconnect the motor from the robot mechanism.
 * No comms timeout: continuous operation until STOP/reset is intentional.
 * Pin reference: https://github.com/grbl/grbl/blob/master/grbl/cpu_map/cpu_map_atmega328p.h
 * A routing reference: https://makerhardware.net/wiki/doku.php?id=electronics:cnc_shield
 * Driver timing: https://www.pololu.com/file/0J450/A4988.pdf (>=1 us high/low).
 */
#include <Arduino.h>
#include <string.h>
#include <stdlib.h>
#include "mechy_control.h"

const char AXIS_NAMES[] = "XYZA";
const uint8_t AXIS_COUNT = sizeof(AXIS_NAMES) - 1;
const uint8_t STEP_PINS[] = {2, 3, 4, 12}; // CNC Shield V3 X/Y/Z/A STEP
const uint8_t DIR_PINS[] = {5, 6, 7, 13};  // CNC Shield V3 X/Y/Z/A DIR
const uint8_t ENABLE_PIN = 8;           // Shared enable, active LOW
const uint8_t DIRECTION = HIGH;         // Change to LOW to reverse (power off first)
const uint32_t BAUD = 115200;
constexpr float MOTOR_STEPS_REV = 200.0f;     // 1.8 deg stepper
constexpr uint8_t MICROSTEPS = 16;           // Set to match the jumper caps (1, 2, 4, 8, 16)
constexpr float PULSES_PER_REV = MOTOR_STEPS_REV * MICROSTEPS;
constexpr float DEFAULT_RPM = 30.0f;         // Gentle bench default
constexpr float MAX_RPM = 300.0f;            // Uno loop tops out near 16k pulses/s at 1/16
constexpr float RAMP_RPM_S = 60.0f;          // Reaches 30 RPM in 0.5 s
const uint32_t PULSE_HIGH_US = 2;        // Exceeds A4988 minimum 1 us
static_assert(MICROSTEPS == 1 || MICROSTEPS == 2 || MICROSTEPS == 4 || MICROSTEPS == 8 || MICROSTEPS == 16, "A4988 microsteps");
static_assert(DEFAULT_RPM > 0 && DEFAULT_RPM <= MAX_RPM, "Default speed out of range");
float targetRpm = DEFAULT_RPM;

mc::FixedRate controlLoop(1000UL);      // Ramp update at 1 kHz
mc::FixedRate streamLoop(500000UL);     // Optional telemetry at 2 Hz
bool running = false, streaming = false;
uint8_t axis = 0;
float pulseRate = 0.0f;
uint32_t lastStepUs = 0;

void safeState() {
  digitalWrite(ENABLE_PIN, HIGH);
  running = false;
  pulseRate = 0.0f;
  for (uint8_t i = 0; i < AXIS_COUNT; ++i) digitalWrite(STEP_PINS[i], LOW);
}

void controlStep(float dt) {
  if (!running) return;
  // Ramp toward the target both ways, so SPEED changes while running are smooth too.
  const float target = targetRpm / 60.0f * PULSES_PER_REV;
  const float stepRate = RAMP_RPM_S / 60.0f * PULSES_PER_REV * dt;
  pulseRate = pulseRate < target ? fminf(pulseRate + stepRate, target) : fmaxf(pulseRate - stepRate, target);
}

void runStepper() {
  if (!running || pulseRate < 1.0f) return;
  const uint32_t now = micros();
  const uint32_t interval = (uint32_t)(1000000.0f / pulseRate);
  if ((uint32_t)(now - lastStepUs) < interval) return;
  lastStepUs = now;                    // Never burst to catch up after serial delays
  digitalWrite(STEP_PINS[axis], HIGH);
  delayMicroseconds(PULSE_HIGH_US);     // Only pulse shaping; no delay() in the loop
  digitalWrite(STEP_PINS[axis], LOW);
}

void report(bool telemetry) {
  Serial.print(telemetry ? F("DATA") : F("OK STATUS"));
  Serial.print(F(" axis=")); Serial.print(AXIS_NAMES[axis]);
  Serial.print(F(" run=")); Serial.print(running);
  Serial.print(F(" rpm=")); Serial.print(pulseRate * 60.0f / PULSES_PER_REV, 1);
  Serial.print(F("/")); Serial.print(targetRpm, 1);
  Serial.print(F(" usteps=")); Serial.print(MICROSTEPS);
  Serial.print(F(" overruns=")); Serial.println(controlLoop.overruns);
}

void handleLine(char *line) {
  for (char *p = line; *p; ++p) if (*p >= 'a' && *p <= 'z') *p -= 32;
  char *name = strtok(line, " \t");
  if (!name) return;
  char *arg = strtok(NULL, " \t");
  char *extra = strtok(NULL, " \t");
  // STOP always stops, even if accidental extra text follows it.
  if (!strcmp(name, "STOP")) { safeState(); Serial.println(F("OK STOP")); return; }
  if (extra) { Serial.println(F("ERR PARSE extra argument")); return; }
  if (!strcmp(name, "START")) {
    const char *selected = (arg && !arg[1]) ? strchr(AXIS_NAMES, arg[0]) : NULL;
    if (!selected) {
      Serial.println(F("ERR AXIS use START X|Y|Z|A")); return;
    }
    if (running) { Serial.println(F("ERR BUSY send STOP first")); return; }
    axis = (uint8_t)(selected - AXIS_NAMES);
    pulseRate = 0.0f;
    lastStepUs = micros();
    controlLoop.started = false;
    digitalWrite(ENABLE_PIN, LOW);
    running = true;
    Serial.print(F("OK START ")); Serial.println(arg[0]);
  } else if (!strcmp(name, "SPEED")) {
    const float rpm = arg ? atof(arg) : 0.0f;
    if (rpm <= 0.0f || rpm > MAX_RPM) { Serial.println(F("ERR RANGE SPEED 1..300 rpm")); return; }
    targetRpm = rpm;
    Serial.print(F("OK SPEED ")); Serial.println(targetRpm, 1);
  } else if (!strcmp(name, "STREAM")) {
    if (!arg || (strcmp(arg, "0") && strcmp(arg, "1"))) {
      Serial.println(F("ERR PARSE STREAM 0|1")); return;
    }
    streaming = arg[0] == '1';
    Serial.print(F("OK STREAM ")); Serial.println(streaming);
  } else if (arg) Serial.println(F("ERR PARSE unexpected argument"));
  else if (!strcmp(name, "PING")) Serial.println(F("OK PONG"));
  else if (!strcmp(name, "STATUS")) report(false);
  else if (!strcmp(name, "HELP")) Serial.println(F("OK HELP START X|Y|Z|A; STOP; SPEED rpm; PING; STATUS; STREAM 0|1"));
  else Serial.println(F("ERR UNKNOWN send HELP"));
}

void readSerial() {
  static char buf[48];
  static uint8_t len = 0;
  static bool overflow = false;
  uint8_t budget = 16;                 // Keep servicing steps under incoming traffic
  while (Serial.available() > 0 && budget--) {
    const char c = (char)Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      buf[len] = '\0';
      if (overflow) Serial.println(F("ERR LONG line discarded"));
      else if (len) handleLine(buf);
      len = 0; overflow = false;
      return;                         // At most one command per loop iteration
    }
    if (c == '\0') overflow = true;   // Reject embedded NUL instead of truncating START
    else if (len < sizeof(buf) - 1) buf[len++] = c;
    else overflow = true;
  }
}

void setup() {
  digitalWrite(ENABLE_PIN, HIGH);       // Set latch before OUTPUT to avoid LOW glitch
  pinMode(ENABLE_PIN, OUTPUT);
  for (uint8_t i = 0; i < AXIS_COUNT; ++i) {
    digitalWrite(STEP_PINS[i], LOW); pinMode(STEP_PINS[i], OUTPUT);
    digitalWrite(DIR_PINS[i], DIRECTION); pinMode(DIR_PINS[i], OUTPUT);
  }
  safeState();
  Serial.begin(BAUD);
  Serial.println(F("READY continuous_spin proto=1"));
}

void loop() {
  runStepper();
  readSerial();
  const uint32_t now = micros();
  if (controlLoop.due(now)) controlStep(controlLoop.dt());
  if (streamLoop.due(now) && streaming && Serial.availableForWrite() >= 60) report(true);
}
