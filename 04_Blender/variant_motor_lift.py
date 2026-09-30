"""Variant: fixed head, motorized lead-screw bed lift, belt-synced plunger drive.

Builds the baseline (build_pipette.py) and then modifies it:
  * lever mechanism, fixed bed and the bed ring's front/back members are removed
  * LIFT: one NEMA17 drives two T8 screws (x = +/-72, clear of the tray) through a closed GT2 loop.
    Screws run in KFL08 flange bearings under a steel base plate hung beneath the bed-ring side
    members; the motor hangs below that plate. Brass nuts under the platform, which rides the same
    four MGN9H rails as before. Positions are programmable per labware; the screw holds position.
  * PLUNGER: the four per-screw steppers become one NEMA17 + closed GT2 loop around four T8 screws
    at (+/-65, +/-58.9). The screws hang from KFL08s on a plate across the frame's top ring, with
    the pulleys, belt and idler under it and the motor standing on it; only the nuts ride on the
    drive (plunger) plate. Mechanically synced -> the plate cannot rack if a step is missed.
    Accuracy upgrades: T8x2 plunger screws with anti-backlash nuts (spring + second nut), a 2020
    stiffening frame on the drive plate so the plate bends less under stopper friction,
    and a 48 mm (~0.5 N m class) motor so one motor matches the original four's thrust.
  * both belts have a smooth-idler tensioner on a slotted printed bracket; the lift homes onto a
    micro switch pressed by the platform underside at the bottom of travel
  * frees two of the CNC shield's four driver slots (X = plunger, Y = lift)
  * the pipette plate is bolted through two printed brackets to a 2020 bar along each side of
    the frame; the lift platform's rail plates bolt to four printed carriage brackets on the plate
  * the control box lies in front of the base with its screen panel sloped toward the user
    (CONTROL_SLOPE_DEG), low enough that well plates still slide in from the front over it
  * everything syringe- and tip-specific is a cartridge that slides in at the front like a drawer:
    its plate runs in channels under the pipette plate (a U, open at the front), its plunger carrier
    over two D-shaft clamps under the drive plate; a tip ejector and optical home sensors let the
    plunger go past home to push the tips off (see "Syringe cartridge" in 01_Hardware/MotorLift/README.md)
Layout numbers and the laser-cut plates come from 01_Hardware/MotorLift/make_dxf.py (run it first
if the DXFs are missing); export_motor_lift_parts.py writes the printed parts as STL.
Run: blender --python 04_Blender/variant_motor_lift.py  (or open it in Blender's Text Editor and Run Script)
"""
import bpy, bmesh, math, os, importlib.util
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

def _script_dir():
    """This script's folder, whether run with `blender --python`, from Blender's Text Editor,
    or exec'd with __file__ set. PIPETTE_BLENDER_DIR overrides as a last resort."""
    f = globals().get("__file__", "")
    if f and os.path.isfile(f):
        return os.path.dirname(os.path.abspath(f))
    txt = bpy.data.texts.get(os.path.basename(f)) if f else None
    if txt and txt.filepath:
        return os.path.dirname(bpy.path.abspath(txt.filepath))
    env = os.environ.get("PIPETTE_BLENDER_DIR")
    if env:
        return env
    raise RuntimeError("Can't find the 04_Blender folder: run with `blender --python <script>`, "
                       "open the script in Blender's Text Editor, or set PIPETTE_BLENDER_DIR.")


HERE = _script_dir()
g = {"__name__": "pipette_lib", "__file__": os.path.join(HERE, "build_pipette.py")}
exec(open(os.path.join(HERE, "build_pipette.py"), encoding="utf-8").read(), g)   # functions only

FAB = os.path.normpath(os.path.join(HERE, "..", "01_Hardware", "MotorLift"))
_spec = importlib.util.spec_from_file_location("motorlift_layout", os.path.join(FAB, "make_dxf.py"))
L = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(L)             # layout constants shared with the laser-cut DXFs
FAB_DXF = os.path.join(FAB, "ToLaserCut-DXF")

D = math.radians
M = None
box, cyl, dxf_part, dup, new_obj = g["box"], g["cyl"], g["dxf_part"], g["dup"], g["new_obj"]
IF_X, IX, PY, T, P, FH = g["IF_X"], g["IX"], g["PY"], g["T"], g["P"], g["FH"]
PLG_MID, PLG_TOP, BED_RECT_Z = g["PLG_MID"], g["PLG_TOP"], g["BED_RECT_Z"]

# ---------------------------------------------------------------- parameters
PULLEY_R = L.PULLEY_R             # GT2 20T pitch radius
# lift
LIFT_X = L.LIFT_X                 # screws at (+/-LIFT_X, 0): outside the tray (+/-63.9)
LIFT_MOTOR_XY = L.LIFT_MOTOR_XY
BASE_Z = BED_RECT_Z - 10 - T      # base plate top = underside of bed-ring side members (52..55)
LIFT_PLUS = BASE_Z + T + 1        # pulley stack starts 1 mm above the base plate
LIFT0 = 78.0                      # platform underside at the bottom of travel
TRAY_H, PLATE_H = 15.0, 14.4
TIP_DEPTH = 9.0                   # tips this far into the wells at the top of travel
SEAT = P - T                      # syringe flanges sit on the cartridge carrier plate, under the pipette plate
TIP_DROP = 8.0                    # tips sit this much lower than the repo model: the carrier plate (3 mm)
TIP_BOTTOM = P - 112 - TIP_DROP   # and the ejector plate (3 mm) under the barrel ends, plus 2 mm
LIFT_TRAVEL = (TIP_BOTTOM + TIP_DEPTH) - (LIFT0 + T + TRAY_H + PLATE_H)
LIFT_LEAD = 2.0                   # T8x2 on the lift: force + self-locking
BRK_H = 18.0                      # lift carriage bracket height above the plate
BRK_BOLT_Z = LIFT0 + T + 10.0     # rail-plate M4 row: the rail plates ride this high so it clears the plate
LIFT_IF_HOLE_Y = (PY - 30.0, PY - 50.0)   # the rail plate's 2 M4 holes (DXF x 20, 40; anchor x -10 at PY)
PLG_BRK_H = 18.0                  # plunger carriage bracket height under the plate
assert L.CARRIAGE_Y == PY and PLG_MID - L.RAIL_ZC_BELOW_MID == g["ZC_HIGH"]
# plunger
PS_XY = L.PS_XY                   # order: LF, RF, LB, RB
PLG_MOTOR_XY = L.PLG_MOTOR_XY
SWITCH_TOP = P + 39 + 11.5        # limit-switch lever tops on the pipette-plate corner blocks
PLG_REST = (SWITCH_TOP + 0.5) - (PLG_MID - T / 2)   # home = plate just off the switches (firmware homes onto them)
ASPIRATE = 12.0                   # animation stroke (~215 uL in a 4.78 mm-bore 1 mL syringe)
PLG_LEAD = 2.0                    # T8x2: 4x the resolution and thrust of the original T8x8
# tensioners / homing
IDLER_R = L.IDLER_R               # belt pitch-line radius on a 16 mm smooth idler (back-side wrap)
TENSION_TAKEUP = L.TENSION_TAKEUP # idler deflects the run this far; slot gives +/-6 mm.
                                  # (take-up ~ deflection^2 / span, so a shallow idler takes up almost nothing)
HOME_SW_XY = L.HOME_SW_XY         # lift home switch: under the platform, clear of belt + nuts
HOME_OVERTRAVEL = 0.8             # lever deflection when the platform is home
# Syringes: typical 1 mL (Luer-slip) values; measure yours and adjust. The finger tabs are cut
# back to short stubs so the flange is SYR_KEY_L across the tabs and SYR_KEY_W wide; the stubs key
# each barrel into its row's slot under the locking frame (tabs along x).
SYR_BARREL_D = 6.4                # barrel OD (the pipette plate's holes are 6.5)
SYR_FLANGE_T = 1.2                # flange thickness
SYR_KEY_L, SYR_KEY_W = 8.2, 7.2   # trimmed flange: across the tab stubs (x) x width (y)
GRIP_SLIP_D = 6.9                 # printed grip holes: a slip fit, no press (prints come out small)
FRAME_T = 4.0                     # locking frame thickness
FRAME_HALF = (55.5, 41.0)         # locking frame, inside the pipette plate's drawer slot
PC_BELOW = 6.0                    # plunger carrier (3 mm steel) + pad retainer (3 mm) under the drive plate
TOP_PZ0 = FH - 1 - 16             # plunger pulleys hang under the top plate, inside the top ring
CART_HANDLE_H = 12.0              # cartridge handle, under the front of the cartridge plate
LEVER_HUB = (8.0, 8.0)            # D-shaft lever hub: radius, length along the shaft
LEVER_ARM = (24.0, 5.6)           # lever arm: reach from the axis, thickness in the turning plane
LEVER_OPEN_DEG = 30.0             # open lever: arm this far outward of straight down (clear of the rail plate)
KEEP_X = 52.5                     # the outer plunger rods pass at |x| <= 51 as the drawer slides: drawer hardware stays outside
EJ_SPRING_Z = (SEAT, SEAT + 20)   # ejector springs: carrier plate top to the spring nut
# Parts that come out with the syringe cartridge (see check_cartridge_removal)
CARTRIDGE = ("cartridge_plate", "cartridge_handle", "syringe_barrels", "syringe_lock_frame", "syringe_grip",
             "eject_", "plunger_carrier", "pad_retainer", "plungers_x96")
# USB: a panel-mount USB-B socket on the control box's left end, forward of the DC jack, joined
# to the Arduino by a short USB-B extension. Typical socket: 12.5 x 11.5 mm body, 2 M3 ears 30 mm
# apart (check yours).
# The control box stands CBOX_BACK_GAP off the frame: clear of the corner brackets' bolt heads
# (2.75 mm) by 0.75. Positions measured on the housing below were taken at a 0.5 mm gap: CBOX_DY.
CBOX_BACK_GAP = 2.75 + 0.75
CBOX_DY = -(CBOX_BACK_GAP - 0.5)
USB_PANEL_YZ = (-185.0 + CBOX_DY, 36.0)   # socket center on the left end wall
USB_PANEL_CUT = (12.5, 11.5)      # body cutout (y x z)
USB_PANEL_EARS = 30.0             # M3 hole spacing, along y
# Tip ejector (see tip_ejector()): the carriage brackets reach the front rods EJ_GAP_F below home
# and the back rods EJ_GAP_B below, so the plate tilts and strips the tips a few rows at a time,
# front to back; EJECT_MM below home every tip has been pushed EJ_STROKE off its nozzle.
EJ_GAP_F, EJ_GAP_B = 1.0, 5.5
EJ_STROKE = 6.0
EJECT_MM = EJ_GAP_B + EJ_STROKE
# Plunger home sensors: slotted optical endstops (TCST2103-type fork, 24.5 x 10.8 x 6.3 mm body,
# 3.1 mm slot, M3 ears 19 mm apart; check yours). Laid flat, so each flag passes straight through
# its slot; the sensor sits OPT_BELOW under the plunger plate at home so the plate and the flag's
# 3 mm tab clear it when it goes EJECT_MM lower.
OPT_BODY = (24.5, 10.8, 6.3)
OPT_SLOT = 3.1
OPT_EARS = 19.0
OPT_BELOW = EJECT_MM + 3.0 + 1.5
CBOX_BOSSES = [(sx * 79.0, y + CBOX_DY) for sx in (-1, 1) for y in (-207.5, -117.5)]   # repo lid screw bosses (measured)
CONTROL_SLOPE_DEG = 10.0          # control-box screen panel tilted toward the user (front edge lowered)


# ---------------------------------------------------------------- part helpers
def _cone(bm, r1, r2, z0, z1, seg=32, xy=(0, 0)):
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=z1 - z0,
                          matrix=Matrix.Translation((xy[0], xy[1], (z0 + z1) / 2)))


def pulley(name, x, y, z0, coll):
    """GT2 20T: 6 mm hub + 8 mm toothed section with flanges; origin on the axis."""
    bm = bmesh.new()
    _cone(bm, 6.5, 6.5, z0, z0 + 6)
    _cone(bm, 9.5, 9.5, z0 + 6, z0 + 7)
    _cone(bm, 8.0, 8.0, z0 + 7, z0 + 15, seg=40)
    _cone(bm, 9.5, 9.5, z0 + 15, z0 + 16)
    bmesh.ops.translate(bm, verts=bm.verts[:], vec=(0, 0, 0))
    o = new_obj(name, bm, coll, M["chrome"])
    o.data.transform(Matrix.Translation((0, 0, 0)))
    o.location = (x, y, 0)
    return o


def kfl08(name, x, y, z_face, down, coll, rot=0.0):
    """KFL08 two-bolt flange bearing: 5 mm flange at z_face, housing on the `down` side."""
    s = -1 if down else 1
    bm = bmesh.new()
    pts = [(24 * math.cos(D(a)), 13.5 * math.sin(D(a))) for a in range(0, 360, 12)]
    f = bm.faces.new([bm.verts.new((px, py, 0)) for px, py in pts])
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, verts=[v for v in ext['geom'] if isinstance(v, bmesh.types.BMVert)], vec=(0, 0, 5 * s))
    _cone(bm, 13, 13, min(0, 12 * s), max(0, 12 * s))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    o = new_obj(name, bm, coll, M["pla_grey"])
    o.location = (x, y, z_face)
    o.rotation_euler.z = rot
    return o


def nema17(prefix, x, y, z_face, face_up, coll, length=40.0):
    """Motor hanging from a plate: mounting face at z_face, body below (face_up) or above.
    length: 40 mm body (~0.4 N m) or 48 mm (~0.5 N m class)."""
    s = -1 if face_up else 1
    zc = z_face + s * length / 2
    box(prefix + "_body", (42.3, 42.3, length - 8), (x, y, zc), coll, M["motor"], bevel=0.8)
    box(prefix + "_capF", (42.3, 42.3, 4), (x, y, z_face + s * 2), coll, M["chrome"], bevel=1.5)
    box(prefix + "_capB", (42.3, 42.3, 4), (x, y, z_face + s * (length - 2)), coll, M["chrome"], bevel=1.5)
    cyl(prefix + "_shaft", 2.5, 18, (x, y, z_face - s * 9 + s * 0), coll, M["chrome"], seg=16)


def spring(name, x, y, z0, z1, r_coil, r_wire, turns, coll, m):
    """Helical compression spring from z0 to z1 (swept circle along a helix)."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions, cu.bevel_depth, cu.bevel_resolution = '3D', r_wire, 2
    n = int(turns * 24)
    sp = cu.splines.new('POLY')
    sp.points.add(n)
    for i in range(n + 1):
        a = 2 * math.pi * turns * i / n
        sp.points[i].co = (r_coil * math.cos(a), r_coil * math.sin(a), z0 + (z1 - z0) * i / n, 1)
    tmp = bpy.data.objects.new(name + "_crv", cu)
    bpy.data.collections[coll].objects.link(tmp)
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    o = bpy.data.objects.new(name, me)
    bpy.data.collections[coll].objects.link(o)
    me.materials.append(m)
    o.location = (x, y, 0)
    return o


def belt_route(seq, n_arc=48):
    """Pitch-line path of a closed belt through pulleys given in counter-clockwise order.
    seq: (cx, cy, r) with r > 0 for toothed pulleys inside the loop and r < 0 for smooth idlers
    pressing on the belt's back from outside. Returns (points, length)."""
    k = len(seq)
    normals = []                       # outward normal of each straight run i -> i+1
    for i in range(k):
        (xa, ya, ra), (xb, yb, rb) = seq[i], seq[(i + 1) % k]
        L = math.hypot(xb - xa, yb - ya)
        tx, ty = (xb - xa) / L, (yb - ya) / L
        a = (ra - rb) / L
        b = math.sqrt(max(0.0, 1 - a * a))
        normals.append((a * tx + b * ty, a * ty - b * tx))
    pts, length = [], 0.0
    for i in range(k):
        cx, cy, r = seq[i]
        n_in, n_out = normals[i - 1], normals[i]
        a0, a1 = math.atan2(n_in[1], n_in[0]), math.atan2(n_out[1], n_out[0])
        tau = 2 * math.pi
        if r > 0:
            sweep = (a1 - a0) % tau                    # toothed pulley: wraps counter-clockwise
            sweep = 0.0 if sweep > tau - 1e-9 else sweep
        else:
            sweep = -((a0 - a1) % tau)                 # back-side idler: wraps clockwise
            sweep = 0.0 if sweep < -(tau - 1e-9) else sweep
        steps = max(2, int(abs(sweep) / (2 * math.pi) * n_arc) + 1)
        for j in range(steps + 1):
            t = a0 + sweep * j / steps
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
        length += abs(r * sweep)
        cx2, cy2, r2 = seq[(i + 1) % k]
        length += math.dist((cx + r * n_out[0], cy + r * n_out[1]),
                            (cx2 + r2 * n_out[0], cy2 + r2 * n_out[1]))
    clean = [pts[0]]
    for q in pts[1:]:
        if math.dist(q, clean[-1]) > 0.05:
            clean.append(q)
    if math.dist(clean[0], clean[-1]) < 0.05:
        clean.pop()
    return clean, length


def belt(name, seq, zc, coll, w=6.0):
    """Closed GT2 belt (6 mm wide) along belt_route(seq). Returns length (mm)."""
    path, length = belt_route(seq)
    n = len(path)
    bm = bmesh.new()
    rings = []
    for off, z in ((-0.6, zc - w / 2), (0.8, zc - w / 2), (0.8, zc + w / 2), (-0.6, zc + w / 2)):
        ring = []
        for i in range(n):
            a, b, c = path[i - 1], path[i], path[(i + 1) % n]
            nx, ny = (c[1] - a[1]), -(c[0] - a[0])          # outward normal (CCW path)
            l = math.hypot(nx, ny)
            ring.append(bm.verts.new((b[0] + off * nx / l, b[1] + off * ny / l, z)))
        rings.append(ring)
    for k in range(4):
        r0, r1 = rings[k], rings[(k + 1) % 4]
        for i in range(n):
            bm.faces.new((r0[i], r0[(i + 1) % n], r1[(i + 1) % n], r1[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    new_obj(name, bm, coll, M["rubber"])
    return length


def idler(name, x, y, z0, coll):
    """Smooth 16 mm idler (the belt's back rides on it) on a shoulder bolt; same stack as pulley()."""
    bm = bmesh.new()
    _cone(bm, 9.5, 9.5, z0 + 6, z0 + 7)
    _cone(bm, 8.0, 8.0, z0 + 7, z0 + 15, seg=40)
    _cone(bm, 9.5, 9.5, z0 + 15, z0 + 16)
    o = new_obj(name, bm, coll, M["chrome"])
    o.location = (x, y, 0)
    bm = bmesh.new()
    _cone(bm, 2.5, 2.5, z0 - 6, z0 + 16)
    _cone(bm, 4.0, 4.0, z0 + 16, z0 + 19)
    new_obj(name + "_bolt", bm, coll, M["motor"]).location = (x, y, 0)
    return o


def slot_prism(bm, cx, cy, length, width, z0, z1):
    """Stadium prism along y (for cutting an adjustment slot)."""
    r, h = width / 2, (length - width) / 2
    pts = [(h + r * math.cos(D(a)), r * math.sin(D(a))) for a in range(-90, 91, 15)] + \
          [(-h + r * math.cos(D(a)), r * math.sin(D(a))) for a in range(90, 271, 15)]
    f = bm.faces.new([bm.verts.new((cx - py, cy + px, z0)) for px, py in pts])
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, verts=[v for v in ext['geom'] if isinstance(v, bmesh.types.BMVert)], vec=(0, 0, z1 - z0))


def boolean(obj, bm, op='DIFFERENCE', solver='EXACT', self_intersect=False):
    """Apply a cutter (or union) built in world coordinates to obj and bake the result."""
    cut = new_obj(obj.name + "_tool", bm, obj.users_collection[0].name)
    mod = obj.modifiers.new("tool", 'BOOLEAN')
    mod.object, mod.operation, mod.solver = cut, op, solver
    mod.use_self = self_intersect
    bpy.context.view_layer.update()
    mats = list(obj.data.materials)
    obj.data = bpy.data.meshes.new_from_object(obj.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    obj.modifiers.clear()
    if not obj.data.materials:
        for m in mats:
            obj.data.materials.append(m)
    bpy.data.objects.remove(cut)


def _block(bm, x0, x1, y0, y1, z0, z1):
    g_ = bmesh.ops.create_cube(bm, size=1)
    for v in g_["verts"]:
        v.co = Vector(((x0 + x1) / 2 + v.co.x * (x1 - x0), (y0 + y1) / 2 + v.co.y * (y1 - y0),
                       (z0 + z1) / 2 + v.co.z * (z1 - z0)))


def _bar(bm, p0, p1, r, seg=24):
    """Cylinder from p0 to p1 (for holes along any axis)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=d.length,
                          matrix=Matrix.Translation((p0 + p1) / 2) @ rot)


def tensioner(prefix, x, y_idler, z_base, height, coll):
    """Printed bracket: 12 mm adjustment slot along y for the idler's shoulder bolt, plus two M3
    screws into the plate. The model shows the idler at TENSION_TAKEUP (mid-slot)."""
    br = box(prefix + "_bracket", (30, 34, height), (x, y_idler, z_base + height / 2), coll, M["pla"], bevel=1.0)
    bm = bmesh.new()
    slot_prism(bm, x, y_idler, L.SLOT_TRAVEL + L.M5, L.M5, z_base - 5, z_base + height + 5)
    for s_ in (-1, 1):
        _cone(bm, L.M3 / 2, L.M3 / 2, z_base - 5, z_base + height + 5, xy=(x + s_ * L.TENSIONER_HOLE_DX, y_idler))
    boolean(br, bm)
    return br


def microswitch(prefix, x, y, z_base, lever_top, coll, cbore=None):
    """Printed holder + micro limit switch (KW12-style, 20 x 10 x 6.4 mm, mounting holes 9.5 mm
    apart). The switch stands in a channel between two walls, clamped by two M2 screws through
    the walls; two M3 screws hold the base to the plate outside the switch footprint."""
    sw_h, lev, wall_h = 10.0, 1.0, 8.0
    zt = lever_top - lev - 0.5 - sw_h                 # base top = switch bottom
    h = box(prefix + "_holder", (34, 16, zt - z_base), (x, y, (z_base + zt) / 2), coll, M["pla"])
    bm = bmesh.new()
    for s_ in (-1, 1):                                # walls either side of a 6.6 mm channel
        _block(bm, x - 10, x + 10, y + s_ * 3.3, y + s_ * 8.0, zt - 0.01, zt + wall_h)
    boolean(h, bm, 'UNION')
    bm = bmesh.new()
    for s_ in (-1, 1):
        _cone(bm, L.M3 / 2, L.M3 / 2, z_base - 5, zt + 5, xy=(x + s_ * 14, y))
        _bar(bm, (x + s_ * 4.75, y - 12, zt + 3), (x + s_ * 4.75, y + 12, zt + 3), 1.1)
    boolean(h, bm)
    if cbore:                                         # tall post: screw heads sit cbore above the plate
        bm = bmesh.new()
        for s_ in (-1, 1):
            _cone(bm, 3.2, 3.2, z_base + cbore, zt + 5, xy=(x + s_ * 14, y))
        boolean(h, bm)
    box(prefix + "_body", (20, 6.5, sw_h), (x, y, zt + sw_h / 2), coll, M["pla_grey"])
    box(prefix + "_lever", (18, 4, lev), (x + 1, y, lever_top - lev / 2), coll, M["chrome"])


def optical_post(prefix, x, y, beam_z, coll):
    """Printed post on the pipette plate's arm carrying a slotted optical endstop laid flat (long
    side along y), its beam at beam_z; a pocket under the slot lets the flag carry on EJECT_MM past
    the beam. 2 M3 x 12 through counterbores into the plate, 2 M3 through the sensor's ears into the
    post (self-tapping)."""
    bl, bw, bt = OPT_BODY
    zs = beam_z - bt / 2                              # sensor underside = post top
    dy = L.SWITCH_POST_HOLE_DY
    h = box(prefix + "_post", (11, 2 * dy + 6, zs - P), (x, y, (P + zs) / 2), coll, M["pla"])
    bm = bmesh.new()
    _block(bm, x - 3.5, x + 3.5, y - 2.5, y + 2.5, zs - (EJECT_MM - bt / 2) - 1.5, zs + 1)   # flag pocket
    for s_ in (-1, 1):
        _cone(bm, L.M3 / 2, L.M3 / 2, P - 1, zs + 1, xy=(x, y + s_ * dy))
    boolean(h, bm)
    bm = bmesh.new()
    for s_ in (-1, 1):
        _cone(bm, 3.2, 3.2, P + 6, zs + 1, xy=(x, y + s_ * dy))                             # counterbores
        _cone(bm, 1.25, 1.25, zs - 8, zs + 1, xy=(x, y + s_ * OPT_EARS / 2))                # sensor screws
    boolean(h, bm)
    sen = box(prefix + "_sensor", (bw, bl, bt), (x, y, zs + bt / 2), coll, M["pla_grey"])
    bm = bmesh.new()                                  # the fork's slot, open toward the frame side
    xa, xb = sorted((x - (2.5 if x > 0 else -2.5), x + (bw if x > 0 else -bw)))
    _block(bm, xa, xb, y - OPT_SLOT / 2, y + OPT_SLOT / 2, zs - 1, zs + bt + 1)
    boolean(sen, bm)


def plunger_flag(name, x, y, coll):
    """Printed flag under the drive plate (build frame): a tab with 2 M3 into the plate (along y)
    and a 4 x 2 mm vane that reaches the optical beam at home."""
    zu = PLG_MID - T / 2                              # plate underside, build frame
    vane = OPT_BELOW + OPT_BODY[2] / 2                # plate underside to the beam at home
    o = box(name, (8, 2 * (L.FLAG_HOLE_DY + 4), 3), (x, y, zu - 1.5), coll, M["pla"])
    bm = bmesh.new()
    _block(bm, x - 2.0, x + 2.0, y - 1.0, y + 1.0, zu - vane, zu - 2.9)
    boolean(o, bm, 'UNION', self_intersect=True)
    bm = bmesh.new()
    for s_ in (-1, 1):
        _cone(bm, L.M3 / 2, L.M3 / 2, zu - 5, zu + 1, xy=(x, y + s_ * L.FLAG_HOLE_DY))
    boolean(o, bm)
    return o


def tip_ejector(coll):
    """Tip ejector, all in the cartridge: a 3 mm plate (tip_ejector_plate.dxf) under the barrel
    ends, on 4 M4 threaded rods that slide up through the carrier plate (and ride in the pipette
    plate's slot). A spring over each rod, between the carrier plate and a nut, holds the plate up
    against the barrel ends, where it is also the stop the tips seat against. Going below home,
    the plunger carrier meets the rod tops (the front pair EJ_GAP_F below home, the back
    pair EJ_GAP_B), so the plate tilts front first and pushes the tips off a few rows at a time."""
    z_top = SEAT - 58                                 # barrel ends = ejector plate top
    plate = fab_plate("tip_ejector_plate.dxf", "eject_plate", coll, (0, 0, z_top - T / 2))
    brk_bot = SWITCH_TOP + 0.5 - PC_BELOW             # plunger carrier underside at home
    z_col = EJ_SPRING_Z[1]                            # spring top / nut
    for x, y in L.EJ_ROD_HOLES:
        tag = f"{'LR'[x > 0]}{'FB'[y > 0]}"
        top = brk_bot - (EJ_GAP_B if y > 0 else EJ_GAP_F)
        bm = bmesh.new()
        _cone(bm, 2.0, 2.0, z_top - T - 5, top, seg=16, xy=(x, y))                   # M4 rod
        _cone(bm, 3.8, 3.8, z_top - T - 3.2, z_top - T, seg=6, xy=(x, y))            # nut under the plate
        _cone(bm, 3.8, 3.8, z_top, z_top + 3.2, seg=6, xy=(x, y))                    # nut on top
        _cone(bm, 3.8, 3.8, z_col, z_col + 3.2, seg=6, xy=(x, y))                    # spring nut
        new_obj(f"eject_rod_{tag}", bm, coll, M["chrome"])
        spring(f"eject_spring_{tag}", x, y, EJ_SPRING_Z[0], z_col, 3.2, 0.4, 7, coll, M["chrome"])
    return plate


def head_bracket(name, sx, coll):
    """Printed bracket joining the pipette plate to the side bar. An L profile (so it prints on
    its side with no overhang): the upper block sits under the plate edge (2 M4 up through the
    plate), the foot runs under the bar (2 M5 up into the bar's bottom slot)."""
    zt = P - T                                        # pipette plate underside = bar top
    x_in, x_bar, x_out = 69.5, IX, IX + 17.4          # inner face (outside the cartridge channel), bar, foot
    o = box(name, (x_bar - x_in, 60, 20), (sx * (x_in + x_bar) / 2, 0, zt - 10), coll, M["pla"])
    bm = bmesh.new()
    xa, xb = sorted((sx * (x_bar - 0.01), sx * x_out))
    _block(bm, xa, xb, -30, 30, zt - 26, zt - 20 + 0.01)
    boolean(o, bm, 'UNION')
    bm = bmesh.new()
    for x, y in L.HEAD_MOUNT_XY:
        if x * sx > 0:
            _cone(bm, L.M4 / 2, L.M4 / 2, zt - 30, zt + 5, xy=(x, y))
    for y in (-20.0, 20.0):
        _cone(bm, L.M5 / 2, L.M5 / 2, zt - 30, zt - 15, xy=(sx * (IX + 10), y))
    boolean(o, bm)
    return o


def lift_carriage_bracket(name, sx, sy, coll):
    """Printed block joining the lift plate to one rail plate. It sits on the plate, its outer
    face against the rail plate: 2 M4 from outside through the rail plate's own holes into
    captive nuts (slots from the top), 2 M4 down through the block and the plate (counterbored,
    nuts under the plate). Its inner face stays 2 mm outside the well plate's path."""
    zb, zt = LIFT0 + T, LIFT0 + T + BRK_H
    x_in, x_out = 66.0, IF_X - T / 2                  # inner face; outer face = rail plate
    y0, y1 = L.LIFT_BRACKET_Y[0] - 5, L.LIFT_BRACKET_Y[1] + 5
    o = box(name, (x_out - x_in, y1 - y0, BRK_H), (sx * (x_in + x_out) / 2, sy * (y0 + y1) / 2, (zb + zt) / 2),
            coll, M["pla"])
    bm = bmesh.new()                                  # two passes so no cutters overlap each other
    for y in LIFT_IF_HOLE_Y:                          # rail-plate bolts
        _bar(bm, (sx * (x_in - 1), sy * y, BRK_BOLT_Z), (sx * (x_out + 1), sy * y, BRK_BOLT_Z), L.M4 / 2)
    for y in L.LIFT_BRACKET_Y:                        # plate bolts
        _cone(bm, L.M4 / 2, L.M4 / 2, zb - 1, zt + 1, xy=(sx * L.LIFT_BRACKET_X, sy * y))
    boolean(o, bm)
    bm = bmesh.new()
    for y in LIFT_IF_HOLE_Y:                          # M4 nut slots (7 mm AF), open at the top
        xa, xb = sorted((sx * 73.0, sx * 76.5))
        _block(bm, xa, xb, sy * y - 3.7, sy * y + 3.7, BRK_BOLT_Z - 4.0, zt + 1)
    for y in L.LIFT_BRACKET_Y:                        # counterbores for the plate-bolt heads
        _cone(bm, 4.2, 4.2, zb + 8, zt + 1, xy=(sx * L.LIFT_BRACKET_X, sy * y))
    boolean(o, bm)
    return o


def plunger_carriage_bracket(name, sx, sy, coll):
    """Printed block hanging under a side edge of the drive plate, outside the cartridge's D-shaft
    trough (x > 67.5) and clear of the nut screws: 2 M4 through the plate (one into a captive nut in
    a pocket from below, one up from the pocket into a T-nut in the stiffener's long bar), and 2 M4
    from outside through the plunger rail plate into captive nuts in slots from below."""
    zt = PLG_MID - T / 2                              # plate underside
    zb, zr = zt - PLG_BRK_H, PLG_MID - L.PLG_BRACKET_ROW_BELOW_MID
    x_in, x_out = 67.5, IF_X - T / 2
    y0, y1 = 5.0, 50.0
    o = box(name, (x_out - x_in, y1 - y0, PLG_BRK_H), (sx * (x_in + x_out) / 2, sy * (y0 + y1) / 2, (zb + zt) / 2),
            coll, M["pla"])
    bm = bmesh.new()                                  # two passes so no cutters overlap each other
    for y in L.PLG_BRACKET_RAIL_Y:
        _bar(bm, (sx * (x_in - 1), sy * y, zr), (sx * (x_out + 1), sy * y, zr), L.M4 / 2)
    for x, y in L.PLG_BRACKET_PLATE_XY:
        _cone(bm, L.M4 / 2, L.M4 / 2, zb - 1, zt + 1, xy=(sx * x, sy * y))
    boolean(o, bm)
    bm = bmesh.new()
    for y in L.PLG_BRACKET_RAIL_Y:                    # rail-bolt nut slots (7 mm AF), open at the bottom
        xa, xb = sorted((sx * 75.5, sx * 79.0))
        _block(bm, xa, xb, sy * y - 3.7, sy * y + 3.7, zb - 1, zr + 4.0)
    for x, y in L.PLG_BRACKET_PLATE_XY:               # plate-bolt nut pockets from below
        _cone(bm, 4.2, 4.2, zb - 1, zt - 9.0, seg=6, xy=(sx * x, sy * y))
    boolean(o, bm)
    return o


def syringe_barrels(name, coll):
    """96 barrels with the finger tabs trimmed to stubs (see SYR_KEY_L / SYR_KEY_W): the flange's
    underside sits on the cartridge carrier plate, the barrel hangs through it and the grip."""
    bm = bmesh.new()
    r = SYR_BARREL_D / 2
    for x, y in g["GRID"]:
        t = bmesh.new()
        _cone(t, r, r, SEAT - 58, SEAT, seg=20, xy=(x, y))
        _block(t, x - SYR_KEY_L / 2, x + SYR_KEY_L / 2, y - SYR_KEY_W / 2, y + SYR_KEY_W / 2, SEAT, SEAT + SYR_FLANGE_T)
        for f in t.faces:
            f.material_index = 0
        n0 = len(t.faces)
        _cone(t, 1.5, 2.0, SEAT - 66, SEAT - 58, seg=20, xy=(x, y))   # Luer nozzle
        for f in list(t.faces)[n0:]:
            f.material_index = 1
        me = bpy.data.meshes.new("tmp")
        t.to_mesh(me)
        t.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    o = new_obj(name, bm, coll)
    o.data.materials.append(M["syr"])
    o.data.materials.append(M["white"])
    for f in o.data.polygons:
        f.use_smooth = False
    return o


def syringe_lock_frame(name, coll):
    """Printed frame that clamps the trimmed syringe flanges to the cartridge carrier plate
    (replaces the repo S-P retainer and the press fit). Its underside has one slot per row,
    SYR_KEY_W + 0.2 wide and 0.1 mm shallower than the flange, so the stubs can't turn and the
    frame presses every flange down; 5.2 mm holes pass the plunger rods and bear on each barrel's
    rim. 4 M3 through the frame and the carrier into the grip's ears clamp the three together; it
    passes through the pipette plate's drawer slot with 1.5 mm to spare."""
    z0, z1 = SEAT, SEAT + FRAME_T
    xs = [x for x, _ in g["GRID"]]
    ys = sorted({y for _, y in g["GRID"]})
    x_end = max(xs) + SYR_KEY_L / 2 + 0.3
    o = box(name, (2 * FRAME_HALF[0], 2 * FRAME_HALF[1], FRAME_T), (0, 0, (z0 + z1) / 2), coll, M["pla"])
    bm = bmesh.new()                                      # flange slots, one per row
    for y in ys:
        _block(bm, -x_end, x_end, y - SYR_KEY_W / 2 - 0.1, y + SYR_KEY_W / 2 + 0.1, z0 - 1, z0 + SYR_FLANGE_T - 0.1)
    boolean(o, bm)
    bm = bmesh.new()
    for x, y in g["GRID"]:                                # plunger rods
        _cone(bm, 2.6, 2.6, z0 - 1, z1 + 1, seg=16, xy=(x, y))
    for x, y in L.FRAME_SCREWS:                           # M3 into the grip's ears
        _cone(bm, L.M3 / 2, L.M3 / 2, z0 - 1, z1 + 1, xy=(x, y))
    boolean(o, bm)
    return o


def cartridge_grip(grip):
    """The repo grip, opened to a slip fit and hung from the carrier plate: 4 ears under the frame
    screws (FRAME_SCREWS) take M3 self-tappers, so it can't slide down the barrels."""
    drill(grip, g["GRID"], GRIP_SLIP_D / 2)
    grip.location.z -= T                              # under the carrier plate, not the pipette plate
    bpy.context.view_layer.update()
    zt = SEAT - T                                     # carrier underside
    bm = bmesh.new()
    for x, y in L.FRAME_SCREWS:
        xa, xb = sorted((x - 4.0, x + 4.0))
        ya, yb = (35.5, 40.8) if y > 0 else (-40.8, -35.5)       # clear of the outer barrels (34.7)
        _block(bm, xa, xb, ya, yb, zt - 10, zt)
    boolean(grip, bm, 'UNION', self_intersect=True)
    bm = bmesh.new()
    for x, y in L.FRAME_SCREWS:
        _cone(bm, 1.25, 1.25, zt - 9, zt + 1, xy=(x, y))
    boolean(grip, bm)
    grip.name = "syringe_grip_slipfit"
    return grip


def plunger_carrier(members):
    """The cartridge's plunger carrier (build frame, under the drive plate): 3 mm steel under the
    96 thumb pads, a printed retainer (pockets for the pads) over them, and the plungers. It slides
    in under the drive plate on the D-shaft clamps, which then press it up against the plate; it
    pushes the ejector rods."""
    zu = PLG_MID - T / 2                              # drive plate underside
    pc = dxf_part(os.path.join(FAB_DXF, "plunger_carrier.dxf"), "plunger_carrier", T, "Head", M["steel"])
    pc.location.z = zu - 3.0 - T / 2
    rt = box("pad_retainer", (2 * 55.7, 2 * 48.0, 3.0), (0, 0, zu - 1.5), "Head", M["pla"])
    bm = bmesh.new()
    for x, y in g["GRID"]:                            # pad pockets from below
        _cone(bm, 4.1, 4.1, zu - 4.0, zu - 1.5, seg=24, xy=(x, y))
    for x, y in L.RETAINER_SCREWS:                    # M3 countersunk, heads flush with the top
        _cone(bm, L.M3 / 2, L.M3 / 2, zu - 4.0, zu + 1.0, seg=24, xy=(x, y))
        _cone(bm, 1.6, 3.2, zu - 1.6, zu + 0.1, seg=24, xy=(x, y))   # starts inside the hole: no shared edge
    boolean(rt, bm, self_intersect=True)
    # plungers: stoppers where they were relative to the barrels
    bm = bmesh.new()
    for x, y in g["GRID"]:
        t = bmesh.new()
        _cone(t, 3.05, 3.05, SEAT - 30 - PLG_REST, SEAT - 24 - PLG_REST, seg=20, xy=(x, y))
        for f in t.faces:
            f.material_index = 1
        n0 = len(t.faces)
        _cone(t, 1.5, 1.5, SEAT - 24 - PLG_REST, zu - 3.0, seg=12, xy=(x, y))
        _cone(t, 3.9, 3.9, zu - 3.0, zu - 1.5, seg=20, xy=(x, y))
        for f in list(t.faces)[n0:]:
            f.material_index = 0
        me = bpy.data.meshes.new("tmp")
        t.to_mesh(me)
        t.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    pl = new_obj("plungers_x96", bm, "Syringes")
    pl.data.materials.append(M["plunger"])
    pl.data.materials.append(M["rubber"])
    members += [pc, rt, pl]


def dshaft_clamps(members):
    """Under the drive plate (build frame), each side: a printed trough bolted up to the plate,
    cradling an 8 mm D-shaft along y with a lever at the front. Flat up, the plunger carrier slides
    in over the shafts; a quarter turn puts the round side up and presses it against the plate,
    so the coupling has no play in either direction. Modeled clamped: flats facing outward, levers
    pointing inward-down (the quarter turn swings them to hang just outward of down and brings the
    flats up). Everything stays outside KEEP_X, where the outer plunger rods pass."""
    zu = PLG_MID - T / 2
    r = L.DSHAFT_D / 2
    zc = dshaft_axis_z()                              # shaft axis: its top meets the carrier's underside
    y0, y1 = -100.0, L.CART_SLOT_BACK
    for sx in (-1, 1):
        tag = "LR"[sx > 0]
        xa, xb = sorted((sx * KEEP_X, sx * 67.0))
        zb = zc - r - 3.0                                                     # 2.9 mm floor under the cradle
        tr = box(f"dshaft_trough_{tag}", (xb - xa, y1 - y0, zc - zb), ((xa + xb) / 2, (y0 + y1) / 2, (zb + zc) / 2),
                 "Head", M["pla"])
        bm = bmesh.new()
        wa, wb = sorted((sx * 60.5, sx * 67.0))
        _block(bm, wa, wb, y0, y1, zc - 0.01, zu)                            # outer wall up to the plate
        boolean(tr, bm, 'UNION', self_intersect=True)
        bm = bmesh.new()
        _bar(bm, (sx * L.DSHAFT_X, y0 - 1, zc), (sx * L.DSHAFT_X, y1 + 1, zc), r + 0.1, seg=32)   # the cradle
        for x, y in L.PS_XY:                                                  # T8 screw passes by
            if x * sx > 0 and y0 < y < y1:
                _cone(bm, 5.0, 5.0, zu - 20, zu + 1, xy=(x, y))
        for x, y in L.TROUGH_BOLTS:
            _cone(bm, L.M3 / 2, L.M3 / 2, zu - 20, zu + 1, xy=(sx * x, y))
        boolean(tr, bm)
        xc, yh0, yh1 = sx * L.DSHAFT_X, y0 - LEVER_HUB[1] - 6.0, y0 - 6.0      # lever hub, clear of the trough
        ym = (yh0 + yh1) / 2
        bm = bmesh.new()
        _bar(bm, (xc, yh0, zc), (xc, y1, zc), r, seg=48)
        sh = new_obj(f"dshaft_{tag}", bm, "Head", M["chrome"])
        bm = bmesh.new()                                                      # the flat, facing outward
        _block(bm, *sorted((xc + sx * (r - L.DSHAFT_FLAT), xc + sx * (r + 1))), yh0 - 1, y1 + 1, zc - r - 1, zc + r + 1)
        _bar(bm, (xc, ym, zc - r - 0.5), (xc, ym, zc - r + 1.5), 1.25, seg=16)   # set-screw dimple, underneath
        boolean(sh, bm)
        # lever. Open, the carrier slides out over the shaft's front end and the outer plunger rods pass
        # just inside it, so the hub only wraps the shaft where neither goes (~190 deg: trimmed flush
        # with the flat and at KEEP_X); an M3 set screw into the dimple drives it. The arm hangs
        # LEVER_OPEN_DEG outward of straight down when open, a quarter turn inward of that when clamped.
        bm = bmesh.new()
        _bar(bm, (xc, yh0, zc), (xc, yh1, zc), LEVER_HUB[0], seg=48)
        lv = new_obj(f"dshaft_lever_{tag}", bm, "Head", M["pla"])
        a = D(180 + LEVER_OPEN_DEG)                                           # arm direction, clamped
        u, n = Vector((sx * math.cos(a), 0, math.sin(a))), Vector((-sx * math.sin(a), 0, math.cos(a)))
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1)
        c = Vector((xc, ym, zc)) + u * (LEVER_ARM[0] / 2)
        bmesh.ops.transform(bm, verts=bm.verts, matrix=Matrix(((u.x * LEVER_ARM[0], 0, n.x * LEVER_ARM[1], c.x),
                            (0, yh1 - yh0, 0, c.y), (u.z * LEVER_ARM[0], 0, n.z * LEVER_ARM[1], c.z), (0, 0, 0, 1))))
        boolean(lv, bm, 'UNION', self_intersect=True)
        e = LEVER_HUB[0] + 2
        keep = L.DSHAFT_X - KEEP_X                                            # open, this side faces the rods
        bm = bmesh.new()
        _block(bm, *sorted((xc + sx * (r - L.DSHAFT_FLAT - 0.2), xc + sx * e)), yh0 - 1, yh1 + 1, zc - e, zc + e)   # flat side
        _block(bm, xc - e, xc + e, yh0 - 1, yh1 + 1, zc + keep, zc + e)       # rod side
        _bar(bm, (xc, yh0 - 1, zc), (xc, yh1 + 1, zc), r + 0.15, seg=48)      # bore
        _bar(bm, (xc, ym, zc - e), (xc, ym, zc - r + 0.5), 1.25, seg=16)      # M3 set screw, tapped
        boolean(lv, bm, self_intersect=True)
        for o in (sh, lv):                                                    # origin on the axis: the lever turns in place
            d = Vector((xc, 0.0, zc)) - o.location
            o.data.transform(Matrix.Translation(-d))
            o.location += d
        members += [tr, sh, lv]


def dshaft_axis_z():
    return PLG_MID - T / 2 - 2 * T - L.DSHAFT_D / 2


def dshaft_drop(turn):
    """How far the carrier sinks with the levers `turn` of the way open: it rests on the shaft tops,
    and the flat (normal from facing outward to facing up) only reaches the top in the last ~37 deg."""
    r, fd = L.DSHAFT_D / 2, L.DSHAFT_FLAT
    a, b = D(90) * (1 - turn), math.acos((r - fd) / r)
    return 0.0 if a >= b else r - r * math.cos(b - a)


def drawer_channels():
    """Under the pipette plate's arms, each side: a steel ledge (cart_ledge.dxf) on a printed spacer,
    CART_GAP below the arm; the cartridge plate's edge runs between them. The spacer turns in at the
    back as the stop, and a spring plunger in the ledge clicks into the plate's detent hole."""
    zt = SEAT                                         # pipette plate underside
    for sx in (-1, 1):
        tag = "LR"[sx > 0]
        ld = fab_plate("cart_ledge.dxf", f"cart_ledge_{tag}", "Head", (0, 0, zt - L.CART_GAP - T / 2))
        if sx < 0:
            ld.scale.x = -1
        xa, xb = sorted((sx * 63.3, sx * L.LEDGE_X[1]))
        sp = box(f"cart_spacer_{tag}", (xb - xa, L.CART_SLOT_BACK + 100, L.CART_GAP),
                 ((xa + xb) / 2, (L.CART_SLOT_BACK - 100) / 2, zt - L.CART_GAP / 2), "Head", M["pla"])
        bm = bmesh.new()
        ta, tb = sorted((sx * 56.5, sx * 63.31))
        _block(bm, ta, tb, L.CART_SLOT_BACK + 0.3, L.CART_SLOT_BACK + 6, zt - L.CART_GAP, zt)   # back stop
        boolean(sp, bm, 'UNION', self_intersect=True)
        bm = bmesh.new()
        for x, y in L.LEDGE_BOLTS:
            _cone(bm, L.M3 / 2, L.M3 / 2, zt - 5, zt + 1, xy=(sx * x, y))
        boolean(sp, bm)
        for x, y in L.CART_DETENTS:
            if x * sx > 0:
                cyl(f"cart_detent_{tag}", 3.0, 10.0, (x, y, zt - L.CART_GAP - 5.0), "Head", M["chrome"])


def cartridge_handle(coll):
    """Printed handle under the front of the cartridge plate (2 M3 self-tappers down through the
    plate); a finger slot to pull the drawer out."""
    zt = SEAT - T
    y1 = -L.CART_PLATE[1] + 6.0
    h = box("cartridge_handle", (50, 21, CART_HANDLE_H), (0, y1 - 10.5, zt - CART_HANDLE_H / 2), coll, M["pla"])
    bm = bmesh.new()
    _block(bm, -18, 18, y1 - 21 - 1, y1 - 12, zt - CART_HANDLE_H - 1, zt - 4)          # finger slot
    for x, y in L.CART_HANDLE_SCREWS:
        _cone(bm, 1.25, 1.25, zt - 9, zt + 1, xy=(x, y))
    boolean(h, bm)


def well_plate_nest(name, z0, coll):
    """Printed nest that locates the well plate on the lift platform (replaces the flat repo tray).
    A TRAY_H base keeps the plate at the height the firmware expects; walls 4 mm above it on the
    back and sides and a 2 mm lip at the front hold the SBS footprint with 0.4 mm clearance (lift the
    plate over the lip to load it). The side walls stop short of the carriage brackets and leave a
    gap for the lift nut bodies. 4 M4 down
    through counterbores into the lift plate, nuts underneath."""
    hx, hy = 63.9 + 0.4, 42.7 + 0.4
    o = box(name, (2 * hx, 2 * hy, TRAY_H), (0, 0, z0 + TRAY_H / 2), coll, M["pla"])
    bm = bmesh.new()
    _block(bm, -hx, hx, hy - 0.5, hy + 3, z0, z0 + TRAY_H + 4)              # back wall
    _block(bm, -40, 40, -hy - 3, -hy + 0.5, z0, z0 + TRAY_H + 2)            # front lip
    for s_ in (-1, 1):                                  # side walls, split around the lift nut bodies
        xa, xb = sorted((s_ * (hx - 0.5), s_ * (hx + 1.6)))
        for ya, yb in ((-30, -7), (7, 30)):
            _block(bm, xa, xb, ya, yb, z0, z0 + TRAY_H + 4)
    boolean(o, bm, 'UNION', self_intersect=True)
    bm = bmesh.new()
    for x, y in L.NEST_HOLES:
        _cone(bm, L.M4 / 2, L.M4 / 2, z0 - 1, z0 + TRAY_H + 1, xy=(x, y))
    boolean(o, bm)
    bm = bmesh.new()
    for x, y in L.NEST_HOLES:
        _cone(bm, 4.2, 4.2, z0 + 6, z0 + TRAY_H + 1, xy=(x, y))
    boolean(o, bm)
    return o


def close_control_box(h):
    """The repo housing hung on the frame with its open back against the posts and its lid set
    between them; laid on the bench here, its walls stop short of the lid and its side bays have
    no floor. So: a 3 mm skirt runs every wall down to the bench, the lid's four screw bosses are
    extended down to a new full-size base plate, and a pad on the back wall carries 2 M5 into
    T-nuts in the bottom front bar."""
    vs = [h.matrix_world @ v.co for v in h.data.vertices]
    x1 = max(v.x for v in vs)
    y0, y1 = min(v.y for v in vs), max(v.y for v in vs)
    w = 3.0
    bm = bmesh.new()                                  # skirt ring (4 non-overlapping sides)
    _block(bm, -x1, x1, y0, y0 + w, 0, 16)
    _block(bm, -x1, x1, y1 - w, y1, 0, 16)
    for s_ in (-1, 1):
        xa, xb = sorted((s_ * x1, s_ * (x1 - w)))
        _block(bm, xa, xb, y0 + w + 0.01, y1 - w - 0.01, 0, 16)
    boolean(h, bm, 'UNION', self_intersect=True)
    bm = bmesh.new()
    for x, y in CBOX_BOSSES:                          # lid bosses down to the base plate
        _cone(bm, 3.5, 3.5, 3, 15.5, xy=(x, y))
    boolean(h, bm, 'UNION', self_intersect=True)
    bm = bmesh.new()                                  # frame pad
    _block(bm, -40, 40, y1 - 0.5, -g["FY"] / 2 - 0.2, 2, 18)
    boolean(h, bm, 'UNION', self_intersect=True)
    bm = bmesh.new()
    for x, y in CBOX_BOSSES:                          # pilot holes for M3 self-tappers (2.4: just
        _cone(bm, 1.2, 1.2, -1, 30, xy=(x, y))       # inside the repo boss's 2.5 hole, no shared wall)
    for x in (-25.0, 25.0):                           # M5 into the bar's front slot (z 10)
        _bar(bm, (x, y1 - 12, 10), (x, -g["FY"] / 2 + 1, 10), L.M5 / 2)
    boolean(h, bm)
    bm = bmesh.new()                                  # panel-mount USB-B socket, left end wall
    uy, uz = USB_PANEL_YZ
    cw, ch = USB_PANEL_CUT
    _block(bm, -x1 - 5, -x1 + w + 5, uy - cw / 2, uy + cw / 2, uz - ch / 2, uz + ch / 2)
    for s_ in (-1, 1):
        _bar(bm, (-x1 - 5, uy + s_ * USB_PANEL_EARS / 2, uz), (-x1 + w + 5, uy + s_ * USB_PANEL_EARS / 2, uz), L.M3 / 2)
    boolean(h, bm)
    coll = h.users_collection[0].name
    box("usb_panel_socket_flange", (1.5, USB_PANEL_EARS + 8, ch + 3), (-x1 - 0.75, uy, uz), coll, M["pla_grey"])
    box("usb_panel_socket_body", (18, cw - 0.4, ch - 0.4), (-x1 + w + 9, uy, uz), coll, M["pla_grey"])
    base = box("control_box_base", (2 * (x1 - w - 0.3), (y1 - y0) - 2 * (w + 0.3), 3),
               (0, (y0 + y1) / 2, 1.5), h.users_collection[0].name, M["pla"])
    bm = bmesh.new()
    for x, y in CBOX_BOSSES:                          # countersunk M3
        _cone(bm, 1.7, 1.7, -1, 4, xy=(x, y))
    boolean(base, bm)
    bm = bmesh.new()
    for x, y in CBOX_BOSSES:
        _cone(bm, 3.4, 1.7, -0.01, 1.7, xy=(x, y))
    boolean(base, bm)
    return base


def fab_plate(fname, obj_name, coll, loc):
    """A laser-cut plate from the generated DXFs (01_Hardware/MotorLift/ToLaserCut-DXF)."""
    o = dxf_part(os.path.join(FAB_DXF, fname), obj_name, T, coll, M["steel"])
    o.location = loc
    return o


def replace_mesh(obj, fname):
    """Swap a baseline plate's mesh for the generated DXF (same drawing frame, same transform)."""
    tmp = dxf_part(os.path.join(FAB_DXF, fname), obj.name + "_new", T, obj.users_collection[0].name, M["steel"])
    old = obj.data
    obj.data = tmp.data
    bpy.data.objects.remove(tmp)
    bpy.data.meshes.remove(old)


def drill(obj, holes, r):
    """Boolean-cut vertical through-holes (world x, y) into obj, baked into its mesh."""
    bm = bmesh.new()
    for x, y in holes:
        _cone(bm, r, r, -500, 500, seg=32, xy=(x, y))
    cut = new_obj(obj.name + "_cut", bm, obj.users_collection[0].name)
    mod = obj.modifiers.new("holes", 'BOOLEAN')
    mod.object, mod.operation, mod.solver = cut, 'DIFFERENCE', 'EXACT'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    baked = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    obj.modifiers.clear()
    mats = list(obj.data.materials)
    obj.data = baked
    if not obj.data.materials:
        for m in mats:
            obj.data.materials.append(m)
    bpy.data.objects.remove(cut)


def rig_empty(name, coll, members):
    e = bpy.data.objects.new(name, None)
    bpy.data.collections[coll].objects.link(e)
    e.empty_display_type, e.empty_display_size = 'ARROWS', 30
    bpy.context.view_layer.update()
    for k in members:
        mw = k.matrix_world.copy()
        k.parent = e
        k.matrix_parent_inverse = Matrix.Identity(4)
        k.matrix_basis = mw
    return e


def _find_front_cutout(h, y_front, zu):
    """Bounds (x0, x1, z0, z1) of the opening in the housing's front wall below the panel,
    found by shooting rays through the wall on a 0.5 mm grid."""
    dg = bpy.context.evaluated_depsgraph_get()
    he = h.evaluated_get(dg)
    inv = h.matrix_world.inverted()
    d = (inv.to_3x3() @ Vector((0, 1, 0))).normalized()
    pts = []
    for i in range(-200, 201):
        for k in range(int((zu - 30) * 2), int(zu * 2)):
            x, z = i * 0.5, k * 0.5
            ok, loc, _, _ = he.ray_cast(inv @ Vector((x, y_front - 5, z)), d)
            if not ok or (h.matrix_world @ loc).y > y_front + 3.5:     # passed the wall
                pts.append((x, z))
    if not pts:
        return None
    return (min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts))


def slope_control_box(theta, parts):
    """Tilt the control box's screen panel toward the user by theta, lowering the front edge.

    The panel, and everything hanging within 8 mm under it (LCD, encoder and Arduino standoffs,
    ribs), rotates as one rigid piece about the box's back top edge, so the boards keep their
    mounting. The walls are trimmed to meet it, the panel is extended to close the gap it leaves
    at the front, and the front-wall cutout (the Arduino's USB port) is filled: laid down, that
    wall faces the user, so USB moves to the left end (see close_control_box). The screen, bezel
    and knob tilt with the panel."""
    obj = bpy.data.objects
    h = obj["ScreenHousing"]
    bpy.context.view_layer.update()
    h.data.transform(h.matrix_world)                 # work in world coordinates
    h.matrix_world = Matrix.Identity(4)
    vs = [v.co for v in h.data.vertices]
    x0, x1 = min(v.x for v in vs), max(v.x for v in vs)
    y_front, y_back = min(v.y for v in vs), max(v.y for v in vs)
    zt = max(v.z for v in vs)
    wall = T                                          # 3 mm shell (measured)
    zu, zf = zt - wall, zt - wall - 7.5               # panel underside; depth of panel-mounted features
    pivot = Vector((0, y_back, zt))
    R = Matrix.Translation(pivot) @ Matrix.Rotation(theta, 4, 'X') @ Matrix.Translation(-pivot)
    cut = _find_front_cutout(h, y_front, zu)

    def block(*b, rot=False):
        bm = bmesh.new()
        _block(bm, *b)
        if rot:
            bm.transform(R)
        return bm

    big = (x0 - 50, x1 + 50)
    # The panel piece is cut out in ONE intersection with a T-shaped tool: a full-width slab
    # (panel + wall rims) over a box that reaches 0.5 mm into the walls (standoffs, ribs, bosses).
    # Gluing separately cut pieces together instead leaves self-intersections that the exact
    # solver later turns into non-manifold slivers.
    tool = new_obj("ScreenHousing_Ttool", block(*big, y_front - 50, y_back + 50, zu, zt + 50), h.users_collection[0].name)
    boolean(tool, block(x0 + wall - 0.5, x1 - wall + 0.5, y_front + wall - 0.5, y_back - wall + 0.5, zf, zu + 0.5), 'UNION')
    pnl = h.copy()
    pnl.data = h.data.copy()
    pnl.name = "ScreenHousing_panel"
    h.users_collection[0].objects.link(pnl)
    boolean(pnl, _mesh_bm(tool), 'INTERSECT')
    pnl.data.transform(R)
    # walls = the rest, with the old port cutout filled
    boolean(h, _mesh_bm(tool))
    obj.remove(tool)
    if cut:
        cx0, cx1, cz0, cz1 = cut
        boolean(h, block(cx0 - 1, cx1 + 1, y_front, y_front + wall, cz0 - 1, min(cz1 + 1, zu)), 'UNION')
    # trim to the slope: side and back walls run 1 mm up into the tilted panel; the front wall runs
    # up to the panel's top surface, which fills the ~1.5 mm the tilted panel falls short at the front
    strip = y_front + wall + 2
    boolean(h, block(*big, strip, y_back + 50, zu + 1.0, zu + 300, rot=True))
    boolean(h, block(*big, y_front - 400, strip + 1, zt, zt + 300, rot=True))   # overlap: no sliver at the seam
    # The panel's wall rims share their outer faces with the walls below, which the exact solver
    # only merges in self-intersection mode. export_motor_lift_parts.py refuses to write the part
    # if the result has any open edges.
    boolean(h, _mesh_bm(pnl), 'UNION', self_intersect=True)
    obj.remove(pnl)
    for o in parts[2:]:                               # bezel, screen, knob ride on the panel
        o.matrix_world = R @ o.matrix_world
    return cut


def _mesh_bm(o):
    """A bmesh of o's mesh in world coordinates (for use as a boolean tool)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.transform(o.matrix_world)
    return bm


# ================================================================ modify baseline
def modify():
    global M
    M = g["materials"]()
    obj = bpy.data.objects
    lever = ("bearing_", "bearing_plate", "bearing_insert", "square_shaft", "lever_", "linkage")
    drop = [o.name for o in obj if o.name.startswith(lever + ("NEMA17_", "T8_", "MGN9H_rail_"))]
    drop += ["bed_left", "bed_right", "ext_bed_F", "ext_bed_B"]
    for n in drop:
        if n in obj:
            obj.remove(obj[n])

    # rails: full height for the lift + plunger carriages
    r0, r1 = BASE_Z - 7, FH - 25
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(f"MGN9H_rail_{'LR'[sx > 0]}{'FB'[sy > 0]}", (6.5, 9, r1 - r0),
                (sx * (IX - 3.25), sy * PY, (r0 + r1) / 2), "Frame", M["chrome"], bevel=0.3)
    # pipette plate fixed to the frame: a 2020 bar along each side at plate height, joined to
    # the plate by printed brackets (replaces the lower rail carriages and interface plates)
    for o in [o for o in obj if o.name.startswith(("MGN9H_carriage_low", "interface_plate_low"))]:
        obj.remove(o)
    for sx in (-1, 1):
        g["tslot_bar"](f"ext_head_{'LR'[sx > 0]}", g["FY"] - 40, (sx * g["PX"], 0, P - T - 10), 'Y', "Frame", M["ext"])
        head_bracket(f"head_bracket_{'LR'[sx > 0]}", sx, "Head")
    # syringes: tab stubs keyed under a locking frame instead of cut-off ends hammered into the grip
    # (the grip stays as a slip-fit guide for the barrels' lower ends)
    for n in ("syringe_barrels_x96", "S-P_plate"):
        obj.remove(obj[n])
    fab_plate("cartridge_plate.dxf", "cartridge_plate", "Head", (0, 0, SEAT - T / 2))
    cartridge_handle("Head")
    drawer_channels()
    syringe_barrels("syringe_barrels_x96", "Syringes")
    syringe_lock_frame("syringe_lock_frame", "Head")
    cartridge_grip(obj["syringe_grip_static"])
    obj["pipette_tips_x96"].location.z -= TIP_DROP
    tip_ejector("Head")
    # plunger home sensors: the repo corner blocks stood on their sides unbolted; printed posts
    # bolted to the pipette plate's arms carry three slotted optical endstops (the firmware homes on
    # the first and checks the other two). Optical, because the plunger goes on past home to eject tips.
    for o in [o for o in obj if o.name.startswith(("LimitSwitch_holder_B", "limit_switch_"))]:
        obj.remove(o)
    for x, y in L.SWITCH_POSTS:
        optical_post(f"plunger_optical_{'LR'[x > 0]}{'FB'[y > 0]}", x, y, SWITCH_TOP + 0.5 - OPT_BELOW - OPT_BODY[2] / 2, "Head")

    # ---------------- LIFT
    fab_plate("lift_base_plate.dxf", "lift_base_plate", "Frame", (0, 0, BASE_Z + T / 2))
    nema17("lift_motor", *LIFT_MOTOR_XY, BASE_Z, True, "Bed")
    obj["lift_motor_shaft"].location.z = BASE_Z + 9
    for sx in (-1, 1):
        tag = "LR"[sx > 0]
        kfl08(f"KFL08_lift_{tag}", sx * LIFT_X, 0, BASE_Z, True, "Bed")
        cyl(f"lift_screw_{tag}", 4, 118, (sx * LIFT_X, 0, BASE_Z - 14 + 59), "Bed", M["chrome"], seg=16)
        pulley(f"lift_pulley_{tag}", sx * LIFT_X, 0, LIFT_PLUS, "Bed")
    pulley("lift_pulley_motor", *LIFT_MOTOR_XY, LIFT_PLUS, "Bed")
    # tensioner: idler pushes the long lower run (between the screws) inward (+y)
    li_y = L.LIFT_IDLER_Y
    idler("lift_idler", 0, li_y, LIFT_PLUS, "Bed")
    tensioner("lift_tensioner", 0, li_y, BASE_Z + T, LIFT_PLUS + 6 - (BASE_Z + T) - 0.5, "Bed")
    lift_seq = [(-LIFT_X, 0, PULLEY_R), (0, li_y, -IDLER_R), (LIFT_X, 0, PULLEY_R), (*LIFT_MOTOR_XY, PULLEY_R)]
    lift_belt = belt("lift_belt", lift_seq, LIFT_PLUS + 11, "Bed")
    # homing: the platform underside presses the lever at the bottom of travel
    microswitch("lift_home_switch", *HOME_SW_XY, BASE_Z + T, LIFT0 + HOME_OVERTRAVEL, "Bed")

    # platform (+ carriages, interface plates, nuts, tray, plate)
    lp = fab_plate("lift_plate.dxf", "lift_plate", "Bed", (0, 0, LIFT0 + T / 2))
    members = [lp]
    for sx in (-1, 1):
        for sy in (-1, 1):
            members.append(lift_carriage_bracket(f"lift_carriage_bracket_{'LR'[sx > 0]}{'FB'[sy > 0]}", sx, sy, "Bed"))
    src = dxf_part("interface_plate_high.DXF", "lift_interface", T, "Bed", M["steel"])
    zc = BRK_BOLT_Z - 10                              # DXF hole row y = 10 lands on the bracket bolts
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        o = src if i == 0 else dup(src, f"lift_interface.{i:03d}")
        g["frame_to"](o, -sy * Vector((0, 1, 0)), Vector((0, 0, 1)), (-10, 0), (sx * IF_X, sy * PY, zc))
        members += [o, box(f"MGN9H_carriage_lift_{'LR'[sx > 0]}{'FB'[sy > 0]}", (6.5, 20, 39.9),
                           (sx * (IX - 6.75), sy * PY, zc + 4), "Frame", M["chrome"], bevel=0.5)]
    for sx in (-1, 1):
        tag = "LR"[sx > 0]
        members.append(cyl(f"lift_nut_flange_{tag}", 11, 3.5, (sx * LIFT_X, 0, LIFT0 - 1.75), "Bed", M["brass"]))
        members.append(cyl(f"lift_nut_body_{tag}", 5.1, 15, (sx * LIFT_X, 0, LIFT0 + 7.5), "Bed", M["brass"]))
    obj.remove(obj["vertical_tray"])
    tray, wp = well_plate_nest("well_plate_nest", LIFT0 + T, "Bed"), obj["well_plate_96"]
    wp.location.z = LIFT0 + T + TRAY_H + PLATE_H / 2
    members += [tray, wp]
    rig_empty("lift_platform", "Bed", members)

    # ---------------- PLUNGER drive on the top plate: the pipette plate is a U open at the front for
    # the cartridge drawer, so the screws hang from KFL08s on a plate across the top ring, with their
    # pulleys, the belt and the idler under it (inside the ring) and the motor standing on it.
    pip, plg = obj["pipette_plate"], obj["plunger_plate"]
    replace_mesh(pip, "pipette_plate_motorlift.dxf")
    replace_mesh(plg, "plunger_plate_motorlift.dxf")   # the drive plate: the thumb pads are the cartridge's
    obj.remove(obj["plunger_holder_plate"])
    fab_plate("top_plate.dxf", "top_plate", "Frame", (0, 0, FH + T / 2))
    z_top = FH + T
    s_lo, s_hi = 286.0, z_top + 14.0                  # screw: below the nut at full eject, up through the KFL08
    for i, (x, y) in enumerate(PS_XY, 1):
        kfl08(f"KFL08_plunger_{i}", x, y, z_top, False, "Motors", rot=D(90))
        cyl(f"plunger_screw_{i}", 4, s_hi - s_lo, (x, y, (s_lo + s_hi) / 2), "Motors", M["chrome"], seg=16)
        pulley(f"plunger_pulley_{i}", x, y, TOP_PZ0, "Motors")
    nema17("plunger_motor", *PLG_MOTOR_XY, z_top, False, "Motors", length=48.0)
    pulley("plunger_pulley_motor", *PLG_MOTOR_XY, TOP_PZ0, "Motors")
    # tensioner: idler pushes the front run inward (+y); its bolt goes up through the plate's slot
    pi_y = L.PLG_IDLER_Y
    idler("plunger_idler", 0, pi_y, TOP_PZ0, "Motors")
    obj.remove(obj["plunger_idler_bolt"])
    cyl("plunger_idler_bolt", 2.5, z_top + 5.5 - (TOP_PZ0 + 4), (0, pi_y, (z_top + 5.5 + TOP_PZ0 + 4) / 2), "Motors", M["motor"])
    cyl("plunger_idler_bolt_head", 4.0, 3.0, (0, pi_y, z_top + 5.5 + 1.5), "Motors", M["motor"])
    tensioner("plunger_tensioner", 0, pi_y, z_top, 5.5, "Motors")
    lf, rf, lb, rb = PS_XY          # PS_XY order: LF, RF, LB, RB
    plg_seq = [(*lf, PULLEY_R), (0, pi_y, -IDLER_R), (*rf, PULLEY_R), (*rb, PULLEY_R),
               (*PLG_MOTOR_XY, PULLEY_R), (*lb, PULLEY_R)]   # motor on the back run, idler on the front
    plg_belt = belt("plunger_belt", plg_seq, TOP_PZ0 + 10, "Motors")

    # moving plunger carriage: plate, holder, plungers, carriage brackets, rail plates, carriages,
    # nuts, stiffener. The repo's LimitSwitch_holder_A blocks carry no switch here and joined
    # nothing, so they go; the rail plates become the taller plunger_rail_plate.dxf.
    for o in [o for o in obj if o.name.startswith("LimitSwitch_holder_A")]:
        bpy.data.objects.remove(o)
    rails = [o for o in obj if o.name.startswith("interface_plate_high")]
    tmp = dxf_part(os.path.join(FAB_DXF, "plunger_rail_plate.dxf"), "plunger_rail_plate", T, "Head", M["steel"])
    for o in rails:
        o.data = tmp.data
    bpy.data.objects.remove(tmp)
    obj.remove(obj["plungers_x96"])
    members = [plg] + rails
    plunger_carrier(members)
    dshaft_clamps(members)
    members += [plunger_flag(f"plunger_flag_{'LR'[x > 0]}{'FB'[y > 0]}", x, y, "Head") for x, y in L.SWITCH_POSTS]
    members += [o for o in obj if o.name.startswith("MGN9H_carriage_high")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            members.append(plunger_carriage_bracket(f"plunger_carriage_bracket_{'LR'[sx > 0]}{'FB'[sy > 0]}", sx, sy, "Head"))
    zh = PLG_TOP
    for i, (x, y) in enumerate(PS_XY, 1):
        # anti-backlash T8 nut, flange down on the drive plate (4 M3 through it), body up; preload
        # spring and second nut above it
        members.append(cyl(f"plunger_nut_flange_{i}", 11, 3.5, (x, y, zh + 1.75), "Motors", M["brass"]))
        members.append(cyl(f"plunger_nut_body_{i}", 5.1, 12, (x, y, zh + 9.5), "Motors", M["brass"]))
        members.append(spring(f"plunger_nut_spring_{i}", x, y, zh + 15.5, zh + 23.5, 6.0, 0.6, 4, "Motors", M["chrome"]))
        members.append(cyl(f"plunger_nut_upper_{i}", 7.0, 10, (x, y, zh + 28.5), "Motors", M["brass"], seg=6))
    # 2020 stiffening frame on the drive plate, over the syringe array and inside the nuts: two
    # bars along x carry the load toward the screw rows (the carriage-bracket bolts at (+/-72, +/-33)
    # come up into M4 T-nuts in them), two short bars close the frame (inside corner brackets).
    zf = zh + 10
    ly, sxx = L.STIFF_LONG_Y, L.STIFF_SHORT_X
    for sy in (-1, 1):
        members.append(g["tslot_bar"](f"plunger_stiffener_{'FB'[sy > 0]}", 150, (0, sy * ly, zf), 'X', "Head", M["ext"]))
    for sx in (-1, 1):
        members.append(g["tslot_bar"](f"plunger_stiffener_{'LR'[sx > 0]}", 2 * (ly - 10), (sx * sxx, 0, zf), 'Y', "Head", M["ext"]))
    rig_empty("plunger_carriage", "Head", members)

    # ---------------- control box: laid down in front of the base, screen and knob facing up,
    # base plate on the bench. At 72 mm tall it stays below the lowered tray (96 mm), so well plates
    # still slide in from the front; two M5 through a pad on its back wall into the bottom front bar.
    parts = [obj[n] for n in ("ScreenHousing", "electronics_lid", "LCD_2004_bezel", "LCD_2004_screen", "encoder_knob")]
    bpy.context.view_layer.update()
    R = Matrix.Rotation(D(-90), 4, 'X')               # screen normal -y -> +z, box top -> toward the frame
    for o in parts:
        o.matrix_world = R @ o.matrix_world
    bpy.context.view_layer.update()
    pts = [o.matrix_world @ Vector(c) for o in parts for c in o.bound_box]
    back = -(g["FY"] / 2 + T + CBOX_BACK_GAP)         # just clear of the corner brackets' bolt heads
    shift = Vector((-(min(p.x for p in pts) + max(p.x for p in pts)) / 2,
                    back - max(p.y for p in pts), -min(p.z for p in pts)))
    for o in parts:
        o.matrix_world = Matrix.Translation(shift) @ o.matrix_world
    slope_control_box(D(CONTROL_SLOPE_DEG), parts)
    obj.remove(obj["electronics_lid"])
    close_control_box(obj["ScreenHousing"])

    def span(seq, idx, sign):         # belt length with the idler at each end of its slot
        out = []
        for take in (TENSION_TAKEUP - 6, TENSION_TAKEUP + 6):
            q = list(seq)
            cx, cy, r = q[idx]
            q[idx] = (cx, cy + sign * (take - TENSION_TAKEUP), r)
            out.append(round(belt_route(q)[1], 1))
        return out
    return {"lift_belt_mm": round(lift_belt, 1), "plunger_belt_mm": round(plg_belt, 1),
            "lift_belt_range": span(lift_seq, 1, +1), "plunger_belt_range": span(plg_seq, 1, +1)}


# ================================================================ motion
def spinners():
    obj = bpy.data.objects
    lift = [o for o in obj if o.name.startswith(("lift_screw_", "lift_pulley_"))]
    plg = [o for o in obj if o.name.startswith(("plunger_screw_", "plunger_pulley_"))]
    return lift, plg


def pose(lift_mm, plg_mm):
    """plg_mm < 0 goes below home: the tip ejector follows (see tip_ejector)."""
    obj = bpy.data.objects
    obj["lift_platform"].location.z = lift_mm
    obj["plunger_carriage"].location.z = PLG_REST + plg_mm
    e = max(0.0, -plg_mm)
    df, db = max(0.0, e - EJ_GAP_F), max(0.0, e - EJ_GAP_B)
    z0, z1 = EJ_SPRING_Z                                 # springs: carrier plate to the spring nut
    for o in obj:
        d = db if o.name.endswith("B") else df
        if o.name.startswith("eject_rod_"):
            o.location.z = -d
        elif o.name.startswith("eject_spring_"):          # compress with the rod, bottom fixed
            k = (z1 - d - z0) / (z1 - z0)
            o.scale.z, o.location.z = k, z0 * (1 - k)
    ep = obj["eject_plate"]
    ep.location.z = SEAT - 58 - T / 2 - (df + db) / 2
    ep.rotation_euler.x = math.atan2(df - db, 2 * L.EJ_ROD_Y)
    lift, plg = spinners()
    for o in lift:
        o.rotation_euler.z = D(360) * lift_mm / LIFT_LEAD
    for o in plg:
        o.rotation_euler.z = D(360) * (PLG_REST + plg_mm) / PLG_LEAD


# (frame, lift mm, plunger mm): raise -> aspirate -> lower -> raise -> dispense -> lower
KEYS = [(1, 0, 0), (28, 1, 0), (34, 1, 0), (58, 1, 1), (64, 1, 1), (90, 0, 1), (100, 0, 1),
        (126, 1, 1), (132, 1, 1), (156, 1, 0), (162, 1, 0), (188, 0, 0), (196, 0, 0)]
EJ_A = -EJECT_MM / ASPIRATE       # plunger fraction for the eject pose
KEYS += [(220, 0, EJ_A), (228, 0, EJ_A), (252, 0, 0), (260, 0, 0)]


def animate():
    sc = bpy.context.scene
    lift, plg = spinners()
    movers = [bpy.data.objects["lift_platform"], bpy.data.objects["plunger_carriage"]] + lift + plg
    movers += [o for o in bpy.data.objects if o.name.startswith(("eject_rod_", "eject_plate"))]
    for o in movers:
        o.animation_data_clear()
    for f, l, a in KEYS:
        pose(l * LIFT_TRAVEL, a * ASPIRATE)
        for o in movers:
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("rotation_euler", frame=f)
    sc.frame_start, sc.frame_end, sc.render.fps = 1, KEYS[-1][0], 24
    sc.frame_set(1)


# Cartridge swap, after the cycle (plunger home, bed down): levers a quarter turn open, drawer out
# DRAWER_OUT (its back edge well clear of the front posts), back in, levers closed.
# (frame, lever turn 0..1, drawer out 0..1)
DRAWER_OUT = 210.0
DRAWER_KEYS = [(270, 0, 0), (294, 1, 0), (306, 1, 0), (366, 1, 1), (390, 1, 1), (450, 1, 0), (462, 1, 0),
               (486, 0, 0), (498, 0, 0)]


def drawer_parts():
    obj = bpy.data.objects
    cart = [o for o in obj if o.type == 'MESH' and o.name.startswith(CARTRIDGE + ("pipette_tips",))]
    levers = [obj[f"dshaft_{p}{t}"] for t in "LR" for p in ("", "lever_")]
    return cart, levers


CARRIER = ("plunger_carrier", "pad_retainer", "plungers_x96")   # ride on the D-shafts: sink when they open


def pose_drawer(turn, out):
    """turn 1 = D-shafts a quarter turn open, levers swung out level, carrier sunk onto the flats;
    out 1 = drawer DRAWER_OUT forward. Uses delta transforms, so it stacks on pose()."""
    cart, levers = drawer_parts()
    for o in cart:
        o.delta_location.y = -out * DRAWER_OUT
        o.delta_location.z = -dshaft_drop(turn) if o.name.startswith(CARRIER) else 0.0
    for o in levers:
        o.delta_rotation_euler.y = (1 if o.name.endswith("L") else -1) * turn * D(90)


def animate_drawer():
    """Key the levers and the drawer at DRAWER_KEYS; the carrier's sink follows the shaft profile,
    so it's keyed every frame of the lever turns."""
    cart, levers = drawer_parts()
    for f, turn, out in DRAWER_KEYS:
        pose_drawer(turn, out)
        for o in cart:
            o.keyframe_insert("delta_location", index=1, frame=f)
        for o in levers:
            o.keyframe_insert("delta_rotation_euler", index=1, frame=f)
    lv = bpy.data.objects["dshaft_lever_R"]
    fc = next(c for c in _fcurves(lv) if c.data_path == "delta_rotation_euler" and c.array_index == 1)
    carrier = [o for o in cart if o.name.startswith(CARRIER)]
    for f in range(DRAWER_KEYS[0][0], DRAWER_KEYS[-1][0] + 1):
        turn = -fc.evaluate(f) / D(90)
        for o in carrier:
            o.delta_location.z = -dshaft_drop(turn)
            o.keyframe_insert("delta_location", index=2, frame=f)
    pose_drawer(0, 0)
    bpy.context.scene.frame_end = DRAWER_KEYS[-1][0]


def _fcurves(o):
    """F-curves of an object's action (Blender 5 keeps them in layered channelbags)."""
    act = o.animation_data.action
    for layer in act.layers:
        for strip in layer.strips:
            bag = strip.channelbag(o.animation_data.action_slot)
            if bag:
                yield from bag.fcurves


def world_bvh(o):
    dg = bpy.context.evaluated_depsgraph_get()
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    mw = o.matrix_world
    t = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [p.vertices[:] for p in me.polygons])
    oe.to_mesh_clear()
    return t


def collision_report():
    """Check every mesh pair that can meet: moving groups vs everything at each keyframe, plus
    the new static drive parts vs the rest at rest. Intended contacts are whitelisted."""
    obj = bpy.data.objects
    meshes = [o for o in obj if o.type == 'MESH' and o.name != "Ground" and not o.name.startswith(("LCD", "encoder"))]
    lift_g = {o.name for o in meshes if o.parent and o.parent.name == "lift_platform"}
    plg_g = {o.name for o in meshes if o.parent and o.parent.name == "plunger_carriage"}
    new_static = {o.name for o in meshes if o.name.startswith(("lift_screw", "lift_pulley", "lift_belt", "lift_motor",
                  "KFL08", "lift_base", "plunger_screw", "plunger_pulley", "plunger_belt", "plunger_motor",
                  "lift_idler", "lift_tensioner", "lift_home_switch", "plunger_idler", "plunger_tensioner",
                  "ext_head", "head_bracket", "plunger_switch", "ScreenHousing", "control_box_base", "syringe_lock_frame", "usb_panel_socket", "eject_", "plunger_optical", "cartridge_plate", "syringe_grip", "top_plate",
                  "cart_ledge", "cart_spacer", "cart_detent", "cartridge_handle"))}
    allowed = [("lift_screw", "lift_nut"), ("lift_screw", "KFL08_lift"), ("lift_screw", "lift_pulley"),
               ("lift_screw", "lift_base_plate"), ("plunger_screw", "plunger_nut"), ("plunger_screw", "KFL08_plunger"),
               ("plunger_screw", "plunger_pulley"), ("plunger_screw", "pipette_plate"), ("KFL08_lift", "lift_base_plate"),
               ("KFL08_plunger", "pipette_plate"), ("lift_motor", "lift_base_plate"), ("lift_motor", "lift_pulley_motor"),
               ("plunger_motor", "pipette_plate"), ("plunger_motor", "plunger_pulley_motor"),
               ("lift_belt", "lift_pulley"), ("plunger_belt", "plunger_pulley"), ("lift_motor", "lift_motor"),
               ("plunger_motor", "plunger_motor"), ("MGN9H_carriage", "MGN9H_rail"), ("MGN9H_carriage", "lift_interface"),
               ("MGN9H_carriage", "interface_plate"), ("head_fixed_mount", "MGN9H_rail"), ("lift_base_plate", "ext_bed"),
               ("KFL08_lift", "lift_screw"), ("plungers_x96", "syringe_barrels"),   # stoppers ride inside the (solid) barrels
               ("lift_belt", "lift_idler"), ("plunger_belt", "plunger_idler"), ("lift_idler", "lift_tensioner"),
               ("plunger_idler", "plunger_tensioner"), ("lift_idler", "lift_idler"), ("plunger_idler", "plunger_idler"),
               ("lift_tensioner", "lift_base_plate"), ("plunger_tensioner", "pipette_plate"),
               ("lift_home_switch", "lift_home_switch"), ("lift_home_switch_holder", "lift_base_plate"),
               ("lift_home_switch_lever", "lift_plate"),   # the platform presses the lever at home
               ("head_bracket", "pipette_plate"), ("head_bracket", "ext_head"), ("ext_head", "post"),
               ("plunger_idler", "pipette_plate"), ("lift_idler", "lift_base_plate"),
               ("plunger_switch", "pipette_plate"), ("plunger_switch", "plunger_switch"),
               ("control_box_base", "ScreenHousing"),
               ("eject_rod", "plunger_carriage_bracket"), ("eject_rod", "eject_plate"), ("eject_rod", "eject_spring"),
               ("eject_spring", "syringe_lock_frame"), ("eject_plate", "pipette_tips"), ("eject_plate", "syringe_barrels"),
               ("plunger_optical", "pipette_plate"), ("plunger_optical", "plunger_optical"),
               ("cartridge_plate", "pipette_plate"), ("cartridge_plate", "syringe_barrels"),
               ("cartridge_plate", "syringe_lock_frame"), ("cartridge_plate", "syringe_grip"),
               ("cartridge_plate", "eject_spring"),
               ("eject_rod", "plunger_carrier"),
               ("top_plate", "ext_top"), ("top_plate", "post_"), ("top_plate", "angle_bracket"), ("KFL08_plunger", "top_plate"), ("plunger_motor", "top_plate"),
               ("plunger_tensioner", "top_plate"), ("plunger_idler", "top_plate"), ("plunger_idler", "plunger_tensioner"),
               ("plunger_screw", "top_plate"), ("cart_spacer", "pipette_plate"), ("cart_ledge", "cart_spacer"),
               ("cart_detent", "cart_ledge"), ("cartridge_handle", "cartridge_plate"), ("usb_panel_socket", "ScreenHousing"), ("usb_panel_socket", "usb_panel_socket"), ("syringe_lock_frame", "syringe_barrels"),
               ("syringe_lock_frame", "pipette_plate"), ("ScreenHousing", "LCD_2004"), ("ScreenHousing", "encoder")]   # bolts in slots
    ok = lambda a, b: any((a.startswith(p) and b.startswith(q)) or (a.startswith(q) and b.startswith(p)) for p, q in allowed)
    hits = {}
    samples = sorted({(l, a) for _, l, a in KEYS} | {(0.5, 0), (0.5, 1), (1, 0.5), (0, 0.5)} |
                     {(0, -e / ASPIRATE) for e in (EJ_GAP_F + 1, EJ_GAP_B, EJ_GAP_B + 3)})
    for l, a in samples:
        pose(l * LIFT_TRAVEL, a * ASPIRATE)
        bpy.context.view_layer.update()
        bv = {o.name: world_bvh(o) for o in meshes}
        movers = lift_g | plg_g | new_static
        for i, na in enumerate(sorted(movers)):
            for nb in bv:
                if nb == na or (nb in movers and nb < na) or ok(na, nb):
                    continue
                if (na in lift_g and nb in lift_g) or (na in plg_g and nb in plg_g):
                    continue
                if bv[na].overlap(bv[nb]):
                    hits.setdefault(f"{na} x {nb}", []).append((round(l * LIFT_TRAVEL, 1), round(a * ASPIRATE, 1)))
    pose(0, 0)
    return hits


if __name__ != "motor_lib":        # exec with this name to load functions only
    g["build"]()
    g["stage"]()
    belts = modify()
    pose(0, 0)
    animate()                        # keyframe a full cycle for timeline playback
    animate_drawer()                 # then a cartridge swap
summary = {
    "lift_travel_mm": round(LIFT_TRAVEL, 2),
    "lift_revs": round(LIFT_TRAVEL / LIFT_LEAD, 1),
    "wellplate_top_mm": [round(LIFT0 + T + TRAY_H + PLATE_H, 1), round(LIFT0 + T + TRAY_H + PLATE_H + LIFT_TRAVEL, 1)],
    "tip_bottom_mm": round(TIP_BOTTOM, 1),
}
