"""Layout dimensions for the motorized-lift build, and the laser-cut DXFs derived from them.

    python 01_Hardware/MotorLift/make_dxf.py

writes ToLaserCut-DXF/*.dxf next to this file (units: millimeters, DXF R12, LINE/ARC/CIRCLE only).
The Blender model (04_Blender/variant_motor_lift.py) imports this module for the same numbers and
builds its plates from the generated DXFs, so the model and the cut files always agree.

Coordinates in the layout constants are in the machine frame: origin on the syringe-array
center, +x right, +y back (the front of the machine is -y).
"""
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DXF = os.path.join(HERE, "..", "ToLaserCut-DXF")
OUT = os.path.join(HERE, "ToLaserCut-DXF")

# ---------------------------------------------------------------- layout (machine frame, mm)
PLATE_T = 3.0                                    # all laser-cut parts
PS_XY = [(-65.0, -58.9), (65.0, -58.9), (-65.0, 58.9), (65.0, 58.9)]   # plunger screws: LF RF LB RB
PLG_MOTOR_XY = (0.0, -76.0)                      # plunger motor, on the top plate
LIFT_X = 70.0                                    # lift screws at (+/-LIFT_X, 0)
LIFT_MOTOR_XY = (0.0, 36.0)                      # lift motor, hangs under the base plate
HOME_SW_XY = (-40.0, -35.0)                      # lift home switch on the base plate
HEAD_MOUNT_XY = [(sx * 75.0, sy * 20.0) for sx in (-1, 1) for sy in (-1, 1)]   # pipette plate -> side brackets

PULLEY_R = 6.37                                  # GT2 20T pitch radius
IDLER_R = 8.8                                    # belt pitch line on a 16 mm smooth idler
TENSION_TAKEUP = 16.0                            # nominal idler deflection
SLOT_TRAVEL = 12.0                               # tensioner adjustment (+/-6)
PLG_IDLER_Y = PS_XY[3][1] + PULLEY_R + IDLER_R - TENSION_TAKEUP   # plunger idler, back run
LIFT_IDLER_Y = -(PULLEY_R + IDLER_R) + TENSION_TAKEUP             # lift idler, run between screws
TENSIONER_HOLE_DX = 11.0                         # bracket screws either side of the slot

KFL08_BOLTS = 37.0                               # KFL08 bolt spacing (check your bearings)
NEMA17_BOLTS = 31.0
NEMA17_BOSS_D = 23.0
T8_NUT_BODY_BORE_D = 10.4                        # nut body passes through the plate (10.2 mm body)
T8_NUT_PCD = 16.0                                # flange screw circle
T8_NUT_SCREW_D = 3.4                             # M3 clearance; slot width in the nut cutout

LIFT_PLATE = (160.0, 200.0)
BASE_PLATE = (229.2, 120.0)
BASE_MOUNT_XY = [(sx * 104.6, sy * 45.0) for sx in (-1, 1) for sy in (-1, 1)]  # into side extrusions
LIFT_BRACKET_X = 71.0                            # lift carriage brackets: 2 M4 down through the plate each,
LIFT_BRACKET_Y = (38.0, 80.0)                    # either side of the rail plate's M4 holes (y 49, 69)
LIFT_BRACKET_HOLES = [(sx * LIFT_BRACKET_X, sy * y) for sx in (-1, 1) for sy in (-1, 1) for y in LIFT_BRACKET_Y]
# Plunger carriage brackets hang under the drive (plunger) plate's side edges, outside its cartridge
# channels (x > 67.5). The plunger rail plates are a taller version of interface_plate_high whose M4
# row lands in the brackets; their frame: DXF (-10, 0) sits on the carriage center (y = CARRIAGE_Y),
# DXF x runs toward the machine's middle, DXF y is up, and DXF y = 0 is RAIL_ZC_BELOW_MID below the
# plunger plate's mid-plane (ZC_HIGH in build_pipette.py).
CARRIAGE_Y = 99.0                                # PY in build_pipette.py
RAIL_ZC_BELOW_MID = 10.0
PLG_BRACKET_PLATE_XY = [(72.0, 10.0), (72.0, 33.0)]    # per corner (mirrored): M4 through the plate
PLG_BRACKET_RAIL_Y = (22.0, 44.0)                # rail-plate M4 bolts into the bracket
PLG_BRACKET_ROW_BELOW_MID = 7.5                  # rail-plate bolt row, below the plunger plate's mid-plane
PLG_BRACKET_HOLES = [(sx * x, sy * y) for sx in (-1, 1) for sy in (-1, 1) for x, y in PLG_BRACKET_PLATE_XY]
DRIVE_PLATE = (160.0, 200.0)                     # the drive (plunger) plate, widened to reach the brackets
# 2020 stiffening frame on the drive plate: long bars along x at y = +/-STIFF_LONG_Y (the bracket
# bolts at (+/-72, +/-33) come up into M4 T-nuts in them), short bars along y at x = +/-STIFF_SHORT_X
# (inside corner brackets to the long bars only).
STIFF_LONG_Y = 32.0
STIFF_SHORT_X = 58.0
# Plunger home sensors: slotted optical endstops on printed posts on the pipette plate's arms (2 M3
# each, along y), each with a flag hanging from the drive plate (2 M3, along y). Any one homes the
# plunger; three for the level check. Well-plate nest on the lift plate: 4 M4.
SWITCH_POSTS = [(-73.0, -80.0), (73.0, -80.0), (-73.0, 80.0)]
SWITCH_POST_HOLE_DY = 14.0
SWITCH_POST_HOLES = [(x, y + s * SWITCH_POST_HOLE_DY) for x, y in SWITCH_POSTS for s in (-1, 1)]
FLAG_HOLE_DY = 6.0
FLAG_HOLES = [(x, y + s * FLAG_HOLE_DY) for x, y in SWITCH_POSTS for s in (-1, 1)]
# Plunger drive on the top plate (top_plate.dxf), which sits on the frame's top ring: the 4 screws
# hang from KFL08s on it, their pulleys and the belt run under it inside the ring, and the motor
# stands on it with its shaft down. That leaves the head clear for the cartridge drawer.
TOP_PLATE = (229.2, 218.0)
TOP_MOUNT_XY = [(sx * x, sy * 99.0) for sx in (-1, 1) for sy in (-1, 1) for x in (30.0, 75.0)] + \
               [(sx * 104.6, sy * 30.0) for sx in (-1, 1) for sy in (-1, 1)]     # M5 into the top ring
# Syringe cartridge: a drawer that slides in from the front (see "Syringe cartridge" in README.md).
# - The pipette plate is a U, open at the front: its slot is +/-CART_SLOT_X wide and runs back to
#   CART_SLOT_BACK. The cartridge plate slides in under its arms, riding on a steel ledge each side
#   (cart_ledge.dxf) held CART_GAP below the arm on a printed spacer, until it stops at the back;
#   a spring plunger in each ledge clicks into it (CART_DETENTS).
# - The plunger carrier slides in under the drive plate on two 8 mm D-shafts in printed troughs;
#   a quarter turn of each shaft's lever clamps it up against the drive plate with no play.
# Nothing else is in the way at the front: the plunger drive is on the top plate.
ARRAY_GRID = [(-49.5 + 9 * i, -31.5 + 9 * j) for j in range(8) for i in range(12)]
CART_SLOT_X, CART_SLOT_BACK = 57.0, 50.0
CART_PLATE = (62.0, 50.0)                        # cartridge plate half sizes
CART_GAP = 3.3                                   # its channel: 3 mm plate + 0.3 mm
LEDGE_X = (54.3, 69.0)                           # ledge under the arm
LEDGE_BOLTS = [(64.2, y) for y in (-95.0, -70.0, -45.0, -20.0, 5.0, 30.0, 46.0)]   # right side; mirrored
CART_DETENTS = [(sx * 60.0, 40.0) for sx in (-1, 1)]
CART_HANDLE_SCREWS = [(sx * 15.0, -46.0) for sx in (-1, 1)]
PC_PLATE = (60.0, 50.0)                          # plunger carrier half sizes (clears the T8 screws)
DSHAFT_X, DSHAFT_D, DSHAFT_FLAT = 55.5, 8.0, 0.8  # D-shaft clamps: axis, diameter, depth of the flat
TROUGH_BOLTS = [(64.0, y) for y in (-95.0, -80.0, -32.0, 32.0)]   # right side; mirrored. +/-32: T-nuts
FRAME_SCREWS = [(sx * 27.0, sy * 38.8) for sx in (-1, 1) for sy in (-1, 1)]   # frame + carrier + grip
# Tip ejector: a plate under the barrel ends with a hole around each nozzle, hung on 4 M4 rods
# that run up through the cartridge plate; the plunger carrier pushes them down when the plunger
# goes below home. All of it belongs to the cartridge.
EJ_ROD_X, EJ_ROD_Y = 44.0, 45.0
EJ_ROD_HOLES = [(sx * EJ_ROD_X, sy * EJ_ROD_Y) for sx in (-1, 1) for sy in (-1, 1)]
EJ_PLATE = (112.0, 98.0)
EJ_HOLE_D = 5.8                                  # passes the heat-shrunk nozzle, not the tip rim
EJ_ROD_HOLE_D = 6.0                              # loose: the plate tilts a few degrees on the rods
NEST_HOLES = [(sx * 55.0, sy * 15.0) for sx in (-1, 1) for sy in (-1, 1)]

# Hole diameters
M3, M4, M5 = 3.4, 4.5, 5.5
SCREW_CLEAR_D = 9.0                              # T8 screw through a plate


# ---------------------------------------------------------------- DXF read / write
def read_entities(path):
    """LINE/ARC/CIRCLE entities from a DXF as dicts of group code -> value."""
    lines = [l.strip() for l in open(path, errors="ignore").read().splitlines()]
    ents, cur, inside = [], None, False
    for code, val in zip(lines[0::2], lines[1::2]):
        if code == "2" and val == "ENTITIES":
            inside = True
            continue
        if not inside:
            continue
        if code == "0":
            if cur:
                ents.append(cur)
            if val == "ENDSEC":
                break
            cur = {"t": val}
        elif cur is not None and code not in cur:
            cur[code] = val
    out = []
    for e in ents:
        f = lambda k: float(e[k])
        if e["t"] == "LINE":
            out.append(("LINE", f("10"), f("20"), f("11"), f("21")))
        elif e["t"] == "CIRCLE":
            out.append(("CIRCLE", f("10"), f("20"), f("40")))
        elif e["t"] == "ARC":
            out.append(("ARC", f("10"), f("20"), f("40"), f("50"), f("51")))
    return out


def write_dxf(path, ents):
    rows = ["0", "SECTION", "2", "HEADER", "9", "$ACADVER", "1", "AC1009", "0", "ENDSEC",
            "0", "SECTION", "2", "ENTITIES"]
    for e in ents:
        if e[0] == "LINE":
            _, x0, y0, x1, y1 = e
            rows += ["0", "LINE", "8", "0", "10", f"{x0:.4f}", "20", f"{y0:.4f}", "30", "0",
                     "11", f"{x1:.4f}", "21", f"{y1:.4f}", "31", "0"]
        elif e[0] == "CIRCLE":
            _, x, y, r = e
            rows += ["0", "CIRCLE", "8", "0", "10", f"{x:.4f}", "20", f"{y:.4f}", "30", "0", "40", f"{r:.4f}"]
        elif e[0] == "ARC":
            _, x, y, r, a0, a1 = e
            rows += ["0", "ARC", "8", "0", "10", f"{x:.4f}", "20", f"{y:.4f}", "30", "0", "40", f"{r:.4f}",
                     "50", f"{a0:.4f}", "51", f"{a1:.4f}"]
    rows += ["0", "ENDSEC", "0", "EOF"]
    with open(path, "w", newline="\n") as fh:
        fh.write("\n".join(rows) + "\n")


def circle(x, y, d):
    return ("CIRCLE", x, y, d / 2)


def slot_y(x, y, length, width):
    """Stadium slot along y, centered at (x, y); length is end to end."""
    r, h = width / 2, (length - width) / 2
    return [("LINE", x - r, y - h, x - r, y + h), ("LINE", x + r, y - h, x + r, y + h),
            ("ARC", x, y + h, r, 0.0, 180.0), ("ARC", x, y - h, r, 180.0, 360.0)]


def rounded_rect(w, h, r=2.0, cx=0.0, cy=0.0):
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    return [("LINE", x0 + r, y0, x1 - r, y0), ("LINE", x1, y0 + r, x1, y1 - r),
            ("LINE", x1 - r, y1, x0 + r, y1), ("LINE", x0, y1 - r, x0, y0 + r),
            ("ARC", x1 - r, y0 + r, r, 270.0, 360.0), ("ARC", x1 - r, y1 - r, r, 0.0, 90.0),
            ("ARC", x0 + r, y1 - r, r, 90.0, 180.0), ("ARC", x0 + r, y0 + r, r, 180.0, 270.0)]


def nut_holes(x, y, bore_d):
    """T8 flange nut: one cloverleaf cutout, a center bore with 4 radial slots for the M3 flange
    screws (16 mm circle, at 45 deg). Separate holes would leave only 1-2 mm of steel between the
    bore and each screw, under the plate thickness most laser shops accept; the slots remove that
    web. The screws only locate the nut (the flange carries the load), and a washer under each
    M3 nut spans the slot. bore_d = SCREW_CLEAR_D when the nut body points away from the plate
    (plunger), or T8_NUT_BODY_BORE_D when the body passes through it (lift)."""
    R, w, pr = bore_d / 2, T8_NUT_SCREW_D / 2, T8_NUT_PCD / 2
    t0 = math.sqrt(R * R - w * w)                  # where a slot side meets the bore
    da = math.degrees(math.asin(w / R))
    ents = []
    for k in range(4):
        a = 45.0 + 90.0 * k
        ux, uy = math.cos(math.radians(a)), math.sin(math.radians(a))
        nx, ny = -uy, ux
        for s in (-1, 1):                          # slot sides
            ents.append(("LINE", x + t0 * ux + s * w * nx, y + t0 * uy + s * w * ny,
                         x + pr * ux + s * w * nx, y + pr * uy + s * w * ny))
        ents.append(("ARC", x + pr * ux, y + pr * uy, w, a - 90.0, a + 90.0))   # slot end
        ents.append(("ARC", x, y, R, a + da, a + 90.0 - da))                    # bore to next slot
    return ents


def motor_holes(x, y):
    q = NEMA17_BOLTS / 2
    return [circle(x, y, NEMA17_BOSS_D)] + [circle(x + sx * q, y + sy * q, M3) for sx in (-1, 1) for sy in (-1, 1)]


def tensioner_holes(x, y):
    return slot_y(x, y, SLOT_TRAVEL + M5, M5) + [circle(x + s * TENSIONER_HOLE_DX, y, M3) for s in (-1, 1)]


def polygon(pts):
    return [("LINE", *pts[i], *pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def mirror4(quadrant):
    """A closed outline (point list) from its +x/+y quarter, listed from the +x axis to the +y axis."""
    q = list(quadrant)
    q2 = [(-x, y) for x, y in reversed(q)]
    q3 = [(-x, -y) for x, y in q]
    q4 = [(x, -y) for x, y in reversed(q)]
    return q + q2[1:] + q3[1:] + q4[1:-1]


def near_r(e, r):
    return e[0] == "CIRCLE" and abs(e[3] - r) < 0.02


def at_any(e, pts, offset):
    """A circle centered on one of pts (machine frame; offset maps machine -> DXF)."""
    return e[0] == "CIRCLE" and any(abs(e[1] - x - offset[0]) < 0.05 and abs(e[2] - y - offset[1]) < 0.05
                                    for x, y in pts)


# ---------------------------------------------------------------- parts
# The repo plates are drawn in their own frames; these offsets map machine -> DXF coordinates.
PIPETTE_OFFSET = (-49.5, 31.5)     # array center in pipette_plate.DXF
PLUNGER_OFFSET = (-49.5, -31.5)    # array center in plunger_plate.DXF


def pipette_plate():
    """The pipette plate, now a U open at the front for the cartridge drawer (drawn from scratch; the
    repo plate's features all moved or went: plunger drive to the top plate, syringes to the
    cartridge). Held by the head brackets; carries the channel ledges and the sensor posts."""
    ox, oy = PIPETTE_OFFSET
    w, h = DRIVE_PLATE
    hw, hh, sx_, sb = w / 2, h / 2, CART_SLOT_X, CART_SLOT_BACK
    new = polygon([(hw, -hh), (hw, hh), (-hw, hh), (-hw, -hh), (-sx_, -hh), (-sx_, sb), (sx_, sb), (sx_, -hh)])
    new += [circle(x, y, M4) for x, y in HEAD_MOUNT_XY]
    new += [circle(x, y, M3) for x, y in SWITCH_POST_HOLES]
    new += [circle(sx * x, y, M3) for x, y in LEDGE_BOLTS for sx in (-1, 1)]
    return [shift(e, ox, oy) for e in new]


def plunger_plate():
    """The drive plate (drawn from scratch, widened to +/-80 to reach the carriage brackets): T8 nut
    cutouts, bracket and flag holes, and the D-shaft troughs' bolts. The plunger rods and pads are
    the cartridge's."""
    ox, oy = PLUNGER_OFFSET
    new = rounded_rect(*DRIVE_PLATE)
    for x, y in PS_XY:                                       # nuts sit on it, body up
        new += nut_holes(x, y, SCREW_CLEAR_D)
    new += [circle(x, y, M4) for x, y in PLG_BRACKET_HOLES]  # carriage brackets underneath
    new += [circle(x, y, M3) for x, y in FLAG_HOLES]         # optical-endstop flags underneath
    new += [circle(sx * x, y, M3) for x, y in TROUGH_BOLTS for sx in (-1, 1)]
    return [shift(e, ox, oy) for e in new]


def top_plate():
    """Top plate on the frame's top ring: KFL08s for the 4 plunger screws (flange along y), the
    plunger motor (shaft down), the belt tensioner slot, and M5s into the ring."""
    ents = rounded_rect(*TOP_PLATE)
    for x, y in PS_XY:
        ents += [circle(x, y, SCREW_CLEAR_D)]
        ents += [circle(x, y + s * KFL08_BOLTS / 2, M4) for s in (-1, 1)]
    ents += motor_holes(*PLG_MOTOR_XY)
    ents += tensioner_holes(0.0, PLG_IDLER_Y)
    ents += [circle(x, y, M5) for x, y in TOP_MOUNT_XY]
    return ents


def cart_ledge():
    """Channel ledge for the right-hand side (flip it over for the left): 3 mm steel under the
    pipette plate's arm, the cartridge plate rides on it; M3 through the arm and the printed spacer,
    and a tapped M6 hole for the spring plunger."""
    (x0, x1), y0, y1 = LEDGE_X, -100.0, CART_SLOT_BACK
    ents = rounded_rect(x1 - x0, y1 - y0, 1.0, (x0 + x1) / 2, (y0 + y1) / 2)
    ents += [circle(x, y, M3) for x, y in LEDGE_BOLTS]
    ents += [circle(abs(x), y, 5.0) for x, y in CART_DETENTS[1:]]        # M6 tap drill
    return ents


def plunger_rail_plate():
    """interface_plate_high made rectangular and 24 mm longer, so it reaches down beside the
    plunger plate to its carriage bracket: same carriage holes, M4 row moved into the bracket."""
    src = read_entities(os.path.join(REPO_DXF, "interface_plate_high.DXF"))
    ents = [e for e in src if near_r(e, 1.7)]               # the 3 carriage screws
    x0, x1, y0, y1 = -20.0, CARRIAGE_Y - 10.0 - (PLG_BRACKET_RAIL_Y[0] - 9.0), -9.0, 20.0
    ents += rounded_rect(x1 - x0, y1 - y0, 2.0, (x0 + x1) / 2, (y0 + y1) / 2)
    row = RAIL_ZC_BELOW_MID - PLG_BRACKET_ROW_BELOW_MID
    ents += [circle(CARRIAGE_Y - 10.0 - y, row, M4) for y in PLG_BRACKET_RAIL_Y]
    return ents


def cartridge_plate():
    """Carrier plate: 3 mm steel, the cartridge's drawer. Its edges run in the channels under the
    pipette plate's arms; the barrels, frame, grip and ejector hang from it."""
    ents = rounded_rect(2 * CART_PLATE[0], 2 * CART_PLATE[1], 2.0)
    ents += [circle(x, y, 6.5) for x, y in ARRAY_GRID]                 # barrels
    ents += [circle(x, y, M4) for x, y in EJ_ROD_HOLES]                # ejector rods slide here
    ents += [circle(x, y, M3) for x, y in FRAME_SCREWS + CART_HANDLE_SCREWS]
    ents += [circle(x, y, 3.0) for x, y in CART_DETENTS]               # the spring plungers click in
    return ents


def plunger_carrier():
    """Plunger carrier: 3 mm steel under the thumb pads. Its edges run over the D-shaft clamps
    under the drive plate; it pushes the ejector rods."""
    ents = rounded_rect(2 * PC_PLATE[0], 2 * PC_PLATE[1], 2.0)
    ents += [circle(x, y, 3.2) for x, y in ARRAY_GRID]                 # plunger rods
    return ents


def tip_ejector_plate():
    w, h = EJ_PLATE
    ents = rounded_rect(w, h)
    ents += [circle(x, y, EJ_HOLE_D) for x, y in ARRAY_GRID]
    ents += [circle(x, y, EJ_ROD_HOLE_D) for x, y in EJ_ROD_HOLES]
    return ents


def lift_plate():
    w, h = LIFT_PLATE
    ents = rounded_rect(w, h)
    for s in (-1, 1):                                        # nut flange underneath, body up through
        ents += nut_holes(s * LIFT_X, 0.0, T8_NUT_BODY_BORE_D)
    ents += [circle(x, y, M4) for x, y in LIFT_BRACKET_HOLES]
    ents += [circle(x, y, M4) for x, y in NEST_HOLES]
    return ents


def lift_base_plate():
    w, h = BASE_PLATE
    ents = rounded_rect(w, h)
    for s in (-1, 1):                                        # screw clearance + KFL08 (flange along x)
        ents += [circle(s * LIFT_X, 0.0, SCREW_CLEAR_D)]
        ents += [circle(s * LIFT_X + t * KFL08_BOLTS / 2, 0.0, M4) for t in (-1, 1)]
    ents += motor_holes(*LIFT_MOTOR_XY)
    ents += tensioner_holes(0.0, LIFT_IDLER_Y)
    ents += [circle(HOME_SW_XY[0] + s * 14.0, HOME_SW_XY[1], M3) for s in (-1, 1)]
    ents += [circle(x, y, M5) for x, y in BASE_MOUNT_XY]
    return ents


def shift(e, dx, dy):
    if e[0] == "LINE":
        return ("LINE", e[1] + dx, e[2] + dy, e[3] + dx, e[4] + dy)
    if e[0] == "CIRCLE":
        return ("CIRCLE", e[1] + dx, e[2] + dy, e[3])
    return ("ARC", e[1] + dx, e[2] + dy, e[3], e[4], e[5])


PARTS = {
    "pipette_plate_motorlift": pipette_plate,
    "plunger_plate_motorlift": plunger_plate,
    "plunger_rail_plate": plunger_rail_plate,
    "tip_ejector_plate": tip_ejector_plate,
    "cartridge_plate": cartridge_plate,
    "top_plate": top_plate,
    "cart_ledge": cart_ledge,
    "plunger_carrier": plunger_carrier,
    "lift_plate": lift_plate,
    "lift_base_plate": lift_base_plate,
}


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, fn in PARTS.items():
        ents = fn()
        write_dxf(os.path.join(OUT, name + ".dxf"), ents)
        print(f"{name}.dxf: {sum(e[0] == 'CIRCLE' for e in ents)} holes, {len(ents)} entities")


if __name__ == "__main__":
    main()
