# Bill of materials

For the pipette: fixed head, lead-screw bed lift, one belt-synced plunger motor (model:
`04_Blender/build_pipette.py`, firmware: `02_Software/arduino/MotorLift`). Quantities are counted
from the Blender model. The frame layout was reconstructed from the original design's build video,
so treat lengths marked *est.* as starting points and confirm against your own frame.

Every file to cut or print is in `01_Hardware` (paths below are relative to it); its
[README](01_Hardware/README.md) describes each part and how to regenerate the files.

## Order summary

Totals for one machine with one syringe cartridge, checked against the Blender model.
Fastener quantities include about 20 % extra; the sections below say where each part
goes.

**To have made**
- Laser-cut, 3 mm steel: 34 parts from 12 DXF files (sections 1 and 5b). The 16 frame corner
  brackets can be bought instead.
- 3D-printed: 32 parts from 19 STL files (sections 2 and 5b). Mirror `cart_spacer_R` and
  `dshaft_trough_R` for the left side.

**Frame and motion**
- 2020 extrusion, 12 bars to cut: 4 x 430 mm *est.*, 4 x 189.2 mm, 8 x 178 mm, 2 x 150 mm,
  2 x 44 mm (about 4.3 m in total)
- 2020 inside corner brackets: 12
- MGN9 rail, 360 mm *est.*: 4; MGN9H carriages: 8
- NEMA17 steppers: 1 x 40 mm body (lift), 1 x 48 mm body (plunger)
- T8x2 lead screw: 6 pieces (4 x ~131 mm, 2 x ~148 mm); anti-backlash nuts: 4; flange nuts: 2
- KFL08 flange bearings: 6
- GT2 20T pulleys: 6 x 8 mm bore, 2 x 5 mm bore; 16 mm smooth idlers: 2
- GT2 6 mm closed loops: 1 x 339-344 mm, 1 x 539-544 mm
- 8 mm steel rod: 2 x ~165 mm (D-shafts)
- M6 ball spring plungers: 2
- KW12-type micro switch: 1; slotted optical endstop boards: 3

**Electronics:** Arduino Uno, CNC Shield V3, 2 stepper drivers, 20x4 I2C LCD, rotary encoder,
panel-mount USB-B extension, 12 V 5 A supply with a DC socket (optional LM2596), wire and
Dupont leads.

**Cartridge supplies:** 96 1 mL Luer-slip syringes plus spares, heat-shrink tubing, 4 x ~110 mm
M4 threaded rod, 4 light springs (~6.4 mm OD x 20-25 mm).

**Fasteners** (with ~20 % extra)

| Size | Buy |
|---|---|
| M5 x 8 button head | 96 |
| M5 x 10 | 29 |
| M5 x 12 | 5 |
| M5 x 14 | 3 |
| M5 washer | 5 |
| M5 T-nut (2020) | 132 |
| M4 x 12 | 34 |
| M4 x 16 | 15 |
| M4 x 20 | 10 |
| M4 x 30 | 5 |
| M4 hex nut | 72 |
| M4 washer | 15 |
| M4 T-nut (2020) | 5 |
| M3 x 6 | 29 |
| M3 x 8 | 96 |
| M3 x 10 | 29 |
| M3 x 12 | 15 |
| M3 x 14 | 17 |
| M3 x 20 | 3 |
| M3 x 25 | 10 |
| M3 x 10 countersunk | 8 |
| M3 x 6 countersunk | 5 |
| M3 hex nut | 75 |
| M3 T-nut (2020) | 92 |
| M3 x 6 cone-point set screw | 3 |
| M3 self-tapping: pan x 8 / pan x 10 / pan x 14 / countersunk x 10 | 8 / 3 / 5 / 5 |
| M2 x 20 + nut | 3 |
| Shoulder bolt + nut (idlers) | 2 |

## 1. Laser-cut metal

The model assumes **3 mm steel** (not 1/8", 3.18 mm: the cartridge plate runs in a 3.3 mm channel). The machine
works around liquids, so consider 304 stainless or a coated steel over bare mild steel. Aluminum
would be lighter but about 3x more flexible, which costs plunger accuracy.

| Part | Qty | File | Notes |
|---|---|---|---|
| Pipette plate | 1 | `ToLaserCut-DXF/pipette_plate.dxf` | A U open at the front for the cartridge drawer; head-bracket, sensor-post and channel holes. |
| Plunger (drive) plate | 1 | `ToLaserCut-DXF/plunger_plate.dxf` | 160 x 200 mm: 4 T8 nut cutouts, 8 carriage-bracket holes, 3 sensor flags, 8 trough bolts; no plunger-rod holes. |
| Top plate | 1 | `ToLaserCut-DXF/top_plate.dxf` | On the top ring: the plunger screws' KFL08s, the plunger motor, the belt tensioner. |
| Drawer channel ledge | 2 | `ToLaserCut-DXF/cart_ledge.dxf` | Flip one over for the left side. Tap the M6 hole. |
| Lift platform | 1 | `ToLaserCut-DXF/lift_plate.dxf` | 156 x 200 mm (its edges clear the rail plates' carriage-screw heads), 2 T8 nut cutouts, 8 carriage-bracket holes, 4 well-plate-nest holes. |
| Lift base plate | 1 | `ToLaserCut-DXF/lift_base_plate.dxf` | 229.2 x 120 mm. |
| Lift rail plate | 4 | `ToLaserCut-DXF/lift_rail_plate.dxf` | Joins the lift platform's brackets to the carriages. |
| Plunger rail plate | 4 | `ToLaserCut-DXF/plunger_rail_plate.dxf` | A taller, rectangular lift rail plate that reaches down to the plunger carriage brackets. |
| Frame corner bracket | 16 | `ToLaserCut-DXF/corner_bracket.dxf` | Or buy 2020 flat L corner plates. |

The syringe cartridge's three plates are in section 5b.

## 2. 3D-printed parts

PETG is a good default for the load-bearing parts. Suggested:
4 perimeters, 40 % infill. The largest part (the sloped housing, 218 x 111 x 75 mm) needs a bed of at
least 220 mm.

| Part | Qty | File | Notes |
|---|---|---|---|
| Plunger sensor post | 3 | `ToPrint-STL/optical_switch_post.stl` | Holds a slotted optical endstop laid flat under the plunger plate; 2 M3 to the pipette plate. |
| Plunger sensor flag | 3 | `ToPrint-STL/plunger_flag.stl` | Hangs from the plunger plate through the sensor's slot; 2 M3. |
| Electronics housing (sloped) | 1 | `ToPrint-STL/control_box_housing_sloped.stl` | The original design's housing with the screen panel tilted 10 deg toward the user, a skirt that runs its walls down to the bench, the lid bosses extended to the base, and a back pad with 2 M5 into T-nuts in the bottom front bar. |
| Control box base | 1 | `ToPrint-STL/control_box_base.stl` | Closes the housing's underside (replaces the original's lid, which was sized to sit between the posts). 4 countersunk M3 into the bosses. |
| Well-plate nest | 1 | `ToPrint-STL/well_plate_nest.stl` | Locates an SBS plate on the lift platform at the height the firmware expects (replaces the original's flat tray). 4 M4 to the platform. |
| Head bracket | 2 | `ToPrint-STL/head_bracket.stl` | Bolts the pipette plate to the side bars. |
| Belt tensioner bracket (lift) | 1 | `ToPrint-STL/tensioner_bracket_lift.stl` | |
| Belt tensioner bracket (plunger) | 1 | `ToPrint-STL/tensioner_bracket_plunger.stl` | On the top plate. |
| Drawer channel spacer | 1 + 1 mirrored | `ToPrint-STL/cart_spacer_R.stl` | Mirror for the left. |
| D-shaft trough | 1 + 1 mirrored | `ToPrint-STL/dshaft_trough_R.stl` | Mirror for the left. |
| D-shaft lever | 2 | `ToPrint-STL/dshaft_lever.stl` | |
| Plunger carriage bracket | 2 + 2 | `ToPrint-STL/plunger_carriage_bracket_RF_LB.stl`, `ToPrint-STL/plunger_carriage_bracket_RB_LF.stl` | Hang under the plunger plate's side edges and join it to its 4 rail plates. Two mirror-image hands, 2 of each. 4 captive M4 nuts each. |
| Lift carriage bracket | 4 | `ToPrint-STL/lift_carriage_bracket.stl` | Joins the lift platform to its 4 rail plates; same part at every corner. 2 captive M4 nuts each. |
| Lift home-switch holder | 1 | `ToPrint-STL/lift_home_switch_holder.stl` | For a KW12-type switch. |

## 3. Frame and motion

| Part | Qty | Notes |
|---|---|---|
| 2020 aluminum extrusion, 430 mm *est.* | 4 | Posts. 30 mm taller than the original design, so an empty tip rack slides out under freshly loaded tips. |
| 2020 extrusion, 189.2 mm | 4 | Front/back of the bottom and top rings. |
| 2020 extrusion, 178 mm | 8 | Sides of the bottom, bed-level and top rings, plus the two head side bars. |
| 2020 inside corner bracket | 12 | Head side bars (4) and bed-level side bars (4) to the posts; stiffening-frame corners (4). |
| 2020 extrusion, 150 mm | 2 | Plunger-plate stiffening frame. |
| 2020 extrusion, 44 mm | 2 | Plunger-plate stiffening frame. |
| MGN9 linear rail, 360 mm *est.* | 4 | One per post. |
| MGN9H carriage | 8 | Lift platform (4) + plunger plate (4). |
| NEMA17 stepper, 40 mm body (~0.4 N m) | 1 | Lift. 5 mm shaft. |
| NEMA17 stepper, 48 mm body (~0.5 N m) | 1 | Plunger (drives all four screws). Stands on the top plate, shaft down. |
| T8x2 lead screw (8 mm, 2 mm lead) | 6 | Buy 150 mm: cut 4 plunger screws to ~131 mm (hung from the top plate); use 2 uncut for the lift (~148 mm needed for 66 mm of travel). |
| T8x2 anti-backlash nut | 4 | Plunger. |
| T8x2 brass flange nut | 2 | Lift (gravity keeps these loaded one way). |
| KFL08 flange bearing (8 mm bore) | 6 | 4 plunger (on the top plate), 2 lift. The plates assume 37 mm bolt spacing; check yours. |
| GT2 20T pulley, 8 mm bore, 6 mm belt | 6 | On the screws. |
| GT2 20T pulley, 5 mm bore, 6 mm belt | 2 | On the motors. |
| Smooth idler, 16 mm OD, 6 mm belt | 2 | Tensioners, each on a shoulder bolt. |
| GT2 closed-loop belt, 6 mm, 339-344 mm | 1 | Lift. Any loop in this range fits the tensioner's adjustment. |
| GT2 closed-loop belt, 6 mm, 539-544 mm | 1 | Plunger, under the top plate. Any loop in this range fits the tensioner's adjustment. |
| Steel rod, 8 mm, ~165 mm | 2 | Drawer D-shafts: grind or file a 0.8 mm deep flat along the length, and drill a 2.5 mm dimple 1.5 mm deep, 4 mm from the front end, opposite the flat. |
| M3 x 6 cone-point set screw | 2 | Holds each lever on its D-shaft (into the dimple). |
| Ball spring plunger, M6 | 2 | Drawer detents, in the ledges. |
| Micro limit switch (lever type, KW12-style) | 1 | Lift home. |
| Slotted optical endstop board (TCST2103-type, 3D-printer style) | 3 | Plunger home, one per sensor post. Check the body (24.5 x 10.8 x 6.3 mm, 3.1 mm slot, M3 ears 19 mm apart) and the output level when blocked (`PLUNGER_SW_ACTIVE`). |

## 4. Electronics

| Part | Qty | Notes |
|---|---|---|
| Arduino Uno | 1 | |
| CNC Shield V3 | 1 | Plunger in X, lift in Y. |
| Stepper driver (A4988 or DRV8825) | 2 | Set to 1/8 microstepping (first two jumpers on for either). |
| 20x4 LCD with I2C backpack (address 0x27) | 1 | |
| Rotary encoder with push switch | 1 | |
| Panel-mount USB-B extension, B female (panel) to B male, ~30 cm | 1 | Arduino USB out through the control box's left end, beside the DC jack. Typical socket: 12.5 x 11.5 mm cutout, M3 ears 30 mm apart; check yours against `USB_PANEL_*` in the model. |
| 12 V power supply, 5 A suggested | 1 | Plus a DC socket for the housing. |
| LM2596 buck converter | 1 | Optional (the original design used one). |
| Wire, Dupont leads, heat-shrink | | |

## 5. Pipetting consumables

| Part | Qty | Notes |
|---|---|---|
| Pipette tips, racked | as needed | For the cartridge fitted; the firmware caps volumes at the cartridge's tip capacity. |
| 96-well plates (SBS format) | as needed | |

## 5b. Syringe cartridge (per cartridge)

Everything that depends on the syringes and tips (see "Syringe cartridge" in
`01_Hardware/README.md`). Build one per tip family, or a spare.

| Part | Qty | File / notes |
|---|---|---|
| Cartridge plate, 3 mm steel | 1 | `ToLaserCut-DXF/cartridge_plate.dxf` |
| Plunger carrier, 3 mm steel | 1 | `ToLaserCut-DXF/plunger_carrier.dxf`; tap the 4 small (2.5 mm) holes M3 |
| Tip ejector plate, 3 mm steel | 1 | `ToLaserCut-DXF/tip_ejector_plate.dxf` |
| Syringe locking frame (printed) | 1 | `ToPrint-STL/syringe_lock_frame.stl`; a slot per row keys the tab stubs |
| Syringe barrel grip, slip fit (printed) | 1 | `ToPrint-STL/syringe_grip_slipfit.stl`; hangs from the cartridge plate by 4 ears |
| Pad retainer (printed) | 1 | `ToPrint-STL/pad_retainer.stl`; countersunk for 4 M3 |
| 1 mL Luer-slip syringes | 96 + spares | Plungers sanded from 9.5 to 8 mm in a drill so they fit the 9 mm spacing (per the build video). Buy from one batch so the bores match. Instead of cutting the flanged end off, trim the finger tabs to stubs: flange 8.2 mm across the stubs and at most 7.2 mm wide, face left flat (the model assumes a 6.4 mm barrel and a 1.2 mm flange; measure yours). |
| Heat-shrink tubing | 96 pieces | Over each syringe tip so this cartridge's tips seal; size it by test fitting. |
| M4 threaded rod, ~110 mm | 4 | Tip-ejector rods |
| Compression spring, ~6.4 mm OD x 20-25 mm, light | 4 | Hold the ejector plate up; one over each rod |
| M4 nut + washer | 12 | Ejector rods: under and over the plate, and the spring stop |
| Cartridge handle (printed) | 1 | `ToPrint-STL/cartridge_handle.stl` |
| M3 x 10 self-tapping | 2 | Handle to the cartridge plate |
| M3 x 14 self-tapping | 4 | Frame and cartridge plate into the grip's ears |
| M3 x 6 countersunk (ISO 10642) | 4 | Pad retainer down into the carrier's tapped holes; heads flush on top, tips flush underneath |

## 6. Fasteners

Counted from the Blender model, which places every one of them (the `fast_*` objects; see
`fasteners()` in `04_Blender/build_pipette.py`). Lengths were checked against each stack:
T-nut bolts end 4.2-6.0 mm into the slot (through the T-nut, short of the 2020 core), nut bolts
pass through their nut, and screws into plastic, motors or carriages get enough thread. Buy about
20 % extra. The cartridge's own screws are in section 5b.

| Fastener | Qty | Where |
|---|---|---|
| M5 x 8 button head + M5 T-nut (2020) | 80 | Corner brackets (64), top plate (12), base plate (4): 3 mm plates, so 5 mm into the slot. An M5 x 10 would go 7 mm in and bottom out on the extrusion's core (6.1 mm deep) before it clamps. |
| M5 x 10 + M5 T-nut (2020) | 24 | Inside corner brackets: head and bed-level side bars to the posts (16), stiffener corners (8) |
| M5 x 12 + M5 washer + M5 T-nut (2020) | 4 | Head brackets' feet up into the side bars |
| M5 x 14 + M5 T-nut (2020) | 2 | Control box to the bottom front bar, through the 3 mm back wall and the pad |
| M4 x 12 + nut | 28 | KFL08 bearings through the plate and the 5 mm flange (12); rail plates into the carriage brackets' captive nuts (16) |
| M4 x 16 + nut | 12 | Lift brackets down through the platform (8); well-plate nest (4) |
| M4 x 20 + M4 T-nut (2020) | 4 | Plunger carriage brackets: up from the bracket's pocket into the stiffener's long bar |
| M4 x 20 + nut | 4 | Plunger carriage brackets: down through the drive plate into the bracket's pocket |
| M4 x 30 + nut | 4 | Head brackets up through the pipette plate |
| M3 x 6 | 24 | MGN9H carriages to the rail plates (3 each, into the carriage) |
| M3 x 8 | 8 | Motors, into their faces |
| M3 x 8 + M3 T-nut (2020) | 72 | MGN9 rails into the posts (20 mm pitch) |
| M3 x 10 + nut | 24 | T8 nut flanges. Lift (8): heads on the platform, nuts under the flange (they clear the pulley by 1 mm with the bed down). Plunger (16): heads on the flange, nuts under the drive plate (pockets in the D-shaft troughs take the front ones). |
| M3 x 10 countersunk + nut | 6 | Plunger home flags: flush under the tab (it passes over the sensor at full eject), nuts on the drive plate |
| M3 x 10 countersunk, self-tapping | 4 | Control box base into the housing bosses |
| M3 x 12 + nut | 12 | Sensor posts to the pipette plate (6), tensioner brackets (4), USB panel socket (2) |
| M3 x 14 + nut | 14 | Drawer ledges and spacers to the pipette plate |
| M3 x 20 + nut | 2 | Lift home-switch holder to the base plate |
| M3 x 25 + nut | 4 | D-shaft troughs to the drive plate (front) |
| M3 x 25 + M3 T-nut (2020) | 4 | D-shaft troughs into the stiffener's long bars |
| M3 x 8 pan-head self-tapping | 6 | Optical endstops to their posts |
| M2 x 20 + nut | 2 | Lift home switch through its holder's walls |
| Shoulder bolt + nut | 2 | Tensioner idlers |

## 7. Tools and supplies

- Hacksaw or cut-off wheel (lead screws); calipers
- Drill (sanding the syringe plungers to 8 mm)
- Light lubricant for the lead screws
- For calibration: a 0.1 mg analytical balance, or dye plus a plate reader (see
  `02_Software/README.md`)

## Where to get things made

**Laser-cut metal** (upload DXF; all quote instantly online):
- [SendCutSend](https://sendcutsend.com/) (US): DXF/DWG/AI/STEP; 175+ materials; holes must be at
  least 50 % of the material thickness (fine for 3 mm; the smallest holes here are 3.2 mm, in the
  plunger plate).
- [OSH Cut](https://www.oshcut.com/) (US): DXF and most CAD formats; next-day options.
- [Fabworks](https://www.fabworks.com/) (US): online laser cutting.
- [JLCCNC sheet metal](https://jlccnc.com/sheet-metal-fabrication) (China): its quote flow
  expects a STEP file; low minimums.
- [PCBWay laser cutting](https://www.pcbway.com/rapid-prototyping/Sheet-metal/Laser-Cutting.html),
  [Xometry](https://www.xometry.com/capabilities/sheet-metal-fabrication/),
  [Protolabs](https://www.protolabs.com/services/sheet-metal-fabrication/laser-cutting/)

**3D printing** (upload STL):
- [Craftcloud](https://craftcloud3d.com/): compares quotes from 150+ print services.
- [JLC3DP](https://jlc3dp.com/): FDM, SLA, MJF and SLS; low per-part prices.
- [Xometry](https://www.xometry.com/capabilities/3d-printing-service/): also PLA/PETG FDM.
- Or a local makerspace/library printer: every part fits a common 220 mm bed.

**CNC machining**: not needed for this design, since every metal part is a flat laser-cut plate.
Worth considering only for upgrades, e.g. machined aluminum plates or reamed bearing holes:
[Xometry](https://www.xometry.com/capabilities/cnc-machining-service/), [JLCCNC](https://jlccnc.com/),
or PCBWay.

**Extrusion, rails and motion parts**: printer-parts suppliers, MISUMI (cut-to-length extrusion
and rails), or Amazon/AliExpress for the generic parts (NEMA17, T8 screws and nuts, KFL08, GT2).
