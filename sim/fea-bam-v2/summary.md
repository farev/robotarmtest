# Stress (FEA) fea-bam-v2

**Safety factor 4.21** (target 2) on `arm_lower_shank_140` in PLA (printed) under 16.9 N.

- Max von Mises 7.1 MPa against an allowable 30 MPa.
- Max deflection 1.332 mm; tip stiffness 14.0 N/mm.
- Load case: shoulder motor stalled against a blocked tool: 0.45 N m holding x 5.625 gear = 2.53 N m at the joint, over the 150 mm span.
- Mesh: 35,577 voxels of 1.05 mm; mass 27.3 g (print_list.csv est_grams (CAD shells + infill)).

## Assumptions and estimates

- material PLA: typical datasheet values (E 3.5 GPa, yield 60 MPa)
- FDM knockdown: stiffness x0.7 (walls + infill), strength x0.5 (layer lines, worst build direction); the part is modelled as a smeared isotropic solid
- voxel model: 1.05 mm cubes, volume +2% vs the STL; fillets, small holes and threads are stair-stepped or lost
- held rigidly over the 13 mm at the max end of the x axis (the end with more material, taken as the hub / mount; set --opt mount=min|max)
- load: shoulder motor stalled against a blocked tool: 0.45 N m holding x 5.625 gear = 2.53 N m at the joint, over the 150 mm span, spread over the far 13 mm, along -y (the part's middle dimension: the plane it swings in)
- linear elastic, small deflection; no buckling, fatigue or creep
- peak stress excludes the nodes touching the idealised rigid clamp (a singular corner); with them it is 7.1 MPa

## Not verified

- no physical test of this part; numbers come from a coarse voxel model
- printed-material properties are typical values, not measured for this filament / printer
- contact, bolts, bearings and the real joint clamp are idealised as a rigid hold
- the load case is the stall / crash bound, not a measured duty cycle
