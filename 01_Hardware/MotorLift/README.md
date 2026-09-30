# Motorized-lift fabrication files

Cut and print files for the parts that are new or changed in the motorized-lift build (see
`BOM.md` in the repo root for the full list, including the unchanged repo parts). Units are
millimeters.

## Laser-cut (`ToLaserCut-DXF/`, 3 mm steel; 304 stainless or coated steel suggested)

| File | Qty | What changed |
|---|---|---|
| `pipette_plate_motorlift.dxf` | 1 | Redrawn (160 x 200 mm): a U open at the front for the cartridge drawer (slot 114 mm wide, to 50 mm behind center), with the head-bracket holes, 6 for the sensor posts and 14 for the drawer channels. The repo plate's features all moved: the plunger drive to the top plate, the syringes to the cartridge. |
| `plunger_plate_motorlift.dxf` | 1 | The drive plate, redrawn at 160 x 200 mm so the carriage brackets sit outside the drawer's clamp troughs: 4 T8 nut cutouts (the nuts sit on it, body up), 8 M4 for the carriage brackets, 6 M3 for the sensor flags, 8 M3 for the troughs. No plunger-rod holes: the rods are the cartridge's. |
| `plunger_rail_plate.dxf` | 4 | From `interface_plate_high.DXF`: rectangular and 24 mm longer so it reaches down beside the plunger plate; same carriage holes, M4 pair moved into the carriage bracket. |
| `lift_plate.dxf` | 1 | New: 160 x 200 lift platform with 2 T8 nut cutouts (body through), 8 holes for the carriage brackets and 4 for the well-plate nest. |
| `top_plate.dxf` | 1 | New: across the frame's top ring (12 M5 into it). 4 KFL08s for the plunger screws, the plunger motor (standing on it, shaft down) and the belt-tensioner slot; the pulleys, belt and idler run under it inside the ring. |
| `cart_ledge.dxf` | 2 | New: the drawer channels' ledges under the pipette plate's arms (drawn for the right; flip one over for the left): 7 M3 and a tapped M6 hole for the spring plunger. |
| `cartridge_plate.dxf` | 1 per cartridge | New: the cartridge's drawer plate, 124 x 100 mm: 96 barrel holes, 4 ejector-rod holes, 4 frame screws, 2 handle screws, and 2 detent holes for the spring plungers. |
| `plunger_carrier.dxf` | 1 per cartridge | New: under the thumb pads, 120 x 100 mm with 96 rod holes; it rides on the D-shaft clamps and pushes the ejector rods. |
| `tip_ejector_plate.dxf` | 1 per cartridge | New: tip ejector under the barrel ends, 112 x 98 mm with a 5.8 mm hole around each nozzle, 6 mm holes for its 4 M4 rods (loose, so it can tilt). |
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
| `head_bracket.stl` | 2 | Joins the pipette plate to the side bar: 2 M4 up through the plate, 2 M5 up into the bar's bottom slot. Starts at x 69.5, outside the drawer channel. Prints on its side; the same part works on both sides (turn it around). |
| `tensioner_bracket_lift.stl` | 1 | 6.5 mm tall. Idler shoulder bolt in the 12 mm slot, 2 M3 to the plate. |
| `tensioner_bracket_plunger.stl` | 1 | 5.5 mm tall; on the top plate, the idler's bolt goes down through the slot. |
| `control_box_housing_sloped.stl` | 1 | The repo `ScreenHousing` with its screen panel tilted 10 deg toward the user (front 17.5 mm lower), a 3 mm skirt that runs every wall down to the base, the lid bosses extended down to it, and a back pad with 2 M5 holes into the bottom front bar. The repo's USB opening in the front wall (which faces the user once the box lies down) is filled; a panel-mount USB-B socket goes in the left end instead, beside the DC jack, with a short USB-B extension to the Arduino. The panel moves as one piece with the LCD, encoder and Arduino standoffs under it. Prints panel-down. |
| `plunger_carriage_bracket_RF_LB.stl`, `plunger_carriage_bracket_RB_LF.stl` | 2 + 2 | Join the drive plate to its rail plates, hanging under the plate's side edges outside the D-shaft troughs (x 67.5 on). One M4 x 16 down through the plate into a captive nut in a pocket, one M4 x 20 up from a pocket into a T-nut in the stiffener's long bar, and 2 M4 x 12 in from outside through the rail plate into captive nuts in slots from below. Mirror-image hands: RF and LB are one, RB and LF the other. Print plate-face down. |
| `lift_carriage_bracket.stl` | 4 | Joins the lift platform to a rail plate (one per corner, all alike). Sits on the platform with its outer face on the rail plate: 2 M4 x 12 in from outside through the rail plate's holes into captive nuts (slots open at the top), 2 M4 x 16 down through counterbores and the platform. Prints as oriented; its inner face stays 2 mm outside the well plate's path. |
| `optical_switch_post.stl` | 3 | Plunger home-sensor post on the pipette plate's arms: holds a slotted optical endstop laid flat (long side along y), 16 mm below the drive plate at home so the plate can go on 11.5 mm to eject tips; a pocket under the slot takes the flag. 2 M3 x 12 through counterbores into the plate. |
| `plunger_flag.stl` | 3 | Hangs from the drive plate (2 M3, along y) with a 4 x 2 mm vane that reaches the sensor's beam at home and passes on through the slot. Prints tab down. |
| `well_plate_nest.stl` | 1 | Locates the well plate on the lift platform (replaces the flat repo tray): a 15 mm base (the height the firmware expects), walls 4 mm above it on the back and sides, a 2 mm lip at the front, 0.4 mm clearance around the SBS footprint. 4 M4 x 16 through counterbores into the platform. |
| `control_box_base.stl` | 1 | Closes the control box (replaces the repo lid). 4 countersunk M3 self-tappers into the housing bosses. |
| `syringe_lock_frame.stl` | 1 per cartridge | Holds the 96 syringes by their flanges, with the finger tabs trimmed to stubs instead of the flanged end cut off: each flange sits on the cartridge plate in a slot along its row (7.4 mm wide, 1.1 mm deep, so the frame presses 0.1 mm on every flange and the stubs can't turn), and 5.2 mm holes pass the plunger rods. 4 M3 x 14 self-tappers go down through it and the cartridge plate into the grip's ears. Prints slot side up. |
| `syringe_grip_slipfit.stl` | 1 per cartridge | The repo grip with its 96 holes opened from 6.5 to 6.9 mm, so the barrels slide in; it keeps their lower ends in line. 4 ears take the frame screws, so it hangs from the cartridge plate instead of sliding down the barrels. |
| `pad_retainer.stl` | 1 per cartridge | Over the thumb pads, on the plunger carrier (3 mm): pockets keep the 96 pads captive when the cartridge is out, and it carries the drive plate's push down to them. Prints pockets up. |
| `cartridge_handle.stl` | 1 per cartridge | Under the front of the cartridge plate (2 M3 self-tappers): pull the drawer out by it. |
| `cart_spacer_R.stl` | 2 | Drawer channel spacer under the pipette plate's arm, between it and the ledge; its tab at the back is the drawer's stop. Drawn for the right; mirror it for the left. |
| `dshaft_trough_R.stl` | 2 | Under the drive plate, cradling an 8 mm D-shaft along its length (so the shaft can't bend); 4 M3 up into the plate (2 into T-nuts in the stiffener's long bar). Mirror for the left. |
| `dshaft_lever.stl` | 2 | On the front end of each D-shaft, pinned across it (2 x 16 mm spring pin). Hanging down, the flat faces outward and the carrier is clamped; a quarter turn outward brings the flat up and the carrier sinks 0.8 mm onto it. The hub is trimmed flush with the flat and the arm is 5.6 mm thick, so with the lever open the carrier slides out over it. |
| `lift_home_switch_holder.stl` | 1 | For a KW12-type lever micro switch (20 x 10 x 6.4 mm, mounting holes 9.5 mm apart), clamped by 2 M2 through the walls; 2 M3 to the base plate. Check the hole positions against your switch. |

All nineteen are closed solids (every edge shared by exactly two triangles).

## Check against your hardware before cutting

- **KFL08 bolt spacing** is set to 37 mm (`KFL08_BOLTS` in `make_dxf.py`). Measure your bearings.
- **Frame height** (400 mm) and rail lengths were estimated from the build video.
- **Syringes**: the frame and grip assume a 6.4 mm barrel, a 1.2 mm flange, and tabs trimmed so
  the flange is 8.2 x 7.2 mm (typical 1 mL values, `SYR_*` in `04_Blender/variant_motor_lift.py`).
  Measure one of yours; if the flange is thicker, the slot depth follows `SYR_FLANGE_T`.

## Tip ejector

A 3 mm plate under the barrel ends, with a hole around each nozzle that the tip rims can't pass.
Four springs on its M4 rods, between the cartridge plate and a nut, hold it up against the barrel
ends, where it is also the stop the tips seat against when they are loaded. To eject, the plunger
goes on past home: the plunger carrier meets the front rods 1.0 mm below home and the back
rods 5.5 mm below, so the plate tilts (about
5 deg) and strips the tips a few rows at a time, front to back, instead of breaking all 96 loose at
once; at 11.5 mm every tip has been pushed 6 mm off its nozzle. Because the plate goes past home,
the plunger's home sensors are slotted optical endstops with flags, not lever switches. The whole
ejector is part of the syringe cartridge.

Before relying on it, pull one tip off a heat-shrunk nozzle with a luggage scale: the plunger drive
has roughly 300-500 N, and the staggering keeps the peak to about two rows of tips.

## Syringe cartridge (drawer)

Everything that depends on the syringes and tips is one unit that slides in and out at the front,
like a drawer, so a machine can carry cartridges for different tip families (and a spare to swap in
while one is cleaned or repaired). Each cartridge has its own 96 syringes.

- **Stays on the machine:** frame, lift, pipette plate (a U, open at the front), the plunger drive
  (now on the top plate: motor, belt, screws; the drive plate with its nuts, stiffening frame and
  carriage brackets), home sensors and flags, and the drawer's channels and clamps.
- **In the cartridge:** the cartridge plate with the barrels, locking frame, grip and handle; the
  plunger carrier (`plunger_carrier.dxf` + `pad_retainer.stl`) holding the thumb pads captive; the
  tip ejector (plate, rods, springs); the nozzles' heat-shrink for its tip family. Out of the
  machine it holds together by itself: the syringe stoppers' friction keeps the plunger carrier
  where it was.
- **Lower level, the cartridge plate:** its edges run in two channels under the pipette plate's
  arms (a steel ledge on a printed spacer, 3.3 mm gap). It slides in until it stops against the
  spacers' tabs at the back, and a spring plunger in each ledge clicks into its detent holes.
- **Upper level, the plunger carrier:** its edges run over two 8 mm D-shafts, each cradled full
  length in a printed trough under the drive plate. With the flats up it slides in freely; a
  quarter turn of each shaft's front lever puts the round side up and presses the carrier against
  the drive plate, so the coupling has no play in either direction (any play would be lost volume).
- **Firmware:** pick the cartridge on the device ("Cartridge"); its entry in `CARTRIDGES`
  (`Config.h`) sets the tip capacity, calibration and tip height.

To swap: empty the tips (eject them, or leave them on: with the bed down they clear the nest) and
take the labware off; Home all (bed down, plunger at its working zero). Turn the two levers to
open, pull the drawer out by its handle. Slide the other one in until it clicks, turn the levers
to clamp, select it on the device, Home all. The whole path is clear (checked in the model: the
cartridge slides 300 mm straight out the front without touching anything). A new cartridge's
plunger carrier has to sit at the same height as the one that came out; set it once with the
drive plate at its working zero, the syringes' friction keeps it.

## Regenerating

The layout numbers (screw, motor, switch and bracket positions) live in `make_dxf.py`, and the
Blender model reads them from there, so the files and the model stay in sync:

```
python 01_Hardware/MotorLift/make_dxf.py                           # DXFs
blender -b --python 04_Blender/export_motor_lift_parts.py           # STLs (builds the model first)
```
