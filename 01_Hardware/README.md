# Fabrication files

Every part to cut or print for the pipette: 12 DXF files for 34 laser-cut parts and 21 STL files
for 32 printed parts plus 96 resin tip cones. Everything else is bought; see [`BOM.md`](../BOM.md) for the full list with
quantities to order. Units are millimeters.

## Laser-cut (`ToLaserCut-DXF/`, 3 mm steel; 304 stainless or coated steel suggested)

Upload the files separately and set each quantity. The generated files don't declare units: choose
millimeters if asked, and check a size (the top plate is 229.2 x 218 mm). Use 3 mm (or 11 gauge)
stock, not 1/8" (3.18 mm): the cartridge plate slides in a 3.3 mm channel.

| File | Qty | Notes |
|---|---|---|
| `pipette_plate.dxf` | 1 | 160 x 200 mm: a U open at the front for the cartridge drawer (slot 114 mm wide, to 50 mm behind center), with the head-bracket holes, 6 for the sensor posts and 14 for the drawer channels. |
| `plunger_plate.dxf` | 1 | The drive plate, redrawn at 160 x 200 mm so the carriage brackets sit outside the drawer's clamp troughs: 4 T8 nut cutouts (the nuts sit on it, body up), 8 M4 for the carriage brackets, 6 M3 for the sensor flags, 8 M3 for the troughs. No plunger-rod holes: the rods are the cartridge's. |
| `plunger_rail_plate.dxf` | 4 | Joins the drive plate's carriage brackets to the carriages: the lift rail plate made rectangular and 24 mm longer so it reaches down beside the drive plate; same carriage holes, M4 pair moved into the carriage bracket. |
| `lift_rail_plate.dxf` | 4 | Joins the lift platform's carriage brackets to the carriages: 3 carriage screws, 2 M4 into the bracket. The original design's `interface_plate_high`, redrawn 2 mm wider at the carriage end and at its notch, which left only 0.8 mm of steel beside three holes. |
| `corner_bracket.dxf` | 16 | Frame corners, 4 M5 each into the extrusion (the original design's). Or buy 2020 flat L corner plates. |
| `lift_plate.dxf` | 1 | 156 x 200 lift platform (its edges clear the rail plates' carriage-screw heads) with 2 T8 nut cutouts (body through), 8 holes for the carriage brackets and 4 for the well-plate nest. |
| `top_plate.dxf` | 1 | Across the frame's top ring (12 M5 into it). 4 KFL08s for the plunger screws, the plunger motor (standing on it, shaft down) and the belt-tensioner slot; the pulleys, belt and idler run under it inside the ring. |
| `cart_ledge.dxf` | 2 | The drawer channels' ledges under the pipette plate's arms (drawn for the right; flip one over for the left): 7 M3 and a tapped M6 hole for the spring plunger. |
| `cartridge_plate.dxf` | 1 per cartridge | The cartridge's drawer plate, 124 x 100 mm: 96 barrel holes, 4 ejector-rod holes, 4 frame screws, 2 handle screws, and 2 detent holes for the spring plungers. |
| `plunger_carrier.dxf` | 1 per cartridge | Under the thumb pads, 120 x 100 mm with 96 rod holes and 4 holes to tap M3 for the pad retainer; it rides on the D-shaft clamps and pushes the ejector rods. |
| `tip_ejector_plate.dxf` | 1 per cartridge | Tip ejector under the barrel ends, 112 x 102 mm with a 5.8 mm hole around each nozzle, 6 mm holes for its 4 M4 rods (loose, so it can tilt). |
| `lift_base_plate.dxf` | 1 | 229.2 x 120 plate hung under the bed-level side extrusions; lift screws + KFL08s, lift motor, tensioner slot, home-switch holder and 4 M5 mounting holes. |

Each T8 nut mounts through one cloverleaf cutout (the center bore with four 3.4 mm slots out to
the flange screws) instead of a bore and four separate holes, which would leave only 1.2 mm
(lift) and 1.9 mm (plunger) of steel between them. The flange covers the slots and carries the
load; the M3 nuts (5.5 mm across flats) span the 3.4 mm slots on their own.

Checked: all outlines closed; smallest hole 2.5 mm (the plunger carrier's tap holes), most of the
plate thickness. Every hole has at least 1.5 mm of steel to the plate's outer edge (the cartridge
plate's detent holes; everything else 2.2 mm or more), above SendCutSend's 0.91 mm minimum for
instant quoting. The thinnest web is 4.1 mm (drive plate), apart from the cartridge plate's 96
barrel holes, which keep the original design's 2.5 mm webs.

After cutting, tap the 4 small (2.5 mm) holes in `plunger_carrier.dxf` for M3 and the detent hole
in each `cart_ledge.dxf` for M6. For a spare cartridge, order another cartridge plate, plunger
carrier and tip ejector plate.

## 3D-printed (`ToPrint-STL/`, PETG suggested, the tip cones in resin; oriented for printing)

| File | Qty | Notes |
|---|---|---|
| `head_bracket.stl` | 2 | Joins the pipette plate to the side bar: 2 M4 up through the plate, 2 M5 up into the bar's bottom slot. Starts at x 69.5, outside the drawer channel. Prints on its side; the same part works on both sides (turn it around). |
| `tensioner_bracket_lift.stl` | 1 | 6.5 mm tall. Idler shoulder bolt in the 12 mm slot, 2 M3 x 12 to the plate, 25 mm apart so their heads clear the idler. |
| `tensioner_bracket_plunger.stl` | 1 | 5.5 mm tall; on the top plate, the idler's bolt goes down through the slot. |
| `control_box_housing_sloped.stl` | 1 | The original design's `ScreenHousing` (in `04_Blender/source/`) with its screen panel tilted 10 deg toward the user (front 17.5 mm lower), a 3 mm skirt that runs every wall down to the base, the lid bosses extended down to it, and a back pad with 2 M5 holes into the bottom front bar. Its USB opening in the front wall (which faces the user once the box lies down) is filled; a panel-mount USB-B socket goes in the left end instead, beside the DC jack, with a short USB-B extension to the Arduino. The panel moves as one piece with the LCD, encoder and Arduino standoffs under it. Prints panel-down. |
| `plunger_carriage_bracket_RF_LB.stl`, `plunger_carriage_bracket_RB_LF.stl` | 2 + 2 | Join the drive plate to its rail plates, hanging under the plate's side edges outside the D-shaft troughs (x 67.5 on). One M4 x 20 down through the plate into a captive nut in a pocket, one M4 x 20 up from a pocket (pocket floors 11.5 mm under the plate, so it goes 5.5 mm into the T-nut) into a T-nut in the stiffener's long bar, and 2 M4 x 12 in from outside through the rail plate into captive nuts in slots from below. Mirror-image hands: RF and LB are one, RB and LF the other. Print plate-face down. |
| `lift_carriage_bracket.stl` | 4 | Joins the lift platform to a rail plate (one per corner, all alike). Sits on the platform with its outer face on the rail plate: 2 M4 x 12 in from outside through the rail plate's holes into captive nuts (slots open at the top), 2 M4 x 16 down through counterbores and the platform. Prints as oriented; its inner face stays 2 mm outside the well plate's path. |
| `optical_switch_post.stl` | 3 | Plunger home-sensor post on the pipette plate's arms: holds a slotted optical endstop laid flat (long side along y), 18.4 mm below the drive plate at home so the plate and flag tab clear it (and its screw heads) with 1.5 mm to spare at the full 11.5 mm eject; a pocket under the slot takes the flag. 2 M3 x 12 through counterbores into the plate. |
| `plunger_flag.stl` | 3 | Hangs from the drive plate (2 M3 x 10 countersunk up from under the tab, flush, nuts on the plate) with a 4 x 2 mm vane that reaches the sensor's beam at home and passes on through the slot. Prints tab down. |
| `well_plate_nest.stl` | 1 | Locates the well plate on the lift platform (replaces the original's flat tray): a 15 mm base (the height the firmware expects), walls 4 mm above it on the back and sides, a 2 mm lip at the front, 0.4 mm clearance around the SBS footprint. 4 M4 x 16 through counterbores into the platform. Cut back 11.5 mm around each lift nut for its flange screws' heads. |
| `control_box_base.stl` | 1 | Closes the control box (replaces the original's lid, which sat between the posts). 4 countersunk M3 self-tappers into the housing bosses. |
| `syringe_lock_frame.stl` | 1 per cartridge | Holds the 96 syringes by their flanges, with the finger tabs trimmed to stubs instead of the flanged end cut off: each flange sits on the cartridge plate in a slot along its row (7.4 mm wide, 1.1 mm deep, so the frame presses 0.1 mm on every flange and the stubs can't turn), and 5.2 mm holes pass the plunger rods. 4 M3 x 14 self-tappers go down through it and the cartridge plate into the grip's ears. Prints slot side up. |
| `syringe_grip_slipfit.stl` | 1 per cartridge | The original design's grip (in `04_Blender/source/`) with its 96 holes opened from 6.5 to 6.9 mm, so the barrels slide in; it keeps their lower ends in line. 4 ears take the frame screws, so it hangs from the cartridge plate instead of sliding down the barrels. |
| `pad_retainer.stl` | 1 per cartridge | Over the thumb pads, on the plunger carrier (3 mm): pockets keep the 96 pads captive when the cartridge is out, and it carries the drive plate's push down to them. 4 M3 x 6 countersunk screws hold it to the carrier: the heads sit flush with its top (which bears on the drive plate) and the tips come out flush under the carrier (which rides on the D-shafts). Prints pockets up. |
| `cartridge_handle.stl` | 1 per cartridge | Under the front of the cartridge plate (2 M3 self-tappers): pull the drawer out by it. |
| `cart_spacer_R.stl` | 2 | Drawer channel spacer under the pipette plate's arm, between it and the ledge; its tab at the back is the drawer's stop. Drawn for the right; mirror it for the left. |
| `dshaft_trough_R.stl` | 2 | Under the drive plate, cradling an 8 mm D-shaft along its length (so the shaft can't bend); 4 M3 x 25 up into the plate (2 into T-nuts in the stiffener's long bar); pockets under the plate take the nuts of the front plunger T8 flange screws. Mirror for the left. |
| `dshaft_lever.stl` | 2 | On the front end of each D-shaft, held by an M3 cone-point set screw in a dimple opposite the flat. Pointing inward and down, the flat faces outward and the carrier is clamped; a quarter turn outward (the arm ends up hanging 30 deg out from straight down, about 16 mm clear of the rail plate) brings the flat up and the carrier sinks 0.8 mm onto it. With the lever open, the carrier and the plunger rods slide out past it, so the hub only wraps the shaft about 190 deg: it's trimmed flush with the flat (0.2 mm under the carrier) and 1.5 mm outside the outer rods, and the arm is 5.6 mm thick. |
| `lift_home_switch_holder.stl` | 1 | For a KW12-type lever micro switch (20 x 10 x 6.4 mm, mounting holes 9.5 mm apart), clamped by 2 M2 through the walls; 2 M3 to the base plate. Check the hole positions against your switch. |

| `tip_cone.stl` | 96 per cartridge, plus spares | Resin (SLA), not FDM. Pushed onto each syringe's Luer-slip nozzle; the tips seal on it. See "Tip cones" below. Prints Luer mouth up. |
| `tip_cone_sizing_set.stl` | 1 | Resin (SLA). Five tip cones in 0.1 mm steps on a bar, smallest at the notched end: order it first to choose the size. |

All 21 are closed solids (every edge shared by exactly two triangles).

## Check against your hardware before cutting

- **KFL08 bolt spacing** is set to 37 mm (`KFL08_BOLTS` in `make_dxf.py`). Measure your bearings.
- **Frame height** and rail lengths: 430 mm posts and 360 mm rails, 30 mm taller than the original design's (whose 400 mm was estimated from its build video), so an empty tip rack slides out under freshly loaded tips. The lift travels 66 mm.
- **Syringes**: the frame and grip assume a 6.4 mm barrel, a 1.2 mm flange, and tabs trimmed so
  the flange is 8.2 x 7.2 mm (typical 1 mL values, `SYR_*` in `04_Blender/build_pipette.py`).
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

Before relying on it, pull one tip off a tip cone with a luggage scale: the plunger drive
has roughly 300-500 N, and the staggering keeps the peak to about two rows of tips.

## Tip cones

A resin sleeve on each syringe's Luer-slip nozzle that the tips seal on (`tip_cone.stl`). Inside
it is the standard female Luer taper (6 %), open right through, so it pushes onto the nozzle like
any Luer-slip fitting; the nozzle's end sits 4.5 mm in. Outside, the seal cone narrows from 5.14
to 4.90 mm over its first 4.6 mm, then a lead-in chamfers it to 4.6 mm. It sits 0.5 mm under the
ejector plate, whose 5.8 mm holes it passes. Because every cone is the same part, every channel
gets the same seal and the same pull-off force.

It is only 5.3 mm long so the ejector pushes every tip fully clear of it: at full eject the
back row (the least-pushed, since the plate tilts) ends 1.0 mm below the cone's end and the front
row 4.2 mm (`eject_clearance()` in the model). A longer cone would leave the tips loose but still
on it, relying on gravity to drop them. The seal therefore sits over the nozzle, in the tip's top
5 mm.

- **Print in resin (SLA), not FDM,** from a service: JLC3DP and Craftcloud both offer it. Choose a
  tough or engineering resin over standard if offered: the wall over the nozzle is only about
  0.45 mm, since the tip's mouth (about 5.3 mm) limits the outside and the nozzle (about 4.2 mm)
  the inside. Order a few spares.
- **Size them first.** The seal-cone diameters are estimates, and tip brands differ.
  `tip_cone_sizing_set.stl` has five cones on a bar, from 0.2 mm under to 0.2 mm over the model's
  size (`CONE_SIZES`), smallest at the notched end. Order it with a box of the tips you'll use,
  cut the cones off the bar, push each onto a syringe and press a tip on by hand. Pick the
  smallest that seals (draw some water and hold it for a minute: no drop forms) and still pulls
  off with a firm tug. Add its offset to `CONE_SEAL` in `04_Blender/build_pipette.py`, rerun
  `export_parts.py`, and order 96 plus spares.
- **Fitting:** push each onto its nozzle with a quarter twist, as you would a Luer-slip fitting.
  A seated Luer taper usually holds harder than a tip does, so the cones should stay put when the
  tips are ejected. If one comes off with its tip, glue it with cyanoacrylate and a polyolefin
  primer (syringe nozzles are polypropylene).

## Syringe cartridge (drawer)

Everything that depends on the syringes and tips is one unit that slides in and out at the front,
like a drawer, so a machine can carry cartridges for different tip families (and a spare to swap in
while one is cleaned or repaired). Each cartridge has its own 96 syringes.

- **Stays on the machine:** frame, lift, pipette plate (a U, open at the front), the plunger drive
  (now on the top plate: motor, belt, screws; the drive plate with its nuts, stiffening frame and
  carriage brackets), home sensors and flags, and the drawer's channels and clamps.
- **In the cartridge:** the cartridge plate with the barrels, locking frame, grip and handle; the
  plunger carrier (`plunger_carrier.dxf` + `pad_retainer.stl`) holding the thumb pads captive; the
  tip ejector (plate, rods, springs); the 96 tip cones, sized for its tip family. Out of the
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
python 01_Hardware/make_dxf.py                           # DXFs
blender -b --python 04_Blender/export_parts.py           # STLs (builds the model first)
```

`corner_bracket.dxf` is the original design's drawing, cut as it is; `make_dxf.py` writes every
other DXF, including `lift_rail_plate.dxf` (redrawn from the original's).
