# Gripper reference study — 2026-10-30

## References opened

- [Robotiq 2F manual](https://assets.robotiq.com/website-assets/support_documents/document/online/2F-85_2F-140_Instruction_Manual_Gen_HTML_20190524.zip/2F-85_2F-140_Instruction_Manual_Gen_HTML/Content/1.%20General_Presentation.htm): parallel and encompassing contact modes, removable finger sets. Inspiration for broad contact lands and a clear jaw silhouette; this redesign does not copy its adaptive linkage or claim adaptive grasping.
- [InstaGrasp, Zhou and Spiers](https://arxiv.org/abs/2305.17029): modular PLA/TPU printed structure, compliant finger pads, replaceable parts. Inspiration for separate TPU wear pads on rigid jaws. No force or durability result from the paper transfers to BAM.
- [Grković adaptive gripper](https://github.com/Grkila/Adaptive-Gripper-with-Micro-Vibration-Based-Slip-Detection): a parallel rack drive and TPU contact insert, with active slip detection. Inspiration for TPU contact; BAM retains its existing two-slider crank/wire drive and has no slip sensing.
- [SSG-48](https://github.com/Source-Robotics/SSG-48-adaptive-electric-gripper): a complete open-source force-feedback gripper. Its controller and actuator would expand this task's cost and mass, so they were not adopted.

## Design decisions

Keep the low-mass MG90S shortlist and measured dovetail interface. Replace the narrow old fingertips with wider, longer ribbed jaws. Use screw-retained TPU pads with flat lands for box-shaped objects and a shallow central V for round objects. Place screws and nuts below the contact surface. Print fingers on their sides so the jaw bending load lies in the layer plane; pads print back-face down.

The imported viewer contains a 28BYJ motor despite servo-labelled metadata, and its base row is approximately 1 mm offset from the wrist holes. The new cartridge uses an actual MG90S envelope model and corrected mounting axes. Servo clone and horn dimensions remain unverified.

Original guide geometry: Florin Tobler / 20sffactory Community Robot Arm, CC BY 4.0. New finger/rib/pad geometry is project work.
