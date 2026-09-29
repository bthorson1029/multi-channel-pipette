# Motorized-lift fabrication files

Cut and print files for the parts that are new or changed in the motorized-lift build (see
`BOM.md` in the repo root for the full list, including the unchanged repo parts). Units are
millimeters.

## Laser-cut (`ToLaserCut-DXF/`, 3 mm steel; 304 stainless or coated steel suggested)

| File | Qty | What changed |
|---|---|---|
| `pipette_plate_motorlift.dxf` | 1 | From `pipette_plate.DXF`: old per-motor nut holes removed; adds the 4 plunger-screw holes + KFL08 bolts, the plunger motor mount, the belt-tensioner slot, and 4 holes for the side-bar brackets. |
| `plunger_plate_motorlift.dxf` | 1 | From `plunger_plate.DXF`: old motor cutouts removed; adds 4 T8 nut patterns (the nuts sit on the holder plate, body up). |
| `lift_plate.dxf` | 1 | New: 160 x 200 lift platform with 2 T8 nut patterns (body through) and 4 corner-block holes. |
| `lift_base_plate.dxf` | 1 | New: 229.2 x 120 plate hung under the bed-level side extrusions; lift screws + KFL08s, lift motor, tensioner slot, home-switch holder and 4 M5 mounting holes. |

Checked: all outlines closed, smallest hole 3.2 mm (above half the thickness), and at least
2.7 mm of material to every plate edge. The thinnest web is **1.2 mm, between each lift nut's
10.4 mm bore and its four M3 holes** (`lift_plate.dxf`); if your cutter flags it, delete those
eight small holes and drill them after cutting, using the nut as a template.

## 3D-printed (`ToPrint-STL/`, PETG suggested; oriented for printing)

| File | Qty | Notes |
|---|---|---|
| `plunger_holder_plate_motorlift.stl` | 1 | Repo holder plate plus 4 screw clearance holes and the nut flange screw holes. |
| `head_bracket.stl` | 2 | Joins the pipette plate to the side bar: 2 M4 up through the plate, 2 M5 up into the bar's bottom slot. Prints on its side; the same part works on both sides (turn it around). |
| `tensioner_bracket_lift.stl` | 1 | 6.5 mm tall. Idler shoulder bolt in the 12 mm slot, 2 M3 to the plate. |
| `tensioner_bracket_plunger.stl` | 1 | 5.5 mm tall; otherwise the same. |
| `lift_home_switch_holder.stl` | 1 | For a KW12-type lever micro switch (20 x 10 x 6.4 mm, mounting holes 9.5 mm apart), clamped by 2 M2 through the walls; 2 M3 to the base plate. Check the hole positions against your switch. |

All five are closed solids (every edge shared by exactly two triangles).

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
