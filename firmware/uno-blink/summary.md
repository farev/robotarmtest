| What | Where |
|---|---|
| Firmware | firmware/uno-blink/src/main.cpp |
| Build configuration | firmware/uno-blink/platformio.ini |
| Commands, pin sharing, serial transcript | firmware/uno-blink/README.md |
| Local summary | firmware/uno-blink/summary.md |

**Result: compiled, flashed and serial-verified.** Standalone blink replaces the loaded sketch; no arm control. Uno R3 exact USB identity rechecked before upload: /dev/cu.usbmodem2101, serial 75131313832351018082. PlatformIO 6.2.0.

| Check | Expected | Got | PASS/FAIL |
|---|---|---|---|
| Build | Success; RAM <75% | 262/2048 B RAM (12.8%); 2834/32256 B flash (8.8%); no errors | PASS |
| Upload | Verified write | 2834 bytes verified, ATmega328P 0x1e950f | PASS |
| Serial cycles | ≥3 at 115200 baud | READY; ON/OFF at 0/1000/2000/3000/4000/5000/6000/7000 ms | PASS |
| Timing | 1 s edges, 2 s cycles | Seven 1000 ms intervals; three complete 2000 ms cycles, board-reported timestamps | PASS |
| PING | OK PONG | OK PONG | PASS |
| Motor outputs, code review | Disabled, no steps | D8 HIGH; D2/3/4/12 LOW throughout application | PASS |

CNC V3 documentation identifies D13 sharing with spindle/A direction; no attached spindle is documented. A stale 9600-baud Mechy monitor blocked initial reads; stopped that process, then captured via hw_read for 9 s and tested PING. No additional serial recovery tool exists; process inspection/termination was needed. Listed inbox missing; drivers.yaml empty. README includes reproducible commands and source link.

## Not verified

- Physical LED light (no user confirmation); electrical outputs, shield wiring and reset/bootloader behavior.
- Independent timing calibration; arm operation.

## Open decisions

- None. Optional user observation of the L LED remains separate.
