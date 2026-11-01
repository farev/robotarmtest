| What | Where |
|---|---|
| Blink source | src/main.cpp |
| PlatformIO configuration | platformio.ini |
| Verification result | summary.md |
| Planner result | ../../tasks/summaries/T109-controls-uno-blink.md |

The standalone blink test was compiled, uploaded and verified over serial on 2026-10-30. It replaces the previous sketch; it implements no arm controls. Look for the Uno's small LED labelled **L**, near digital pin 13; the power LED stays on. The intended pattern is 1 second on, 1 second off. A shield may obscure it. Physical light has not been observed by the agent or confirmed by the user.

## Reproduce

From the project root, with the confirmed Uno connected:

```sh
/Users/Carlo/.mechy/platformio/bin/pio run -d firmware/uno-blink -e uno
/Users/Carlo/.mechy/platformio/bin/pio run -d firmware/uno-blink -e uno -t upload --upload-port /dev/cu.usbmodem2101
/Users/Carlo/.mechy/platformio/bin/pio device monitor --port /dev/cu.usbmodem2101 --baud 115200
```

Equivalent Mechy calls: `hw_boards({})`, `hw_build({sketch:"firmware/uno-blink",board:"uno"})`, `hw_flash({sketch:"firmware/uno-blink",board:"uno",port:"/dev/cu.usbmodem2101"})`, `hw_read({port:"/dev/cu.usbmodem2101",baud:115200,seconds:9})`. Recheck identity before uploading. Opening serial can reset the Uno. Use one serial monitor at a time.

Commands, newline-terminated and case-insensitive: `PING`, `STATUS`, `STREAM 0`, `STREAM 1`. Streaming is enabled on startup. STREAM changes telemetry only; the LED keeps blinking. No command enables drivers.

## Pin sharing and scope

The [CNC Shield V3 supplier documentation, schematic and GRBL pin diagram](https://4.imimg.com/data4/FA/NC/MY-1833510/arduino-cnc-shield-version-3-0.pdf) documents D12/D13 fourth-axis sharing and spindle connections. D13/LED_BUILTIN also serves spindle direction / optional A direction. D8 is shared active-low driver enable; firmware sets its latch HIGH before configuring OUTPUT. D2/D3/D4/D12 STEP outputs stay LOW, including optional independent A STEP. No step pulses are programmed. Blink changes direction only on a shield with the documented mapping, while drivers are disabled. No spindle or other D13 attachment is documented; do not use this test with such an attachment. Reset/bootloader electrical states and actual shield wiring were not measured.

`hw/drivers.yaml` contains `drivers: []` and `controller: null`; hardware context came from the supplied task brief. The listed inbox file is absent. No other project firmware was edited. Source adapts the reference serial_commands skeleton; task-specific main.cpp and no additional library/header comply with the explicit output list. No motion algorithms or control generator are appropriate for this LED-only test.

## Observed results

Board checked twice: Arduino Uno R3, exact USB match, VID:PID 2341:0043, serial 75131313832351018082, port /dev/cu.usbmodem2101. PlatformIO 6.2.0; Atmel AVR platform 5.3.0; Arduino AVR framework 5.4.0; AVR compiler 7.3.0.

| Check | Expected | Got | PASS/FAIL |
|---|---|---|---|
| Compile | Success, RAM below 75% | Success; RAM 262/2048 B (12.8%), flash 2834/32256 B (8.8%) | PASS |
| Upload | Flash write and readback match | 2834 bytes verified; ATmega328P signature 0x1e950f | PASS |
| Runtime serial | READY and at least 3 complete cycles | READY; 3 complete ON→OFF→ON cycles, 0–6000 ms | PASS |
| Edge interval | 1000 ms firmware timestamp difference | Seven consecutive differences of 1000 ms | PASS |
| Full period | 2000 ms | 2000 ms for each of 3 complete cycles | PASS |
| Command response | PING → OK PONG | OK PONG from hw_send | PASS |
| Driver safety, source review | D8 HIGH; STEP outputs LOW | Set at setup, never changed | PASS — software only |
| Physical LED light | Visible blinking | No visual observation | UNVERIFIED |

Actual `hw_read` capture (115200 baud, 9 s request):

```text
READY uno-blink proto=1
DATA t_ms=0 LED=ON
DATA t_ms=1000 LED=OFF
DATA t_ms=2000 LED=ON
DATA t_ms=3000 LED=OFF
DATA t_ms=4000 LED=ON
DATA t_ms=5000 LED=OFF
DATA t_ms=6000 LED=ON
DATA t_ms=7000 LED=OFF
```

Initial 9 s and 10 s captures returned no lines because an existing Mechy monitor held the port at 9600 baud. Its identified monitor process was stopped; the subsequent direct Mechy capture and PING succeeded. No firmware change was needed. Timestamps are observed board-reported milliseconds, not independently calibrated wall-clock timing.

## Not verified

- Physical LED illumination; electrical driver disable, actual shield/jumper wiring and reset/bootloader pin states.
- Independent oscillator timing accuracy; arm operation (not implemented).

## Open decisions

- None required for this test. User may confirm visible L LED blinking separately.
