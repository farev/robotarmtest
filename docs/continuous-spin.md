# Continuous motor spin test

Sketch: `control/continuous_spin/continuous_spin.ino`. Keep `mechy_control.h` in the same folder. Target: Arduino Uno / board ID `uno`. No third-party libraries.

1. Use a motor with its shaft free from the arm mechanism; this sketch has no travel limits. Check which shield output the motor uses: X, Y, Z or A. For A, use the independent routing described below.
2. With power off, check that the A-axis clone jumpers will not make another motor follow your chosen axis. D8 is shared: START energizes all installed drivers; STOP releases them all. The photo does not establish the jumper routing.
3. Set the A4988 current limit for the motor before testing. The project records 0.9 A/phase, but the exact motor datasheet, sense resistors and Vref setting remain unverified. USB supplies the Uno; the shield needs its separate motor supply. Never unplug the motor while powered.
4. Open the sketch in Arduino IDE, select **Arduino Uno**, choose its USB port, then upload. Alternatively select `control/continuous_spin` and board `uno` in the Electronics panel and flash it yourself. Upload replaces the previous sketch.
5. Open Serial Monitor at **115200 baud**, **Newline**. Reset the board if needed to see `READY continuous_spin proto=1`. Send `PING` (expect `OK PONG`), then `STATUS` (expect `run=0`).
6. Send **`START A`** for the A socket with independent routing configured. `START X`, `START Y` and `START Z` remain available for those sockets. Check a short initial movement and send `STOP`. Once correct, send START again to run continuously. `STOP` stops pulses and disables the drivers immediately; reset also returns to stopped.

The target is **200 STEP pulses/s**, approached over about 2 seconds. It continues without periodic commands until STOP or reset. Actual speed depends on the microstep jumpers. For an assumed 200-full-step/revolution motor, calculated speed is 60 RPM at full step, 7.5 RPM at 1/8, or 3.75 RPM at 1/16. These are calculated values, not measured speed.

Change `TARGET_PULSES_S` to change speed (1..1000 allowed by the sketch) or change `DIRECTION` from HIGH to LOW to reverse it. The numerical cap is a software bound, not a validated speed for this motor and load. `STREAM 1` enables status twice per second; `STREAM 0` turns it off. Changing axes requires STOP first.

## A-axis routing

With USB and motor power disconnected, set the shield A-axis routing jumpers to **D12 -> A STEP** and **D13 -> A DIR**. Remove any A-to-X/Y/Z cloning selection; never bridge multiple source outputs together. These are the A routing selectors, not the microstep jumpers underneath the driver. Follow the board labels or schematic rather than guessing physical jumper positions. The attached photo does not verify these connections.

The [Maker Store CNC Shield guide](https://makerhardware.net/wiki/doku.php?id=electronics:cnc_shield) documents independent fourth-axis operation on D12/D13. If A remains cloned to X/Y/Z, `START A` will not drive it; commanding the cloned source also drives that source socket.

## Evidence and limits

- Existing brief and gallery identify Uno R3, CNC Shield V3, A4988 modules and 42SHDC3026-15B motors. The supplied photo confirms four modules with heatsinks; chip markings and motor label are obscured.
- Pin mapping X 2/5, Y 3/6, Z 4/7, common enable 8: [upstream GRBL Uno pin map](https://github.com/grbl/grbl/blob/master/grbl/cpu_map/cpu_map_atmega328p.h).
- Current limiting, separate motor power and no hot-plugging: [Pololu A4988 carrier documentation](https://www.pololu.com/product/1182). Clone resistor values must be checked on the actual board.
- STEP timing uses 4 us high, exceeding the 1 us minimum in the [Allegro A4988 datasheet](https://www.pololu.com/file/0J450/A4988.pdf). Timing has not been measured on hardware.
- An Arduino Uno R3 is now detected on `/dev/cu.usbmodem2101`. No flash or motor run was performed. Hardware wiring, supply, current limit and microstepping remain unverified.

## Compilation result

A-axis revision: `hw_build(sketch="control/continuous_spin", board="uno")` returned `ok: true`. RAM 331/2048 bytes (16.2%); flash 5510/32256 bytes (17.1%). No warnings in the successful log. Host pin simulation passed for START A pulsing only D12, STATUS A, stopped boot/STOP, invalid axis rejection, X/Y/Z/A regression and lowercase commands. Simulation does not verify physical wiring or timing. No hardware run performed. Build record: `control/continuous_spin/build-result.json`.
