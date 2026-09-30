# Bill of materials: motorized-lift build

For the layout on the `motorized-lift` branch: fixed pipette head, lead-screw bed lift, one
belt-synced plunger motor (model: `04_Blender/variant_motor_lift.py`, firmware:
`02_Software/arduino/MotorLift`). Quantities are counted from the Blender model. The layout was
reconstructed from the creator's build video, so treat lengths marked *est.* as starting points
and confirm against your own frame. The creator's original build came to roughly $250 in parts.

**File status** for fabricated parts:
- **Repo**: use the original file in `01_Hardware` as is.
- **Generated**: new or modified for this layout, in `01_Hardware/MotorLift/` (see its README for
  what changed, what was checked, and how to regenerate).

## 1. Laser-cut metal

The repo doesn't state a material or thickness; the model assumes **3 mm steel**. The machine
works around liquids, so consider 304 stainless or a coated steel over bare mild steel. Aluminum
would be lighter but about 3x more flexible, which costs plunger accuracy.

| Part | Qty | File | Status | Notes |
|---|---|---|---|---|
| Pipette plate | 1 | `MotorLift/ToLaserCut-DXF/pipette_plate_motorlift.dxf` | Generated | A U open at the front for the cartridge drawer; head-bracket, sensor-post and channel holes. |
| Plunger (drive) plate | 1 | `MotorLift/ToLaserCut-DXF/plunger_plate_motorlift.dxf` | Generated | 160 x 200 mm: 4 T8 nut cutouts, 8 carriage-bracket holes, 3 sensor flags, 8 trough bolts; no plunger-rod holes. |
| Top plate | 1 | `MotorLift/ToLaserCut-DXF/top_plate.dxf` | Generated | On the top ring: the plunger screws' KFL08s, the plunger motor, the belt tensioner. |
| Drawer channel ledge | 2 | `MotorLift/ToLaserCut-DXF/cart_ledge.dxf` | Generated | Flip one over for the left side. Tap the M6 hole. |
| Lift platform | 1 | `MotorLift/ToLaserCut-DXF/lift_plate.dxf` | Generated | 160 x 200 mm, 2 T8 nut cutouts, 8 carriage-bracket holes, 4 well-plate-nest holes. |
| Lift base plate | 1 | `MotorLift/ToLaserCut-DXF/lift_base_plate.dxf` | Generated | 229.2 x 120 mm. |
| Interface plate, high | 4 | `ToLaserCut-DXF/interface_plate_high.DXF` | Repo | Lift platform rail plates. |
| Plunger rail plate | 4 | `MotorLift/ToLaserCut-DXF/plunger_rail_plate.dxf` | Generated | A taller, rectangular `interface_plate_high` that reaches down to the plunger carriage brackets. |
| Frame corner bracket | 16 | `ToLaserCut-DXF/angle_bracket-(optionally can be purchased).DXF` | Repo | Or buy 2020 flat L corner plates. |

Not needed in this layout: `interface_plate_low` (the pipette plate now bolts to side bars),
`bearing_plate`, `lever_cutout*`, `linkage1`, `square_stock`.

## 2. 3D-printed parts

PETG is a good default for the load-bearing parts (the syringe grip is a press fit). Suggested:
4 perimeters, 40 % infill. The largest part (`ScreenHousing`, 218 x 100 x 72 mm) needs a bed of at
least 220 mm.

| Part | Qty | File | Status | Notes |
|---|---|---|---|---|
| Plunger sensor post | 3 | `MotorLift/ToPrint-STL/optical_switch_post.stl` | Generated | Holds a slotted optical endstop laid flat under the plunger plate; 2 M3 to the pipette plate. |
| Plunger sensor flag | 3 | `MotorLift/ToPrint-STL/plunger_flag.stl` | Generated | Hangs from the plunger plate through the sensor's slot; 2 M3. |
| Electronics housing (sloped) | 1 | `MotorLift/ToPrint-STL/control_box_housing_sloped.stl` | Generated | Repo housing with the screen panel tilted 10 deg toward the user, a skirt that runs its walls down to the bench, the lid bosses extended to the base, and a back pad with 2 M5 into T-nuts in the bottom front bar. |
| Control box base | 1 | `MotorLift/ToPrint-STL/control_box_base.stl` | Generated | Closes the housing's underside (replaces the repo lid, which was sized to sit between the posts). 4 countersunk M3 into the bosses. |
| Well-plate nest | 1 | `MotorLift/ToPrint-STL/well_plate_nest.stl` | Generated | Locates an SBS plate on the lift platform at the height the firmware expects (replaces the flat repo tray). 4 M4 to the platform. |
| Head bracket | 2 | `MotorLift/ToPrint-STL/head_bracket.stl` | Generated | Bolts the pipette plate to the side bars. |
| Belt tensioner bracket (lift) | 1 | `MotorLift/ToPrint-STL/tensioner_bracket_lift.stl` | Generated | |
| Belt tensioner bracket (plunger) | 1 | `MotorLift/ToPrint-STL/tensioner_bracket_plunger.stl` | Generated | On the top plate. |
| Drawer channel spacer | 1 + 1 mirrored | `MotorLift/ToPrint-STL/cart_spacer_R.stl` | Generated | Mirror for the left. |
| D-shaft trough | 1 + 1 mirrored | `MotorLift/ToPrint-STL/dshaft_trough_R.stl` | Generated | Mirror for the left. |
| D-shaft lever | 2 | `MotorLift/ToPrint-STL/dshaft_lever.stl` | Generated | |
| Plunger carriage bracket | 2 + 2 | `MotorLift/ToPrint-STL/plunger_carriage_bracket_RF_LB.stl`, `..._RB_LF.stl` | Generated | Hang under the plunger plate's side edges and join it to its 4 rail plates. Two mirror-image hands, 2 of each. 4 captive M4 nuts each. |
| Lift carriage bracket | 4 | `MotorLift/ToPrint-STL/lift_carriage_bracket.stl` | Generated | Joins the lift platform to its 4 rail plates; same part at every corner. 2 captive M4 nuts each. |
| Lift home-switch holder | 1 | `MotorLift/ToPrint-STL/lift_home_switch_holder.stl` | Generated | For a KW12-type switch. |

Not needed: `bed_left/right`, `bearing_holder`, `bearing_insert`, `bearing_insert_lid`,
`lever_handle`, `slide_block`, `slider_holder`, `LimitSwitch_holder_A/B`, `electronics_lid`,
`vertical_tray`, `S-P_plate`, `syringe_grip_static`. Optional: the comb jigs and `horizontal_tray`.

## 3. Frame and motion

| Part | Qty | Notes |
|---|---|---|
| 2020 aluminum extrusion, 400 mm *est.* | 4 | Posts. |
| 2020 extrusion, 189.2 mm | 4 | Front/back of the bottom and top rings. |
| 2020 extrusion, 178 mm | 8 | Sides of the bottom, bed-level and top rings, plus the two head side bars. |
| 2020 inside corner bracket | 12 | Head side bars (4) and bed-level side bars (4) to the posts; stiffening-frame corners (4). |
| 2020 extrusion, 150 mm | 2 | Plunger-plate stiffening frame. |
| 2020 extrusion, 44 mm | 2 | Plunger-plate stiffening frame. |
| MGN9 linear rail, 330 mm *est.* | 4 | One per post. |
| MGN9H carriage | 8 | Lift platform (4) + plunger plate (4). |
| NEMA17 stepper, 40 mm body (~0.4 N m) | 1 | Lift. 5 mm shaft. |
| NEMA17 stepper, 48 mm body (~0.5 N m) | 1 | Plunger (drives all four screws). Stands on the top plate, shaft down. |
| T8x2 lead screw (8 mm, 2 mm lead) | 6 | Buy 150 mm and cut: 4 plunger at ~131 mm (hung from the top plate), 2 lift at ~118 mm. |
| T8x2 anti-backlash nut | 4 | Plunger. |
| T8x2 brass flange nut | 2 | Lift (gravity keeps these loaded one way). |
| KFL08 flange bearing (8 mm bore) | 6 | 4 plunger (on the top plate), 2 lift. The plates assume 37 mm bolt spacing; check yours. |
| GT2 20T pulley, 8 mm bore, 6 mm belt | 6 | On the screws. |
| GT2 20T pulley, 5 mm bore, 6 mm belt | 2 | On the motors. |
| Smooth idler, 16 mm OD, 6 mm belt | 2 | Tensioners, each on a shoulder bolt. |
| GT2 closed-loop belt, 6 mm, 339-344 mm | 1 | Lift. Any loop in this range fits the tensioner's adjustment. |
| GT2 closed-loop belt, 6 mm, 542-547 mm | 1 | Plunger, under the top plate. Any loop in this range fits the tensioner's adjustment. |
| Steel rod, 8 mm, ~165 mm | 2 | Drawer D-shafts: grind or file a 0.8 mm deep flat along the length, and drill a 2 mm cross hole 4 mm from the front end, square to the flat. |
| Spring pin, 2 x 16 mm | 2 | Pins each lever to its D-shaft. |
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
| LM2596 buck converter | 1 | Optional; in the original electronics. |
| Wire, Dupont leads, heat-shrink | | |

## 5. Pipetting consumables

| Part | Qty | Notes |
|---|---|---|
| Pipette tips, racked | as needed | For the cartridge fitted; the firmware caps volumes at the cartridge's tip capacity. |
| 96-well plates (SBS format) | as needed | |

## 5b. Syringe cartridge (per cartridge)

Everything that depends on the syringes and tips (see "Syringe cartridge" in
`01_Hardware/MotorLift/README.md`). Build one per tip family, or a spare.

| Part | Qty | File / notes |
|---|---|---|
| Cartridge plate, 3 mm steel | 1 | `MotorLift/ToLaserCut-DXF/cartridge_plate.dxf` |
| Plunger carrier, 3 mm steel | 1 | `MotorLift/ToLaserCut-DXF/plunger_carrier.dxf` |
| Tip ejector plate, 3 mm steel | 1 | `MotorLift/ToLaserCut-DXF/tip_ejector_plate.dxf` |
| Syringe locking frame (printed) | 1 | `MotorLift/ToPrint-STL/syringe_lock_frame.stl`; a slot per row keys the tab stubs |
| Syringe barrel grip, slip fit (printed) | 1 | `MotorLift/ToPrint-STL/syringe_grip_slipfit.stl`; hangs from the cartridge plate by 4 ears |
| Pad retainer (printed) | 1 | `MotorLift/ToPrint-STL/pad_retainer.stl` |
| 1 mL Luer-slip syringes | 96 + spares | Plungers sanded from 9.5 to 8 mm in a drill so they fit the 9 mm spacing (per the build video). Buy from one batch so the bores match. Instead of cutting the flanged end off, trim the finger tabs to stubs: flange 8.2 mm across the stubs and at most 7.2 mm wide, face left flat (the model assumes a 6.4 mm barrel and a 1.2 mm flange; measure yours). |
| Heat-shrink tubing | 96 pieces | Over each syringe tip so this cartridge's tips seal; size it by test fitting. |
| M4 threaded rod, ~110 mm | 4 | Tip-ejector rods |
| Compression spring, ~6.4 mm OD x 20-25 mm, light | 4 | Hold the ejector plate up; one over each rod |
| M4 nut + washer | 12 | Ejector rods: under and over the plate, and the spring stop |
| Cartridge handle (printed) | 1 | `MotorLift/ToPrint-STL/cartridge_handle.stl` |
| M3 x 10 self-tapping | 2 | Handle to the cartridge plate |
| M3 x 14 self-tapping | 4 | Frame and cartridge plate into the grip's ears |

## 6. Fasteners (approximate; buy about 20 % extra)

The hardware README notes the originals are mostly 8 mm-long M3, M4 and M5 bolts with nuts and
T-nuts.

| Fastener | Approx. qty | Where |
|---|---|---|
| M5 x 10 + M5 T-nut (2020) | 108 | Corner brackets (64), inside corner brackets (24), top plate (12), base plate (4), head brackets (4) |
| M5 x 12 + M5 T-nut (2020) | 2 | Control box pad to the bottom front bar |
| M3 x 8 + M3 T-nut (2020) | 70 | MGN9 rails (20 mm hole pitch) |
| M3 x 6-8 | 40 | Carriages to interface plates, electronics housing |
| M3 x 10 + nut | 46 | Motors (8), lift nuts (8), plunger nuts through the drive plate (16), tensioner brackets (4), lift switch holder (2), sensor flags (6), spares |
| M3 x 12 + nut | 8 | Plunger switch posts to the pipette plate (6), USB panel socket (2) |
| M3 x 10 countersunk, self-tapping | 4 | Control box base into the housing bosses |
| M3 flat washer (7 mm OD) | 24 | Under the M3 nuts at the T8 nut cutouts, to span the slots (lift 8, plunger 16) |
| M4 x 10 + nut | 12 | KFL08 bearings |
| M4 x 30 + nut | 4 | Head brackets up through the pipette plate |
| M4 x 12 + nut | 16 | Lift and plunger rail plates into the carriage brackets' captive nuts (8 + 8) |
| M4 x 16 + nut | 12 | Lift brackets down through the platform (8); well-plate nest (4) |
| M4 x 20 + M4 T-nut (2020) | 8 | Plunger carriage brackets up through the drive plate into the stiffening frame's bars |
| M3 x 14 + nut | 14 | Drawer ledges and spacers to the pipette plate |
| M3 x 25 + nut | 4 | D-shaft troughs to the drive plate (front bolts) |
| M3 x 25 + M3 T-nut (2020) | 4 | D-shaft troughs up into the stiffener's long bars |
| M2 x 16 + nut | 2 | Lift home switch in its holder |
| M3 x 8 self-tapping | 6 | Optical endstops to their posts |
| Shoulder bolt + nut for idlers | 2 | Tensioners |

## 7. Tools and supplies

- Hacksaw or cut-off wheel (lead screws); calipers
- Drill (sanding the syringe plungers to 8 mm)
- Light lubricant for the lead screws
- For calibration: a 0.1 mg analytical balance, or dye plus a plate reader (see
  `02_Software/README.txt`)

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
