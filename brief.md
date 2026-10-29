# RobotArmTest

## Goal

I want to build a robot arm, and I have the following mechatronics components: [10/24/26, 1:03:08 PM] Carlos Balbuena: Electronics & Control
Microcontroller: Arduino Uno (programmed via Arduino IDE / PlatformIO)

Shield: CNC Shield V3 expansion board

Drivers: A4988 stepper motor driver modules (with heatsinks installed)

Capacitor: 100 µF, 50 V electrolytic capacitor

Power Supply: 24 V, 6 A DC power supply with barrel jack/terminal adapter
[10/24/26, 1:03:15 PM] Carlos Balbuena: Motors
Type: NEMA 17 bipolar stepper motors

Specific Model: 42SHDC3026-15B (rated around 0.9 A per phase, 4-wire connection)

I know generally how to wire everything up, and I have a friend working on the code part. I need to focus on designing all the 3D-printable components, basically the entire structure of the arm. And for the design, I wanted to have a base, two elbows, and then a hand. Since I have four motors:

* One motor would be for the base, for rotating the entire arm.
* We will have one motor at each of the elbows.
* One motor to rotate the hand.

 I will probably get another servo motor for the gripper itself.

I have access to a Bambu Lab X1E 3D printer. And I ideally want to print everything in PLA. And also, I want the biggest part that we need 3D printed to fit in the base of the 3D printer, so we should design the arm around those constraints. Can you help me actually create the 3D printable design for this robot arm, including all of the motor encasings, frame, and everything needed.
