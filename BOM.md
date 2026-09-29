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
| Pipette plate | 1 | `MotorLift/ToLaserCut-DXF/pipette_plate_motorlift.dxf` | Generated | Plunger screws + KFL08s, plunger motor, tensioner slot, side-bracket holes. |
| Plunger plate | 1 | `MotorLift/ToLaserCut-DXF/plunger_plate_motorlift.dxf` | Generated | 4 T8 nut cutouts; old motor cutouts removed. |
| Lift platform | 1 | `MotorLift/ToLaserCut-DXF/lift_plate.dxf` | Generated | 160 x 200 mm, 2 T8 nut cutouts. |
| Lift base plate | 1 | `MotorLift/ToLaserCut-DXF/lift_base_plate.dxf` | Generated | 229.2 x 120 mm. |
| Interface plate, high | 8 | `ToLaserCut-DXF/interface_plate_high.DXF` | Repo | 4 for the plunger plate, 4 for the lift platform. |
| Frame corner bracket | 16 | `ToLaserCut-DXF/angle_bracket-(optionally can be purchased).DXF` | Repo | Or buy 2020 flat L corner plates. |

Not needed in this layout: `interface_plate_low` (the pipette plate now bolts to side bars),
`bearing_plate`, `lever_cutout*`, `linkage1`, `square_stock`.

## 2. 3D-printed parts

PETG is a good default for the load-bearing parts (the syringe grip is a press fit). Suggested:
4 perimeters, 40 % infill. The largest part (`ScreenHousing`, 218 x 100 x 72 mm) needs a bed of at
least 220 mm.

| Part | Qty | File | Status | Notes |
|---|---|---|---|---|
| Syringe barrel grip | 1 | `ToPrint-STL/syringe_grip_static.STL` | Repo | Barrels press-fit into it. |
| Syringe/plunger retainer | 1 | `ToPrint-STL/S-P_plate.STL` | Repo | |
| Plunger holder plate | 1 | `MotorLift/ToPrint-STL/plunger_holder_plate_motorlift.stl` | Generated | The plunger nuts sit on it. |
| Corner block | 8 | `ToPrint-STL/LimitSwitch_holder_A.STL` | Repo | 4 on the plunger plate, 4 on the lift platform. |
| Corner block + switch, pipette level | 4 | `ToPrint-STL/LimitSwitch_holder_B.STL` | Repo | |
| Electronics housing (sloped) | 1 | `MotorLift/ToPrint-STL/control_box_housing_sloped.stl` | Generated | Repo housing with the screen panel tilted 10 deg toward the user. Lies in front of the base; 2 screws through its back wall into the bottom front bar. |
| Electronics lid | 1 | `ToPrint-STL/electronics_lid.STL` | Repo | |
| Well-plate tray | 1 | `ToPrint-STL/Optional/vertical_tray.STL` | Repo | Laid flat; it sets the well-plate height the firmware expects. |
| Head bracket | 2 | `MotorLift/ToPrint-STL/head_bracket.stl` | Generated | Bolts the pipette plate to the side bars. |
| Belt tensioner bracket (lift) | 1 | `MotorLift/ToPrint-STL/tensioner_bracket_lift.stl` | Generated | |
| Belt tensioner bracket (plunger) | 1 | `MotorLift/ToPrint-STL/tensioner_bracket_plunger.stl` | Generated | |
| Lift home-switch holder | 1 | `MotorLift/ToPrint-STL/lift_home_switch_holder.stl` | Generated | For a KW12-type switch. |

Not needed: `bed_left/right`, `bearing_holder`, `bearing_insert`, `bearing_insert_lid`,
`lever_handle`, `slide_block`, `slider_holder`. Optional: the comb jigs and `horizontal_tray`.

## 3. Frame and motion

| Part | Qty | Notes |
|---|---|---|
| 2020 aluminum extrusion, 400 mm *est.* | 4 | Posts. |
| 2020 extrusion, 189.2 mm | 4 | Front/back of the bottom and top rings. |
| 2020 extrusion, 178 mm | 8 | Sides of the bottom, bed-level and top rings, plus the two head side bars. |
| 2020 inside corner bracket | 4 | Head side bars to the posts. |
| 2020 extrusion, 150 mm | 2 | Plunger-plate stiffening frame. |
| 2020 extrusion, 54 mm | 2 | Plunger-plate stiffening frame. |
| MGN9 linear rail, 330 mm *est.* | 4 | One per post. |
| MGN9H carriage | 8 | Lift platform (4) + plunger plate (4). |
| NEMA17 stepper, 40 mm body (~0.4 N m) | 1 | Lift. 5 mm shaft. |
| NEMA17 stepper, 48 mm body (~0.5 N m) | 1 | Plunger (drives all four screws). |
| T8x2 lead screw (8 mm, 2 mm lead) | 6 | Buy 150 mm and cut: 4 plunger at ~127 mm, 2 lift at ~118 mm. |
| T8x2 anti-backlash nut | 4 | Plunger. |
| T8x2 brass flange nut | 2 | Lift (gravity keeps these loaded one way). |
| KFL08 flange bearing (8 mm bore) | 6 | 4 plunger, 2 lift. The plates assume 37 mm bolt spacing; check yours. |
| GT2 20T pulley, 8 mm bore, 6 mm belt | 6 | On the screws. |
| GT2 20T pulley, 5 mm bore, 6 mm belt | 2 | On the motors. |
| Smooth idler, 16 mm OD, 6 mm belt | 2 | Tensioners, each on a shoulder bolt. |
| GT2 closed-loop belt, 6 mm, 339-344 mm | 1 | Lift. Any loop in this range fits the tensioner's adjustment. |
| GT2 closed-loop belt, 6 mm, 544-549 mm | 1 | Plunger. |
| Micro limit switch (lever type, KW12-style) | 4 | 3 plunger corners + 1 lift home. |

## 4. Electronics

| Part | Qty | Notes |
|---|---|---|
| Arduino Uno | 1 | |
| CNC Shield V3 | 1 | Plunger in X, lift in Y. |
| Stepper driver (A4988 or DRV8825) | 2 | Set to 1/8 microstepping (first two jumpers on for either). |
| 20x4 LCD with I2C backpack (address 0x27) | 1 | |
| Rotary encoder with push switch | 1 | |
| 12 V power supply, 5 A suggested | 1 | Plus a DC socket for the housing. |
| LM2596 buck converter | 1 | Optional; in the original electronics. |
| Wire, Dupont leads, heat-shrink | | |

## 5. Pipetting consumables

| Part | Qty | Notes |
|---|---|---|
| 1 mL Luer-slip syringes | 96 + spares | Plungers sanded from 9.5 to 8 mm in a drill so they fit the 9 mm spacing (per the build video). Buy from one batch so the bores match. |
| 200 uL pipette tips, racked | as needed | The firmware caps volumes at 200 uL. |
| Heat-shrink tubing | 96 pieces | Over each syringe tip so the pipette tips seal (per the video); size it by test fitting. |
| 96-well plates (SBS format) | as needed | |

## 6. Fasteners (approximate; buy about 20 % extra)

The hardware README notes the originals are mostly 8 mm-long M3, M4 and M5 bolts with nuts and
T-nuts.

| Fastener | Approx. qty | Where |
|---|---|---|
| M5 x 10 + M5 T-nut (2020) | 90 | Corner brackets (64), inside brackets (8), stiffening frame (8), base plate (4), head brackets (4) |
| M3 x 8 + M3 T-nut (2020) | 70 | MGN9 rails (20 mm hole pitch) |
| M3 x 6-8 | 40 | Carriages to interface plates, electronics housing |
| M3 x 10 + nut | 24 | Motors (8), lift nuts (8), tensioner brackets (4), switch holder (2), spares |
| M3 x 16 + nut | 16 | Plunger nuts (through nut flange, holder plate, 1.5 mm washers and plunger plate) |
| M3 flat washer (7 mm OD) | 24 | Under the M3 nuts at the T8 nut cutouts, to span the slots (lift 8, plunger 16) |
| M4 x 10 + nut | 32 | Interface plates (16), KFL08 bearings (12), head brackets to the pipette plate (4) |
| M2 x 16 + nut | 2 | Lift home switch |
| M2/M2.5 screws | 6 | Plunger-level limit switches |
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
