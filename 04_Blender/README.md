# Blender models

Python scripts that build the pipette in Blender (tested with 5.2) from the parts in
`01_Hardware`, plus two redesign variants explored in this fork. The scripts are the source of
truth; the `.blend` files they produce are not committed.

```
blender --python 04_Blender/build_pipette.py        # the original design
blender --python 04_Blender/variant_raise_bed.py    # fixed head, lever lifts the bed
blender --python 04_Blender/variant_motor_lift.py   # fixed head, motorized lead-screw lift (chosen)
blender -b --python 04_Blender/export_motor_lift_parts.py   # write the motor-lift printed parts as STL
```

You can also open a script in Blender's Text Editor and use **Run Script**. Add `-b` to build
without the UI. Units are millimeters (Z up, front = -Y).

## What each script builds

| Script | Design | Renders |
|---|---|---|
| `build_pipette.py` | The original: the lever lowers the whole head. | `original_*.jpg` |
| `variant_raise_bed.py` | Head fixed; the geared lever raises the bed through short links arranged as a toggle that locks at the top. Handle on the right. | `lever_lift_*.jpg` |
| `variant_motor_lift.py` | Head fixed; one NEMA17 lifts the bed on two T8x2 screws through a GT2 belt, and one motor (48 mm body) on a plate across the top ring drives all four T8x2 plunger screws through a second belt. Anti-backlash plunger nuts, a 2020 stiffening frame on the drive plate, idler tensioners, a lift home switch, optical plunger home sensors with a level check, a tip ejector, and a swappable syringe cartridge that slides in at the front like a drawer. The control box lies in front of the base with its screen panel sloped 10 deg toward the user (`CONTROL_SLOPE_DEG`). Its plates come from `01_Hardware/MotorLift/make_dxf.py`, which also holds the layout numbers. Firmware: `02_Software/arduino/MotorLift`. | `motor_lift_*.jpg` |

The variants build on `build_pipette.py`, so it has to stay in the same folder.

## Where the geometry comes from

- **Imported directly:** the printed parts from `ToPrint-STL` and the laser-cut parts from
  `ToLaserCut-DXF` (lines, arcs and holes, extruded to 3 mm steel).
- **Modeled:** 2020 T-slot extrusion (B-type 6 mm slot profile), the corner brackets' M5 bolts
  and T-nuts, MGN9H rails and carriages, NEMA17 motors, T8 screws and nuts,
  syringes, tips, the well plate, bearings, pulleys and belts.
- **Layout:** there is no assembly file in the repo, so placement was reconstructed from the
  creator's build video (youtu.be/2TTu-Lkz2Eo). Part shapes are exact; frame height (400 mm; 430 mm in the motor-lift variant, HEAD_RAISE),
  syringe and tip dimensions, and some mounting positions are estimates.
- **Lever variant:** the shorter gear-arm and longer handle are derived from the stock
  `lever_cutout*.DXF` outlines by shifting only their straight sections.
- **Motor-lift variant:** its four laser-cut plates are imported from the generated DXFs in
  `01_Hardware/MotorLift/ToLaserCut-DXF`, and its new printed parts are modeled as closed solids
  so `export_motor_lift_parts.py` can write them straight to STL.

## Checks

Both variants include `collision_report()`, which sweeps every moving part through its full
travel and tests it against the rest of the model, allowing only intended contacts (screws in
nuts, carriages on rails, and so on). Both report no collisions. `variant_motor_lift.py` also
reports the belt loop lengths across the tensioner's adjustment range: 338.9-344.4 mm (lift) and
541.6-547.5 mm (plunger).

Each variant keyframes a full cycle as it builds; scrub the timeline to watch it. The motor-lift
variant plays a complete run (`CYCLE`, 680 frames):
1. It starts with no tips. A tip rack goes into the nest, the bed rises 64 mm to press the nozzles
   into the tips, and the tips stay on the nozzles when the bed goes down. The empty rack then
   slides out under them.
2. A reservoir replaces the rack, and the plunger draws 100 uL per channel with the tips in the
   liquid.
3. A 96-well plate replaces the reservoir, and the plunger dispenses into its wells.
4. A waste tray replaces the plate. The plunger runs 11.5 mm past home, and the tilted ejector
   plate strips the tips a row at a time, front row first; they drop into the tray.
5. The D-shaft levers open (the flats come up and the plunger carrier sinks 0.8 mm onto them),
   and the syringe cartridge slides 210 mm out the front.

The labware (`tip_rack`, `reservoir`, `well_plate_96`, `waste_tray`) is demo-only and is loaded
from the front over the nest's lip. Anything that goes in or out while tips are on has to pass under
them with the bed down (73 mm): the 61 mm rack clears by 12 mm. The tips are ejected into a
30 mm tray.
