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
PLG_MOTOR_XY = (0.0, -79.0)                      # plunger motor, hangs under the pipette plate
LIFT_X = 70.0                                    # lift screws at (+/-LIFT_X, 0)
LIFT_MOTOR_XY = (0.0, 36.0)                      # lift motor, hangs under the base plate
HOME_SW_XY = (-40.0, -35.0)                      # lift home switch on the base plate
HEAD_MOUNT_XY = [(sx * 68.0, sy * 20.0) for sx in (-1, 1) for sy in (-1, 1)]   # pipette plate -> side brackets

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
T8_NUT_SCREW_D = 3.2                             # M3, close clearance to keep the web to the bore

LIFT_PLATE = (160.0, 200.0)
BASE_PLATE = (229.2, 120.0)
BASE_MOUNT_XY = [(sx * 104.6, sy * 45.0) for sx in (-1, 1) for sy in (-1, 1)]  # into side extrusions
CORNER_BLOCK_HOLES = [(sx * 65.0, sy * 90.0) for sx in (-1, 1) for sy in (-1, 1)]   # same as the plunger plate

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
    """T8 flange nut: center bore + 4 M3 flange screws on a 16 mm circle at 45 deg.
    bore_d = SCREW_CLEAR_D when the nut body points away from the plate (plunger), or
    T8_NUT_BODY_BORE_D when the body passes through it (lift)."""
    q = T8_NUT_PCD / 2 / math.sqrt(2)
    return [circle(x, y, bore_d)] + [circle(x + sx * q, y + sy * q, T8_NUT_SCREW_D)
                                     for sx in (-1, 1) for sy in (-1, 1)]


def motor_holes(x, y):
    q = NEMA17_BOLTS / 2
    return [circle(x, y, NEMA17_BOSS_D)] + [circle(x + sx * q, y + sy * q, M3) for sx in (-1, 1) for sy in (-1, 1)]


def tensioner_holes(x, y):
    return slot_y(x, y, SLOT_TRAVEL + M5, M5) + [circle(x + s * TENSIONER_HOLE_DX, y, M3) for s in (-1, 1)]


def near_r(e, r):
    return e[0] == "CIRCLE" and abs(e[3] - r) < 0.02


# ---------------------------------------------------------------- parts
# The repo plates are drawn in their own frames; these offsets map machine -> DXF coordinates.
PIPETTE_OFFSET = (-49.5, 31.5)     # array center in pipette_plate.DXF
PLUNGER_OFFSET = (-49.5, -31.5)    # array center in plunger_plate.DXF


def pipette_plate():
    src = read_entities(os.path.join(REPO_DXF, "pipette_plate.DXF"))
    # drop the old per-motor T8 nut bores (d 11) and their flange screws (d 3.5)
    keep = [e for e in src if not (near_r(e, 5.5) or near_r(e, 1.75))]
    ox, oy = PIPETTE_OFFSET
    new = []
    for x, y in PS_XY:                                       # screw clearance + KFL08 (flange along y)
        new += [circle(x, y, SCREW_CLEAR_D)]
        new += [circle(x, y + s * KFL08_BOLTS / 2, M4) for s in (-1, 1)]
    new += motor_holes(*PLG_MOTOR_XY)
    new += tensioner_holes(0.0, PLG_IDLER_Y)
    new += [circle(x, y, M4) for x, y in HEAD_MOUNT_XY]
    return keep + [shift(e, ox, oy) for e in new]


def plunger_plate():
    src = read_entities(os.path.join(REPO_DXF, "plunger_plate.DXF"))
    # drop the old motor cutouts (d 33) and motor screws (d 3.4)
    keep = [e for e in src if not (near_r(e, 16.5) or near_r(e, 1.7))]
    ox, oy = PLUNGER_OFFSET
    new = []
    for x, y in PS_XY:                                       # nuts sit on the holder plate, body up
        new += nut_holes(x, y, SCREW_CLEAR_D)
    return keep + [shift(e, ox, oy) for e in new]


def lift_plate():
    w, h = LIFT_PLATE
    ents = rounded_rect(w, h)
    for s in (-1, 1):                                        # nut flange underneath, body up through
        ents += nut_holes(s * LIFT_X, 0.0, T8_NUT_BODY_BORE_D)
    ents += [circle(x, y, M4) for x, y in CORNER_BLOCK_HOLES]
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
