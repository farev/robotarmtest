/* Adapted from knowledge/firmware/examples/serial_commands/serial_commands.ino.
 * Task-specific exception: PlatformIO main.cpp only (allowed output list); no
 * mechy_control.h copied, no control algorithm needed. Unsigned millis timing
 * replaces FixedRate for this standalone 1-second LED test. No arm control.
 * CNC Shield V3: D8 active-low enable; STEP D2/3/4, optional A STEP D12.
 * D13 is also spindle direction / optional A direction: do not attach a spindle.
 * Software safe state begins at setup; reset/bootloader pin states are not controlled.
 */
#include <Arduino.h>
#include <string.h>

constexpr uint8_t ENABLE_PIN = 8;
constexpr uint8_t STEP_PINS[] = {2, 3, 4, 12};
constexpr uint32_t HALF_PERIOD_MS = 1000; // Task-specified default.
bool ledOn = true;
bool streaming = true;
uint32_t lastChange = 0;

void heartbeat() {
  Serial.print(F("DATA t_ms=")); Serial.print(millis());
  Serial.print(F(" LED=")); Serial.println(ledOn ? F("ON") : F("OFF"));
}
void handleLine(char *line) {
  for (char *p = line; *p; ++p) if (*p >= 'a' && *p <= 'z') *p -= 32;
  if (!strcmp(line, "PING")) Serial.println(F("OK PONG"));
  else if (!strcmp(line, "STATUS")) {
    Serial.print(F("OK STATUS drivers=DISABLED t_ms=")); Serial.print(millis());
    Serial.print(F(" LED=")); Serial.println(ledOn ? F("ON") : F("OFF"));
  } else if (!strcmp(line, "STREAM 0")) {
    streaming = false; Serial.println(F("OK STREAM 0"));
  } else if (!strcmp(line, "STREAM 1")) {
    streaming = true; Serial.println(F("OK STREAM 1"));
  } else Serial.println(F("ERR UNKNOWN"));
}
void readSerial() {
  static char buf[32];
  static uint8_t len = 0;
  static bool overflow = false;
  // Bounded work keeps serial traffic from starving the blink timer.
  for (uint8_t n = 0; n < 32 && Serial.available(); ++n) {
    char c = static_cast<char>(Serial.read());
    if (c == '\r') continue;
    if (c == '\n') {
      buf[len] = '\0';
      if (overflow) Serial.println(F("ERR LONG"));
      else if (len) handleLine(buf);
      len = 0; overflow = false;
    } else if (len < sizeof(buf)-1) buf[len++] = c;
    else overflow = true;
  }
}
void setup() {
  digitalWrite(ENABLE_PIN, HIGH); // Set latch before output: never command enable.
  pinMode(ENABLE_PIN, OUTPUT);
  for (uint8_t pin : STEP_PINS) {
    digitalWrite(pin, LOW); pinMode(pin, OUTPUT);
  }
  digitalWrite(LED_BUILTIN, HIGH); pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);
  Serial.println(F("READY uno-blink proto=1"));
  lastChange = millis();
  heartbeat();
}
void loop() {
  uint32_t now = millis();
  if (static_cast<uint32_t>(now-lastChange) >= HALF_PERIOD_MS) {
    lastChange = now;
    ledOn = !ledOn;
    digitalWrite(LED_BUILTIN, ledOn ? HIGH : LOW);
    if (streaming) heartbeat();
  }
  readSerial();
}
