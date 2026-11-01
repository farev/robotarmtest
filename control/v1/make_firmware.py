"""Write control/v1/firmware/mechy_arm/ (Mechy's 4-motor arm firmware) from control/joint_limits.yaml.

`mechy control gen` needs the stock arm's params.yaml; this arm is custom, so this script fills the same
config.h from the numbers in joint_limits.yaml and copies the stock mechy_arm.ino next to it.
Run with the engine's Python:  <mechy>/engine/.venv/bin/python control/v1/make_firmware.py

No switches are mounted yet, so the firmware is told where the arm is with SETPOS (the app's
"Drive real arm" does this from the home pose). Do not send HOME: with no switches it would take the
power-on position as the stretched pose.
"""
from __future__ import annotations

import math
import shutil
from pathlib import Path

import yaml
from mechy.control.boards import get_board
from mechy.control.firmware import TEMPLATES, render_config_h

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent.parent
LIMITS = yaml.safe_load((PROJECT / "control" / "joint_limits.yaml").read_text())

# Bench-safe caps per motor (steps/s, steps/s^2 at 16 microsteps): one motor rev/s, reached in 1 s.
# J2 (12:1, holding the arm against gravity) therefore tops out near 30 deg/s, J1/J3 near 60 deg/s.
V_MAX_STEPS = 3200.0
A_MAX_STEPS = 3200.0
SOFT_MARGIN_DEG = 2.0
HOME_DEG = [0.0, 45.0, -90.0, 0.0]   # design/v1/joints.yaml home pose (= assembly.yaml)

board = get_board("uno_cnc")
joints = LIMITS["joints"]
slots = {s["socket"]: s for s in board["slots"]}
motors = []
for i, j in enumerate(joints):
    s = slots[j["shield_axis"]]
    sw = board["switches"][i]
    motors.append({
        "name": j["name"], "socket": s["socket"], "drives": j["name"],
        "step_pin": s["step"], "step_port": s["step_port"], "step_bit": s["step_bit"],
        "dir_pin": s["dir"], "enable_pin": s["enable"],
        "switch_pin": sw["pin"], "switch_label": sw["label"],
        "steps_per_rad": j["steps_per_deg"] * 180.0 / math.pi,
        "steps_per_rev_motor": LIMITS["steps_per_motor_rev"], "pulley_teeth": round(20 * j["ratio"]),
        "v_max_steps": V_MAX_STEPS, "a_max_steps": A_MAX_STEPS,
    })

rad = math.radians
eye = [[1.0 if r == c else 0.0 for c in range(4)] for r in range(4)]
cfg = {
    "variant": "v1", "board": "uno_cnc", "board_title": board["title"], "mcu": board["mcu"],
    "board_define": board["define"], "serial_baud": board["serial_baud"],
    "tick_hz": board["tick_hz"], "ticks_per_update": 20, "update_hz": board["tick_hz"] / 20,
    "microsteps": LIMITS["microsteps"], "microstep_jumpers": "MS1 H, MS2 H, MS3 H (all three jumpers)",
    "max_step_rate_hz": V_MAX_STEPS,
    "mapping": eye, "mapping_inv": eye, "mapping_source": "control/joint_limits.yaml (relative joints, no coupling)",
    "motors": motors, "dir_invert": [0, 0, 0, 0],
    "soft_limits_rad": [[rad(j["limits_deg"][0] + SOFT_MARGIN_DEG), rad(j["limits_deg"][1] - SOFT_MARGIN_DEG)] for j in joints],
    "estop_pin": board["estop"]["pin"], "estop_label": board["estop"]["label"],
    "joint_names": [j["name"] for j in joints],
    "ready_pose_rad": [rad(d) for d in HOME_DEG],
    "homing": {
        "source": "none mounted yet: SETPOS from the home pose", "order": [0, 1, 2, 3],
        "order_names": [j["name"] for j in joints], "kind": ["none"] * 4, "coord_motor": [None] * 4,
        "coord": [f"q{i}" for i in range(4)], "dir": [-1, -1, -1, -1], "pos_rad": [rad(d) for d in HOME_DEG],
        "travel_rad": [rad(360)] * 4, "fast_rad_s": rad(20), "slow_rad_s": rad(5), "backoff_rad": rad(5),
        "window_rad": rad(10), "margin_rad": rad(10), "switch_active_low": True,
    },
}

out = HERE / "firmware" / "mechy_arm"
out.mkdir(parents=True, exist_ok=True)
(out / "config.h").write_text(render_config_h(cfg, "python control/v1/make_firmware.py"))
shutil.copy(TEMPLATES / "mechy_arm.ino", out / "mechy_arm.ino")
print(f"wrote {out.relative_to(PROJECT)}/config.h and mechy_arm.ino")
