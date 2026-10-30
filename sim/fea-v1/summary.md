# Stress (FEA) fea-v1

**Safety factor 42.22** (target 2) on `forearm` in PETG (printed) under 10.0 N.

- Max von Mises 0.6 MPa against an allowable 25 MPa.
- Max deflection 0.100 mm; tip stiffness 136.5 N/mm.
- Load case: generic 10 N (~1 kg) at the far end: not recognised as an arm link (set --opt load_n).
- Mesh: 36,568 voxels of 1.57 mm; mass 86.4 g (print_list.csv est_grams (CAD shells + infill)).

## Assumptions and estimates

- material PETG: typical datasheet values (E 2.1 GPa, yield 50 MPa)
- FDM knockdown: stiffness x0.7 (walls + infill), strength x0.5 (layer lines, worst build direction); the part is modelled as a smeared isotropic solid
- voxel model: 1.57 mm cubes, volume +4% vs the STL; fillets, small holes and threads are stair-stepped or lost
- held rigidly over the 13 mm at the max end of the x axis (the end with more material, taken as the hub / mount; set --opt mount=min|max)
- load: generic 10 N (~1 kg) at the far end: not recognised as an arm link (set --opt load_n), spread over the far 13 mm, along -y (the part's middle dimension: the plane it swings in)
- linear elastic, small deflection; no buckling, fatigue or creep
- peak stress excludes the nodes touching the idealised rigid clamp (a singular corner); with them it is 0.7 MPa

## Not verified

- no physical test of this part; numbers come from a coarse voxel model
- printed-material properties are typical values, not measured for this filament / printer
- contact, bolts, bearings and the real joint clamp are idealised as a rigid hold
- the load case is the stall / crash bound, not a measured duty cycle
