# Motorized-lift fabrication files

Cut and print files for the parts that are new or changed in the motorized-lift build (see
`BOM.md` in the repo root for the full list, including the unchanged repo parts). Units are
millimeters.

## Laser-cut (`ToLaserCut-DXF/`, 3 mm steel; 304 stainless or coated steel suggested)

| File | Qty | What changed |
|---|---|---|
| `pipette_plate_motorlift.dxf` | 1 | From `pipette_plate.DXF`: old per-motor nut holes removed; adds the 4 plunger-screw holes + KFL08 bolts, the plunger motor mount, the belt-tensioner slot, and 4 holes for the side-bar brackets. |
| `plunger_plate_motorlift.dxf` | 1 | From `plunger_plate.DXF`: old motor cutouts removed; adds 4 T8 nut cutouts (the nuts sit on the holder plate, body up) and 8 M4 holes for the carriage brackets underneath. |
| `plunger_rail_plate.dxf` | 4 | From `interface_plate_high.DXF`: rectangular and 24 mm longer so it reaches down beside the plunger plate; same carriage holes, M4 pair moved into the carriage bracket. |
| `lift_plate.dxf` | 1 | New: 160 x 200 lift platform with 2 T8 nut cutouts (body through) and 8 holes for the carriage brackets. |
| `lift_base_plate.dxf` | 1 | New: 229.2 x 120 plate hung under the bed-level side extrusions; lift screws + KFL08s, lift motor, tensioner slot, home-switch holder and 4 M5 mounting holes. |

Each T8 nut mounts through one cloverleaf cutout (the center bore with four 3.4 mm slots out to
the flange screws) instead of a bore and four separate holes, which left only 1.2 mm (lift) and
1.9 mm (plunger) of steel between them. The flange covers the slots and carries the load; put a
washer under each M3 nut so it spans its slot.

Checked: all outlines closed, smallest hole or slot 3.4 mm (above the thickness), and at least
2.7 mm of material to every plate edge. The thinnest web in the new features is 4.1 mm (plunger
plate). The pipette plate's 96 syringe holes keep the repo plate's 2.5 mm webs.

## 3D-printed (`ToPrint-STL/`, PETG suggested; oriented for printing)

| File | Qty | Notes |
|---|---|---|
| `plunger_holder_plate_motorlift.stl` | 1 | Repo holder plate plus 4 screw clearance holes, the nut flange screw holes, and 8 clearance holes over the carriage-bracket bolt heads. |
| `head_bracket.stl` | 2 | Joins the pipette plate to the side bar: 2 M4 up through the plate, 2 M5 up into the bar's bottom slot. Prints on its side; the same part works on both sides (turn it around). |
| `tensioner_bracket_lift.stl` | 1 | 6.5 mm tall. Idler shoulder bolt in the 12 mm slot, 2 M3 to the plate. |
| `tensioner_bracket_plunger.stl` | 1 | 5.5 mm tall; otherwise the same. |
| `control_box_housing_sloped.stl` | 1 | The repo `ScreenHousing` with its screen panel tilted 10 deg toward the user (front 17.5 mm lower). The panel moves as one piece with the LCD, encoder and Arduino standoffs under it, and the USB opening in the front wall is moved to where the port now sits. Prints panel-down. |
| `plunger_carriage_bracket_RF_LB.stl`, `plunger_carriage_bracket_RB_LF.stl` | 2 + 2 | Join the plunger plate to its rail plates, hanging under the plate's side edges between the syringe array and the nut screws. 2 M4 x 16 down through the plate into captive nuts in pockets from below (heads sit in the holder plate's clearance holes, so fit these before the holder plate), and 2 M4 x 12 in from outside through the rail plate into captive nuts in slots from below. Mirror-image hands: RF and LB are one, RB and LF the other. Print plate-face down. |
| `lift_carriage_bracket.stl` | 4 | Joins the lift platform to a rail plate (one per corner, all alike). Sits on the platform with its outer face on the rail plate: 2 M4 x 12 in from outside through the rail plate's holes into captive nuts (slots open at the top), 2 M4 x 16 down through counterbores and the platform. Prints as oriented; its inner face stays 2 mm outside the well plate's path. |
| `lift_home_switch_holder.stl` | 1 | For a KW12-type lever micro switch (20 x 10 x 6.4 mm, mounting holes 9.5 mm apart), clamped by 2 M2 through the walls; 2 M3 to the base plate. Check the hole positions against your switch. |

All nine are closed solids (every edge shared by exactly two triangles).

## Check against your hardware before cutting

- **KFL08 bolt spacing** is set to 37 mm (`KFL08_BOLTS` in `make_dxf.py`). Measure your bearings.
- **Frame height** (400 mm) and rail lengths were estimated from the build video.
- The plunger holder plate stands 1.5 mm off the plunger plate (the plunger thumb pads are
  between them), so put 1.5 mm of washers on each nut screw there.

## Regenerating

The layout numbers (screw, motor, switch and bracket positions) live in `make_dxf.py`, and the
Blender model reads them from there, so the files and the model stay in sync:

```
python 01_Hardware/MotorLift/make_dxf.py                           # DXFs
blender -b --python 04_Blender/export_motor_lift_parts.py           # STLs (builds the model first)
```
