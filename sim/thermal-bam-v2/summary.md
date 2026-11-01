# Heat thermal-bam-v2

**Max 55.7 °C** at steady state in `arm_main_body` (PLA, limit 55 °C) next to a motor dissipating 3.3 W (0.48 W of it flows into the part, case 56 °C).

- Heat-up time constant ~10 min; after 38 min the hottest point is 50.6 °C.
- Mean part temperature 28.9 °C.
- Mesh: 33,922 voxels of 1.12 mm.

## Assumptions and estimates

- material PLA: typical datasheet values (E 3.5 GPa, yield 60 MPa)
- FDM knockdown: stiffness x0.7 (walls + infill), strength x0.5 (layer lines, worst build direction); the part is modelled as a smeared isotropic solid
- voxel model: 1.12 mm cubes, volume +13% vs the STL; fillets, small holes and threads are stair-stepped or lost
- heat: one motor holding: 2 phases x (1.05 A)^2 x 1.5 ohm = 3.3 W (driver at 70% of the 1.5 A rating, phase resistance typical 1.5 ohm); the motor is one lumped body (129 J/K) that sheds heat from its own case (h x 90 cm^2) and passes the rest into the part
- motor face on a NEMA 17 square (1319 mm^2) of the part's largest flat face (normal -y), contact conductance 300 W/m^2 K
- natural convection h = 10 W/m^2 K on every other exposed face, ambient 25 °C; no radiation (adds ~5 W/m^2 K, so real temperatures are somewhat lower)
- printed conductivity 0.072 W/m K = solid 0.13 x fill 0.55
- limit 55 °C: glass transition / heat deflection of PLA, where a loaded part creeps

## Not verified

- no physical test of this part; numbers come from a coarse voxel model
- printed-material properties are typical values, not measured for this filament / printer
- motor heat and the share conducted into the mount are estimates; measure the motor case temperature under the real driver current
