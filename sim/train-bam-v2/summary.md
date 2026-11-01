# Train a policy: train-bam-v2

- **Success: 100.0%** on 5,000 fresh reach episodes (target 90%, met); generation 1: 0.1%. Success = within 10 mm and under 5 cm/s at the end.
- 100,000 arms per generation (501 policies x 200 envs), 75 generations, 300,600,000 env steps in 85 s = **3,528,810 env steps/s** (28,230,478 physics steps/s, 14 processes).
- Mean time to target: 0.64 s.
- MuJoCo cross-check (256 episodes on arm.xml): success 100.0% here vs 100.0% in MuJoCo, outcomes agree 100%, tool paths differ by 1.1 mm on average (95th pct 5.2 mm).

## Not verified

- Simulation only: the batched model is rigid links, ideal belts, no backlash, no step loss; the stepper is modelled as a torque-limited position servo with gravity feed-forward (pull-out curve from hw/motors.yaml, datasheet-typical).
- No collisions (links with the table or each other) are simulated; the tool going below the table is penalised and counted.
- The policy reads perfect joint angles, speeds and target positions; real encoders/vision add noise and latency.
- Observations include the damped-least-squares joint step toward the goal (a textbook feature) and commanded speed scales with distance inside 3 cm of the goal; catch is told the aim point.
- Not run on hardware.
