# Blender model

Python scripts that build the pipette in Blender (tested with 5.2), check it, and write its
printed parts. The scripts are the source of truth; the `.blend` files they produce are not
committed.

```bash
blender --python 04_Blender/build_pipette.py
```

```bash
blender -b --python 04_Blender/export_parts.py
```

The first builds the model and opens it; the second builds it without the UI and writes the
printed parts to `01_Hardware/ToPrint-STL`. You can also open `build_pipette.py` in Blender's Text
Editor and use **Run Script**. Units are millimeters (Z up, front = -Y).

## Files

| File | What it is |
|---|---|
| `build_pipette.py` | The build: lift, plunger drive, syringe cartridge, control box, fasteners, demo labware, the animated run, and the checks. Layout numbers come from `01_Hardware/make_dxf.py`. |
| `pipette_lib.py` | Helpers (materials, mesh, DXF and STL import, T-slot extrusion) and the base parts: frame, corner brackets, well plate, pipette and drive plates, plunger rail plates, the grip and the control box as the original design had them. Not run on its own. |
| `export_parts.py` | Builds the model and writes each printed part as an STL, oriented for printing. It refuses to write a part with holes in its surface. |
| `source/` | Three STLs from the original design that printed parts are derived from: `ScreenHousing.STL` (the sloped control-box housing), `syringe_grip_static.STL` (the slip-fit grip) and `electronics_lid.STL` (used only to position the box). Not printed as they are. |
| `renders/` | Images used in the READMEs. |

## Where the geometry comes from

- **Imported:** the laser-cut parts from `01_Hardware/ToLaserCut-DXF` (lines, arcs and holes,
  extruded to 3 mm steel), and the three `source/` STLs.
- **Modeled:** 2020 T-slot extrusion (B-type 6 mm slot profile), every screw, bolt, nut and
  T-nut in the BOM (`fasteners()`, one `fast_*` object per joint), MGN9H rails and carriages,
  NEMA17 motors, T8 screws and nuts, syringes, tips, labware, bearings, pulleys and belts. The
  printed parts are modeled as closed solids so `export_parts.py` can write them straight to STL.
- **Layout:** the frame layout was reconstructed from the original design's build video
  (youtu.be/2TTu-Lkz2Eo), then raised 30 mm (430 mm posts). Part shapes are exact; syringe and
  tip dimensions and some mounting positions are estimates.

## Checks

- `collision_report()` sweeps every moving part through its full travel (lift, plunger, tip
  eject) and tests it against the rest of the model, allowing only intended contacts (screws in
  nuts, carriages on rails, and so on). It reports no collisions.
- `fasteners()` checks every fastener as it places it: T-nut bolts must end 4.2-6.0 mm into the
  slot, nut bolts must pass through their nut, and screws into a part must get enough thread;
  any that don't are printed.
- The build reports the belt loop lengths across each tensioner's adjustment range: 338.9-344.4
  mm (lift) and 538.7-544.6 mm (plunger).

## The animated run

The timeline plays a complete run (`CYCLE`, 680 frames); scrub it to watch:

1. It starts with no tips. A tip rack goes into the nest, the bed rises 62 mm to press the nozzles
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
from the front over the nest's lip. Anything that goes in or out while tips are on has to pass
under them with the bed down (71 mm): the 61 mm rack clears by 10 mm. The tips are ejected into a
30 mm tray.
