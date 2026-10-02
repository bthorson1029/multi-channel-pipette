"""Build the multi-channel pipette in Blender (mm units, Z up, front = -Y): fixed head, motorized
lead-screw bed lift, belt-synced plunger drive.

  * LIFT: one NEMA17 drives two T8 screws through a closed GT2 loop. The screws run in KFL08 flange
    bearings under a steel base plate hung beneath the bed-level side bars; the motor hangs below
    that plate. Brass nuts under the platform, which rides four MGN9H rails on the posts. Heights
    are programmable per labware; the screws hold position.
  * PLUNGER: one NEMA17 + a closed GT2 loop around four T8x2 screws at (+/-65, +/-58.9). The screws
    hang from KFL08s on a plate across the frame's top ring, with the pulleys, belt and idler under
    it and the motor standing on it; only the anti-backlash nuts ride on the drive (plunger) plate,
    so the plate can't rack if a step is missed. A 2020 stiffening frame on the drive plate.
  * both belts have a smooth-idler tensioner on a slotted printed bracket; the lift homes onto a
    micro switch pressed by the platform at the bottom of travel, the plunger onto three optical
    endstops (with a level check)
  * the pipette plate is bolted through two printed brackets to a 2020 bar along each side of the
    frame; the lift platform's rail plates bolt to four printed carriage brackets on the platform
  * the control box lies in front of the base with its screen panel sloped toward the user
    (CONTROL_SLOPE_DEG), low enough that labware slides in from the front over it
  * everything syringe- and tip-specific is a cartridge that slides in at the front like a drawer:
    its plate runs in channels under the pipette plate (a U, open at the front), its plunger carrier
    over two D-shaft clamps under the drive plate; a tip ejector and optical home sensors let the
    plunger go past home to push the tips off (see "Syringe cartridge" in 01_Hardware/README.md)
  * every fastener in the BOM (fasteners()), demo labware and a full run on the timeline
    (CYCLE), and collision/clearance checks
Layout numbers and the laser-cut plates come from 01_Hardware/make_dxf.py (run it first if the
DXFs are missing); export_parts.py writes the printed parts as STL. The base parts and helpers are
in pipette_lib.py.
Run: blender --python 04_Blender/build_pipette.py  (or open it in Blender's Text Editor and Run Script)
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
g = {"__name__": "pipette_lib", "__file__": os.path.join(HERE, "pipette_lib.py")}
exec(open(os.path.join(HERE, "pipette_lib.py"), encoding="utf-8").read(), g)   # base parts + helpers

FAB = os.path.normpath(os.path.join(HERE, "..", "01_Hardware"))
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
LIFT0 = 80.0                      # platform underside at the bottom of travel: the T8 nut flange's screws and nuts clear the pulley
TRAY_H, PLATE_H = 15.0, 14.4
TIP_DEPTH = 9.0                   # tips this far into the wells at the top of travel
SEAT = P - T                      # syringe flanges sit on the cartridge carrier plate, under the pipette plate
TIP_DROP = 8.0                    # tips sit this much lower than on the original's press-fit head: the carrier plate (3 mm)
TIP_BOTTOM = P - 112 - TIP_DROP   # and the ejector plate (3 mm) under the barrel ends, plus 2 mm
LIFT_TRAVEL = (TIP_BOTTOM + TIP_DEPTH) - (LIFT0 + T + TRAY_H + PLATE_H)
LIFT_LEAD = 2.0                   # T8x2 on the lift: force + self-locking
BRK_H = 18.0                      # lift carriage bracket height above the plate
BRK_BOLT_Z = LIFT0 + T + 10.0     # rail-plate M4 row: the rail plates ride this high so it clears the plate
LIFT_IF_HOLE_Y = (PY - 30.0, PY - 50.0)   # the rail plate's 2 M4 holes (DXF x 20, 40; anchor x -10 at PY)
PLG_BRK_H = 18.0                  # plunger carriage bracket height under the plate
PLG_BRK_POCKET = 11.5             # its bolt pockets' floor under the plate: an M4 x 20 then goes 5.5 into a T-nut
assert L.CARRIAGE_Y == PY and PLG_MID - L.RAIL_ZC_BELOW_MID == g["ZC_HIGH"]
# plunger
PS_XY = L.PS_XY                   # order: LF, RF, LB, RB
PLG_MOTOR_XY = L.PLG_MOTOR_XY
SWITCH_TOP = P + 39 + 11.5        # limit-switch lever tops on the pipette-plate corner blocks
PLG_REST = (SWITCH_TOP + 0.5) - (PLG_MID - T / 2)   # home = plate just off the switches (firmware homes onto them)
ASPIRATE = 12.0                   # animation stroke (~215 uL in a 4.78 mm-bore 1 mL syringe)
PLG_LEAD = 2.0                    # T8x2: 4x the resolution and thrust of the original's T8x8
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
             "eject_", "plunger_carrier", "pad_retainer", "plungers_x96", "cartridge_fasteners", "tip_cone")
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
# Tip cones (see tip_cone_bm()): a resin sleeve pushed onto each syringe's Luer-slip nozzle. Its
# bore is the female Luer taper and its outside is the cone the tips seal on, so every channel gets
# the same fit. The tip's mouth limits the sleeve to about 5.2 mm, so the wall over the nozzle is
# thin. It is short so the ejector pushes every tip clear of it: at EJECT_MM the back row's tips
# (the least-pushed, the plate being tilted) end CONE_EJECT_CLEAR below the cone's end.
LUER_D, LUER_TAPER = 3.976, 0.06  # male Luer nozzle: diameter at its end (ISO 80369-7: 3.925-4.027), 6 % taper
LUER_LEN = 8.0                    # nozzle below the barrel end (7.5 minimum)
CONE_ENGAGE = 4.5                 # nozzle inside the sleeve: its top then sits 0.5 under the ejector plate
CONE_TOP = 0.5                    # straight band at the top
CONE_SEAL = (5.14, 4.90, 4.6)     # seal cone: diameter at the band, diameter at its end, end below the top
CONE_LEN, CONE_TIP_D = 5.3, 4.6   # overall length; lead-in chamfer to this diameter. The bore runs
                                  # through, so a nozzle at the small end can seat deeper.
CONE_EJECT_CLEAR = 1.0            # wanted gap (checked by eject_clearance())
CONE_SIZES = (-0.2, -0.1, 0.0, 0.1, 0.2)   # sizing set: offsets on the seal cone's diameter
CONE_Z = SEAT - 58 - T - 0.5      # sleeve top: 0.5 under the ejector plate at rest
# Plunger home sensors: slotted optical endstops (TCST2103-type fork, 24.5 x 10.8 x 6.3 mm body,
# 3.1 mm slot, M3 ears 19 mm apart; check yours). Laid flat, so each flag passes straight through
# its slot; the sensor sits OPT_BELOW under the plunger plate at home so the plate and the flag's
# 3 mm tab clear it when it goes EJECT_MM lower.
OPT_BODY = (24.5, 10.8, 6.3)
OPT_SLOT = 3.1
OPT_EARS = 19.0
OPT_BELOW = EJECT_MM + 3.0 + 1.5 + 2.4   # + the M3 pan heads holding the sensor down
CBOX_BOSSES = [(sx * 79.0, y + CBOX_DY) for sx in (-1, 1) for y in (-207.5, -117.5)]   # the housing's lid screw bosses (measured)
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
    bm = bmesh.new()                                  # countersinks from below: flush heads
    for s_ in (-1, 1):
        _cone(bm, 3.15, 1.6, zu - 3.01, zu - 3 + 1.95, seg=24, xy=(x, y + s_ * L.FLAG_HOLE_DY))
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
        _cone(bm, 4.2, 4.2, zb - 1, zt - PLG_BRK_POCKET, seg=6, xy=(sx * x, sy * y))
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
        _cone(t, LUER_D / 2, (LUER_D + LUER_TAPER * LUER_LEN) / 2, SEAT - 58 - LUER_LEN, SEAT - 58,
              seg=20, xy=(x, y))   # Luer-slip nozzle
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


def tip_cone_bm(d_off=0.0, seg=40):
    """One tip cone as a closed solid of revolution, top at z = 0: the female Luer bore, open
    through (the nozzle's end sits CONE_ENGAGE in), and outside a short band, the seal cone (d_off
    added to its diameters) and a lead-in chamfer (not offset, to keep its wall)."""
    mouth = LUER_D + LUER_TAPER * CONE_ENGAGE
    prof = [((CONE_SEAL[0] + d_off) / 2, 0), ((CONE_SEAL[0] + d_off) / 2, -CONE_TOP),
            ((CONE_SEAL[1] + d_off) / 2, -CONE_SEAL[2]), (CONE_TIP_D / 2, -CONE_LEN),
            ((mouth - LUER_TAPER * CONE_LEN) / 2, -CONE_LEN), (mouth / 2, 0)]
    bm = bmesh.new()
    vs = [bm.verts.new((r, 0, z)) for r, z in prof]
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.spin(bm, geom=vs + es, cent=(0, 0, 0), axis=(0, 0, 1), angle=2 * math.pi, steps=seg, use_merge=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def tip_cones(name, coll):
    """96 tip cones on the nozzles (part of the cartridge)."""
    one = bpy.data.meshes.new("tmp")
    tip_cone_bm(seg=24).to_mesh(one)
    bm = bmesh.new()
    for x, y in g["GRID"]:
        n0 = len(bm.verts)
        bm.from_mesh(one)
        bm.verts.ensure_lookup_table()
        bmesh.ops.translate(bm, verts=bm.verts[n0:], vec=(x, y, CONE_Z))
    bpy.data.meshes.remove(one)
    o = new_obj(name, bm, coll, M["white"])
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def tip_cone_sizing_set(name, coll):
    """Print-only: one cone per CONE_SIZES offset, smallest to largest, each hung by a thin tab from
    its top band off a bar with a notch at the smallest end."""
    pitch, bar_y, bar = 9.0, -5.0, (2.0, 3.0)
    bm = bmesh.new()
    for i, d in enumerate(CONE_SIZES):
        t = tip_cone_bm(d)
        bmesh.ops.translate(t, verts=t.verts[:], vec=(i * pitch, 0, 0))
        me = bpy.data.meshes.new("tmp")
        t.to_mesh(me)
        t.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    o = new_obj(name, bm, coll, M["white"])
    n = len(CONE_SIZES)
    u = bmesh.new()
    x0, x1 = -pitch / 2, (n - 0.5) * pitch
    _block(u, x0, x1, bar_y - bar[0] / 2, bar_y + bar[0] / 2, -bar[1], 0)
    for i in range(n):                         # 0.8 x 0.45 mm tabs, from the bar into the top band
        _block(u, i * pitch - 0.4, i * pitch + 0.4, bar_y, -2.3, -0.45, -0.05)
    boolean(o, u, 'UNION')
    cut = bmesh.new()                          # notch: marks the smallest size's end
    _block(cut, x0 - 1, x0 + 1.5, bar_y - 2, bar_y + 2, -bar[1] - 1, -bar[1] / 2)
    boolean(o, cut)
    return o


def syringe_lock_frame(name, coll):
    """Printed frame that clamps the trimmed syringe flanges to the cartridge carrier plate
    (replaces the original's S-P retainer and the press fit). Its underside has one slot per row,
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
    """The original grip, opened to a slip fit and hung from the carrier plate: 4 ears under the frame
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
        bm = bmesh.new()                                                      # pockets for the T8 nuts' flange-screw
        for psx, psy in L.PS_XY:                                              # nuts under the plate (the front pair
            for x, y in t8_flange_screws(psx, psy):                           # lands on the wall)
                if x * sx > 0 and y0 < y < y1:
                    _cone(bm, 3.6, 3.6, zu - 4.5, zu + 1, xy=(x, y))
        if bm.verts:
            boolean(tr, bm, self_intersect=True)
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
    """Printed nest that locates the well plate on the lift platform (replaces the original's flat tray).
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
    for sx in (-1, 1):                                  # clear of the lift nuts' flange-screw heads
        _cone(bm, 11.5, 11.5, z0 - 1, z0 + TRAY_H + 5, seg=48, xy=(sx * LIFT_X, 0))
    boolean(o, bm)
    bm = bmesh.new()
    for x, y in L.NEST_HOLES:
        _cone(bm, 4.2, 4.2, z0 + 6, z0 + TRAY_H + 1, xy=(x, y))
    boolean(o, bm)
    return o


def close_control_box(h):
    """The original housing hung on the frame with its open back against the posts and its lid set
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
        _cone(bm, 1.2, 1.2, -1, 30, xy=(x, y))       # inside the housing boss's 2.5 hole, no shared wall)
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
    """A laser-cut plate from the generated DXFs (01_Hardware/ToLaserCut-DXF)."""
    o = dxf_part(os.path.join(FAB_DXF, fname), obj_name, T, coll, M["steel"])
    o.location = loc
    return o


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
    # only merges in self-intersection mode. export_parts.py refuses to write the part
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
    # rails: full height for the lift + plunger carriages
    r0, r1 = BASE_Z - 7, FH - 25
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(f"MGN9H_rail_{'LR'[sx > 0]}{'FB'[sy > 0]}", (6.5, 9, r1 - r0),
                (sx * (IX - 3.25), sy * PY, (r0 + r1) / 2), "Frame", M["chrome"], bevel=0.3)
    # pipette plate fixed to the frame: a 2020 bar along each side at plate height, joined to
    # the plate by printed brackets
    for sx in (-1, 1):
        g["tslot_bar"](f"ext_head_{'LR'[sx > 0]}", g["FY"] - 40, (sx * g["PX"], 0, P - T - 10), 'Y', "Frame", M["ext"])
        head_bracket(f"head_bracket_{'LR'[sx > 0]}", sx, "Head")
    # syringes: tab stubs keyed under a locking frame instead of cut-off ends hammered into the grip
    # (the grip stays as a slip-fit guide for the barrels' lower ends)
    fab_plate("cartridge_plate.dxf", "cartridge_plate", "Head", (0, 0, SEAT - T / 2))
    cartridge_handle("Head")
    drawer_channels()
    syringe_barrels("syringe_barrels_x96", "Syringes")
    syringe_lock_frame("syringe_lock_frame", "Head")
    cartridge_grip(obj["syringe_grip_static"])
    tip_ejector("Head")
    tip_cones("tip_cones_x96", "Syringes")
    # plunger home sensors: printed posts bolted to the pipette plate's arms carry three slotted
    # optical endstops (the firmware homes on the first and checks the other two). Optical, because
    # the plunger goes on past home to eject tips.
    for x, y in L.SWITCH_POSTS:
        optical_post(f"plunger_optical_{'LR'[x > 0]}{'FB'[y > 0]}", x, y, SWITCH_TOP + 0.5 - OPT_BELOW - OPT_BODY[2] / 2, "Head")

    # ---------------- LIFT
    fab_plate("lift_base_plate.dxf", "lift_base_plate", "Frame", (0, 0, BASE_Z + T / 2))
    nema17("lift_motor", *LIFT_MOTOR_XY, BASE_Z, True, "Bed")
    obj["lift_motor_shaft"].location.z = BASE_Z + 9
    for sx in (-1, 1):
        tag = "LR"[sx > 0]
        kfl08(f"KFL08_lift_{tag}", sx * LIFT_X, 0, BASE_Z, True, "Bed")
        ls = 148.0                                     # past the nut at the top of travel
        cyl(f"lift_screw_{tag}", 4, ls, (sx * LIFT_X, 0, BASE_Z - 14 + ls / 2), "Bed", M["chrome"], seg=16)
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
    src = dxf_part("lift_rail_plate.dxf", "lift_interface", T, "Bed", M["steel"])
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
    tray, wp = well_plate_nest("well_plate_nest", LIFT0 + T, "Bed"), obj["well_plate_96"]
    wp.location.z = LIFT0 + T + TRAY_H + PLATE_H / 2
    members += [tray, wp]
    rig_empty("lift_platform", "Bed", members)

    # ---------------- PLUNGER drive on the top plate: the pipette plate is a U open at the front for
    # the cartridge drawer, so the screws hang from KFL08s on a plate across the top ring, with their
    # pulleys, the belt and the idler under it (inside the ring) and the motor standing on it.
    pip, plg = obj["pipette_plate"], obj["plunger_plate"]
    fab_plate("top_plate.dxf", "top_plate", "Frame", (0, 0, FH + T / 2))
    z_top = FH + T
    s_lo, s_hi = P + 26.7, z_top + 14.0               # screw: below the nut at full eject, up through the KFL08
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

    # moving plunger carriage: drive plate, the cartridge's plunger carrier, carriage brackets,
    # rail plates, carriages, nuts, stiffener
    rails = [o for o in obj if o.name.startswith("interface_plate_high")]
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


# ================================================================ fasteners
# Every screw, bolt, nut, washer and T-nut the BOM calls for, placed on the same hole lists the parts
# are cut from. One object per joint (fast_<joint>), parented to whatever moves it. Each fastener is
# logged in FAST_LOG (joint, bearing point, direction, length, grip, what it threads into) so the
# checks can confirm its shank runs down a real hole, and its length is checked as it's placed:
# a T-nut bolt must pass through the T-nut (4.2 mm past the slot face) and stop short of the
# extrusion's core (6.1), a nut bolt must pass through its nut, and a screw into a part must get
# enough thread.
HEAD = {  # d: socket (dk, k), button (dk, k), pan (dk, k), countersunk (dk, depth)
    "socket": {2: (3.8, 2.0), 3: (5.5, 3.0), 4: (7.0, 4.0), 5: (8.5, 5.0)},
    "button": {3: (5.7, 1.65), 4: (7.6, 2.2), 5: (9.5, 2.75)},
    "pan": {3: (5.6, 2.4)},
    "csk": {3: (6.0, 1.86)},
}
NUT = {2: (4.0, 1.6), 3: (5.5, 2.4), 4: (7.0, 3.2), 5: (8.0, 4.0)}   # across flats, height
WASHER = {3: (7.0, 0.5), 4: (9.0, 0.8), 5: (10.0, 1.0)}             # OD, thickness
TNUT_FACE, TNUT_T, SLOT_CORE = 1.9, 2.3, 6.1                         # 2020: behind the 1.8 lip; core depth
FAST_LOG, FAST_WARN = [], []
_FB = {}                                                             # joint -> [bmesh, parent name]


def _fbm(joint, parent=None):
    if joint not in _FB:
        _FB[joint] = [bmesh.new(), parent]
    return _FB[joint][0]


def _frustum(bm, p0, p1, r0, r1, seg=16):
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=d.length,
                          matrix=Matrix.Translation((p0 + p1) / 2) @ rot)


def fastener(joint, p, u, d, length, grip=0.0, head="socket", nut=False, washer=False, tnut=None,
             into=(), min_thread=None, parent=None, head_washer=False, tnut_off=0.0):
    """p: the face the head bears on (for a countersunk head, the flush surface); u: into the joint.
    grip: clamped thickness from p to the far face, where a nut (nut=True, washer under it if
    washer) or a T-nut (tnut = the slot's direction) goes. into: object-name prefixes the shank
    threads into (tapped, self-tapping or a nut's own part); min_thread: engagement it needs there."""
    p, u = Vector(p), Vector(u).normalized()
    bm = _fbm(joint, parent)
    if head_washer:                                   # the head bears on a washer; the shank starts there
        od, t = WASHER[d]
        _frustum(bm, p - u * t, p, od / 2, od / 2)
        p, length, grip = p - u * t, length, grip + t
    if head == "csk":
        dk, k = HEAD["csk"][d]
        _frustum(bm, p, p + u * k, dk / 2, d / 2)
    elif head != "none":
        dk, k = HEAD[head][d]
        _frustum(bm, p - u * k, p, dk / 2, dk / 2)
    _frustum(bm, p, p + u * length, d / 2 - 0.1, d / 2 - 0.1, seg=12)
    far = p + u * grip
    if washer:
        od, t = WASHER[d]
        _frustum(bm, far, far + u * t, od / 2, od / 2)
        far = far + u * t
    if nut:
        af, h = NUT[d]
        _frustum(bm, far, far + u * h, af / math.sqrt(3), af / math.sqrt(3), seg=6)
        if length < grip + (WASHER[d][1] if washer else 0) + h:
            FAST_WARN.append(f"{joint}: M{d} x {length} ends before its nut is through (needs {grip + h:.1f})")
    if tnut is not None:
        a = Vector(tnut).normalized()
        c = far + u * (TNUT_FACE + TNUT_T / 2) + a * tnut_off     # off-center along the slot near a bar's end
        g_ = bmesh.ops.create_cube(bm, size=1)
        across = u.cross(a)
        bmesh.ops.transform(bm, verts=g_["verts"], matrix=Matrix(
            [[a[i] * 10.0, across[i] * 9.5, u[i] * TNUT_T, c[i]] for i in range(3)] + [[0, 0, 0, 1]]))
        past = length - grip
        if not TNUT_FACE + TNUT_T <= past <= SLOT_CORE - 0.1:
            FAST_WARN.append(f"{joint}: M{d} x {length} goes {past:.1f} into the slot (T-nut needs 4.2-6.0)")
    if min_thread is not None and length - grip < min_thread:
        FAST_WARN.append(f"{joint}: M{d} x {length} gets {length - grip:.1f} of thread (wants {min_thread})")
    FAST_LOG.append((joint, p.copy(), u.copy(), length, grip, tuple(into),
                     dict(d=d, head=head, nut=nut, washer=washer or head_washer, tnut=tnut is not None)))


def _span(name, axis=2):
    """(min, max) of an object's world vertices along an axis."""
    o = bpy.data.objects[name]
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    return min(v[axis] for v in vs), max(v[axis] for v in vs)


def _dxf_holes(obj, path, r_lo, r_hi):
    """World centers of an imported plate's DXF circles with r_lo <= r <= r_hi."""
    L_ = [l.strip() for l in open(path, errors='ignore').read().splitlines()]
    out, cur, ins = [], None, False
    for c, v in zip(L_[0::2], L_[1::2]):
        if c == '2' and v == 'ENTITIES':
            ins = True
            continue
        if not ins:
            continue
        if c == '0':
            if cur and cur.get('t') == 'CIRCLE' and r_lo <= float(cur['40']) <= r_hi:
                out.append(obj.matrix_world @ Vector((float(cur['10']), float(cur['20']), 0)))
            cur = {'t': v}
        elif cur is not None:
            cur[c] = v
    return out


def t8_flange_screws(x, y):
    """The 4 flange screws of a T8 nut at (x, y): on the 16 mm circle, 45 deg off the axes."""
    r = L.T8_NUT_PCD / 2
    return [(x + r * math.cos(D(45 + 90 * k)), y + r * math.sin(D(45 + 90 * k))) for k in range(4)]


def inside_corner_bracket(bm, corner, a, b, n=20.0, t=4.0, w=18.0):
    """2020 inside corner bracket (cast L) in the corner at `corner`: leg along +a on the face whose
    normal is -b, leg along +b on the face whose normal is -a; w wide along a x b. Returns the two
    bolt positions (on each leg's inner face) and the direction into each face."""
    corner, a, b = Vector(corner), Vector(a), Vector(b)
    c = a.cross(b)
    for leg_dir, face_n in ((a, b), (b, a)):
        ctr = corner + leg_dir * (n / 2) + face_n * (t / 2)
        g_ = bmesh.ops.create_cube(bm, size=1)
        bmesh.ops.transform(bm, verts=g_["verts"], matrix=Matrix(
            [[leg_dir[i] * n, face_n[i] * t, c[i] * w, ctr[i]] for i in range(3)] + [[0, 0, 0, 1]]))
    web = [corner + a * t, corner + a * (n * 0.8), corner + b * (n * 0.8), corner + b * t]
    for s_ in (-1, 1):                                           # two gussets at the leg edges
        off = c * s_ * (w / 2 - 1.0)
        vs = [bm.verts.new(v + off + c * dz) for dz in (-1.0, 1.0) for v in web]
        for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
            bm.faces.new([vs[i] for i in f])
    return [(corner + a * (n * 0.55) + b * t, -b), (corner + b * (n * 0.55) + a * t, -a)]


def fasteners():
    """Place every fastener (rigs at their build positions: call before pose())."""
    obj = bpy.data.objects
    X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
    _FB.clear()
    FAST_LOG.clear()
    FAST_WARN.clear()
    SP, SL, SC = "plunger_carriage", "lift_platform", None

    # ---- bought parts are modeled as plain solids: drill their mounting holes where the fasteners go
    bpy.context.view_layer.update()
    for o in [o for o in obj if o.name.startswith("KFL08_")]:
        c, a = o.matrix_world.translation, o.matrix_world.to_3x3() @ Vector((L.KFL08_BOLTS / 2, 0, 0))
        drill(o, [(c.x + a.x, c.y + a.y), (c.x - a.x, c.y - a.y)], L.M4 / 2)
    for o in [o for o in obj if o.name.startswith(("lift_nut_flange_", "plunger_nut_flange_"))]:
        c = o.matrix_world.translation
        drill(o, t8_flange_screws(c.x, c.y), L.M3 / 2)
    sw = obj["lift_home_switch_body"]                            # its 2 mounting holes, 9.5 apart, along y
    s0, _ = _span("lift_home_switch_body")
    bm = bmesh.new()
    for s_ in (-1, 1):
        _bar(bm, (HOME_SW_XY[0] + s_ * 4.75, HOME_SW_XY[1] - 10, s0 + 3), (HOME_SW_XY[0] + s_ * 4.75, HOME_SW_XY[1] + 10, s0 + 3), 1.1)
    boolean(sw, bm)
    fl = obj["usb_panel_socket_flange"]                          # its 2 ears
    uy, uz = USB_PANEL_YZ
    fx0, fx1 = _span("usb_panel_socket_flange", 0)
    bm = bmesh.new()
    for s_ in (-1, 1):
        _bar(bm, (fx0 - 1, uy + s_ * USB_PANEL_EARS / 2, uz), (fx1 + 1, uy + s_ * USB_PANEL_EARS / 2, uz), L.M3 / 2)
    boolean(fl, bm)

    # ---- top plate into the top ring (12), base plate up into the bed-level side bars (4)
    zt0, zt1 = _span("top_plate")
    for x, y in L.TOP_MOUNT_XY:
        along = Y if abs(x) > 100 else X
        fastener("fast_top_plate", (x, y, zt1), -Z, 5, 8, grip=zt1 - zt0, head="button", tnut=along)
    zb0, zb1 = _span("lift_base_plate")
    for x, y in L.BASE_MOUNT_XY:
        fastener("fast_base_plate", (x, y, zb0), Z, 5, 8, grip=zb1 - zb0, head="button", tnut=Y)

    # ---- inside corner brackets: head side bars and bed-level side bars to the posts (under each
    # bar end), and the plunger stiffener's corners
    bmb = _fbm("inside_corner_brackets")
    for bar in ("ext_head", "ext_bed"):
        for sx in (-1, 1):
            name = f"{bar}_{'LR'[sx > 0]}"
            z0, _ = _span(name)
            y0, y1 = _span(name, 1)
            for sy, yend in ((-1, y0), (1, y1)):
                bolts = inside_corner_bracket(bmb, (sx * g["PX"], yend, z0), -sy * Y, -Z)
                (p1, u1), (p2, u2) = bolts
                fastener("fast_inside_corners", p1, u1, 5, 10, grip=4.0, head="socket", tnut=Y)
                fastener("fast_inside_corners", p2, u2, 5, 10, grip=4.0, head="socket", tnut=Z)
    bms = _fbm("stiffener_corner_brackets", SP)
    zs0, _ = _span("plunger_stiffener_F")
    ly, sxx = L.STIFF_LONG_Y - 10, L.STIFF_SHORT_X - 10          # inner faces of the long / short bars
    for sx in (-1, 1):
        for sy in (-1, 1):
            bolts = inside_corner_bracket(bms, (sx * sxx, sy * ly, zs0 + 10), -sx * X, -sy * Y, n=18.0, w=16.0)
            for (pp, uu), along in zip(bolts, (X, Y)):
                pp = Vector(pp)
                pp.z = zs0 + 10                                  # on the slot's centerline
                fastener("fast_stiffener_corners", pp, uu, 5, 10, grip=4.0, head="socket", tnut=along, parent=SP)

    # ---- linear rails into the posts' inner slots (20 mm pitch) and carriages to the rail plates
    for sx in (-1, 1):
        for sy in (-1, 1):
            r0, r1 = _span(f"MGN9H_rail_{'LR'[sx > 0]}{'FB'[sy > 0]}")
            xf = sx * g["IX"]                                    # post face under the rail
            n = int((r1 - r0) // 20)
            for i in range(n):
                z = r0 + 10 + 20 * i
                fastener("fast_rails", (xf - sx * 3.0, sy * g["PY"], z), sx * X, 3, 8, grip=3.0,
                         head="socket", tnut=Z, into=("MGN9H_rail",))
    for pl, parent, fname in (("interface_plate_high", SP, os.path.join(FAB_DXF, "plunger_rail_plate.dxf")),
                              ("lift_interface", SL, os.path.join(FAB_DXF, "lift_rail_plate.dxf"))):
        for o in [o for o in obj if o.name.startswith(pl)]:
            xc = o.matrix_world.translation.x
            s = 1 if xc > 0 else -1
            for h in _dxf_holes(o, fname, 1.6, 1.8):            # carriage screws, from inside
                fastener(f"fast_{pl}_carriage", (xc - s * T / 2, h.y, h.z), s * X, 3, 6, grip=T,
                         head="socket", into=("MGN9H_carriage",), min_thread=2.5, parent=parent)
            for h in _dxf_holes(o, fname, 2.2, 2.3):            # into the carriage bracket's captive nut
                xn = s * (77.25 if parent == SP else 74.75)      # nut slot centers (see the bracket builders)
                grip = abs((xc + s * T / 2) - (xn + s * NUT[4][1] / 2))
                fastener(f"fast_{pl}_bracket", (xc + s * T / 2, h.y, h.z), -s * X, 4, 12, grip=grip,
                         head="socket", nut=True, parent=parent)

    # ---- lift platform: carriage brackets (counterbored heads) and the nest down through the plate
    zl0, zl1 = _span("lift_plate")
    for x, y in L.LIFT_BRACKET_HOLES:
        zc = zl1 + 8.0                                           # counterbore floor
        fastener("fast_lift_brackets", (x, y, zc), -Z, 4, 16, grip=zc - zl0, head="socket", nut=True, parent=SL)
    for x, y in L.NEST_HOLES:
        zc = zl1 + 6.0
        fastener("fast_nest", (x, y, zc), -Z, 4, 16, grip=zc - zl0, head="socket", nut=True, parent=SL)
    # T8 lift nuts: flange under the plate; screws down from the plate's top (the heads clear the nut
    # body, the nest is cut back around them), nuts under the flange, 1 mm over the pulley at home
    for sx in (-1, 1):
        f0, f1 = _span(f"lift_nut_flange_{'LR'[sx > 0]}")
        for x, y in t8_flange_screws(sx * LIFT_X, 0):
            fastener("fast_lift_nuts", (x, y, zl1), -Z, 3, 10, grip=zl1 - f0, head="socket", nut=True, parent=SL)

    # ---- plunger carriage: T8 nuts (flange on top of the drive plate, nut + washer underneath)
    zp0, zp1 = _span("plunger_plate")
    for i, (x0, y0) in enumerate(L.PS_XY, 1):
        _, f1 = _span(f"plunger_nut_flange_{i}")
        for x, y in t8_flange_screws(x0, y0):
            fastener("fast_plunger_nuts", (x, y, f1), -Z, 3, 10, grip=f1 - zp0, head="socket", nut=True, parent=SP)
    # carriage brackets: at y 33 up from the pocket into a T-nut in the long bar; at y 10 down from
    # the plate's top into a captive nut in the pocket
    pocket = zp0 - PLG_BRK_POCKET
    for x, y in L.PLG_BRACKET_HOLES:
        if abs(y) > 20:
            fastener("fast_plunger_brackets", (x, y, pocket), Z, 4, 20, grip=zp1 - pocket, head="socket",
                     tnut=X, tnut_off=-math.copysign(2.5, x), parent=SP)     # 3 mm from the bar's end
        else:
            fastener("fast_plunger_brackets", (x, y, zp1), -Z, 4, 20, grip=zp1 - pocket, head="socket",
                     nut=True, parent=SP)
    # D-shaft troughs: up through the outer wall; front pair to nuts on the plate, the pair at +/-32
    # into T-nuts in the long bars
    tz0, _ = _span("dshaft_trough_R")
    for sx in (-1, 1):
        for x, y in L.TROUGH_BOLTS:
            tn = abs(abs(y) - L.STIFF_LONG_Y) < 1
            fastener("fast_troughs", (sx * x, y, tz0), Z, 3, 25, grip=zp1 - tz0, head="socket",
                     nut=not tn, tnut=X if tn else None, parent=SP)
    # optical-endstop flags: countersunk up from under the tab (flush: the tab passes 1.5 mm over the
    # sensor at full eject), nuts on top of the plate
    for x, y in L.FLAG_HOLES:
        fastener("fast_flags", (x, y, zp0 - 3.0), Z, 3, 10, grip=3.0 + T, head="csk", nut=True, parent=SP)

    # ---- head: pipette-plate brackets, optical-endstop posts, drawer ledges
    zq0, zq1 = _span("pipette_plate")
    hb0, _ = _span("head_bracket_R")
    for x, y in L.HEAD_MOUNT_XY:                                 # up through the bracket block + plate
        fastener("fast_head_brackets", (x, y, zq0 - 20), Z, 4, 30, grip=23.0, head="socket", nut=True)
    for sx in (-1, 1):                                           # the foot up into the bar's bottom slot
        for y in (-20.0, 20.0):
            fastener("fast_head_brackets", (sx * (g["IX"] + 10), y, hb0), Z, 5, 12, grip=6.0, head="socket", tnut=Y,
                     head_washer=True)
    for x, y in L.SWITCH_POST_HOLES:                             # counterbores 6 mm over the plate
        fastener("fast_sensor_posts", (x, y, zq1 + 6), -Z, 3, 12, grip=6 + T, head="socket", nut=True)
    for x, y in L.SWITCH_POSTS:                                  # sensor ears, self-tapping into the post
        _, s1 = _span(f"plunger_optical_{'LR'[x > 0]}{'FB'[y > 0]}_sensor")
        for s_ in (-1, 1):
            fastener("fast_sensors", (x, y + s_ * OPT_EARS / 2, s1), -Z, 3, 8, grip=OPT_BODY[2], head="pan",
                     into=("plunger_optical",), min_thread=1.5)
    l0, _ = _span("cart_ledge_R")
    for sx in (-1, 1):
        for x, y in L.LEDGE_BOLTS:
            fastener("fast_ledges", (sx * x, y, l0), Z, 3, 14, grip=zq1 - l0, head="socket", nut=True)

    # ---- motors, bearings, tensioners, the lift home switch
    for x, y, zf, u, m in ((*LIFT_MOTOR_XY, zb1, -Z, "lift"), (*PLG_MOTOR_XY, zt0, Z, "plunger")):
        q = L.NEMA17_BOLTS / 2
        for sx in (-1, 1):
            for sy in (-1, 1):
                fastener("fast_motors", (x + sx * q, y + sy * q, zf), u, 3, 8, grip=T, head="socket",
                         into=(f"{m}_motor",), min_thread=4.0)
    for sx in (-1, 1):                                           # lift KFL08s hang under the base plate
        for s_ in (-1, 1):
            fastener("fast_kfl08", (sx * LIFT_X + s_ * L.KFL08_BOLTS / 2, 0, zb1), -Z, 4, 12, grip=T + 5, head="socket", nut=True)
    for x, y in L.PS_XY:                                         # plunger KFL08s on the top plate (turned 90 deg)
        for s_ in (-1, 1):
            fastener("fast_kfl08", (x, y + s_ * L.KFL08_BOLTS / 2, zt1 + 5), -Z, 4, 12, grip=T + 5, head="socket", nut=True)
    for nm, zbase, ztop, y in (("lift_tensioner_bracket", zb0, None, L.LIFT_IDLER_Y),
                               ("plunger_tensioner_bracket", zt0, None, L.PLG_IDLER_Y)):
        b0, b1 = _span(nm)
        for s_ in (-1, 1):
            fastener("fast_tensioners", (s_ * L.TENSIONER_HOLE_DX, y, b1), -Z, 3, 12, grip=b1 - zbase,
                     head="socket", nut=True)
    hx, hy = HOME_SW_XY
    hz0, _ = _span("lift_home_switch_body")                      # holder base top = switch bottom
    for s_ in (-1, 1):
        fastener("fast_home_switch", (hx + s_ * 14, hy, hz0), -Z, 3, 20, grip=hz0 - zb0, head="socket", nut=True)
        fastener("fast_home_switch", (hx + s_ * 4.75, hy - 8.0, hz0 + 3), Y, 2, 20, grip=16.0, head="socket", nut=True)

    # ---- control box: base plate into the bosses, pad into the bottom front bar, USB socket
    for x, y in CBOX_BOSSES:
        fastener("fast_control_box", (x, y, 0.0), Z, 3, 10, head="csk", into=("ScreenHousing",), min_thread=5.0)
    back = -(g["FY"] / 2 + T + CBOX_BACK_GAP)                   # box back wall, outer face
    for x in (-25.0, 25.0):
        fastener("fast_control_box", (x, back - 3.0, 10.0), Y, 5, 14, grip=(-g["FY"] / 2) - (back - 3.0),
                 head="socket", tnut=X)
    uy, uz = USB_PANEL_YZ
    ux0, _ = _span("usb_panel_socket_flange", 0)
    for s_ in (-1, 1):
        fastener("fast_control_box", (ux0, uy + s_ * USB_PANEL_EARS / 2, uz), X, 3, 12, grip=1.5 + 3.0,
                 head="socket", nut=True)

    # ---- cartridge: lock frame + plate into the grip's ears, handle, pad retainer to the carrier
    _, fr1 = _span("syringe_lock_frame")
    for x, y in L.FRAME_SCREWS:
        fastener("cartridge_fasteners", (x, y, fr1), -Z, 3, 14, grip=FRAME_T + T, head="pan",
                 into=("syringe_grip",), min_thread=5.0)
    _, cp1 = _span("cartridge_plate")
    for x, y in L.CART_HANDLE_SCREWS:
        fastener("cartridge_fasteners", (x, y, cp1), -Z, 3, 10, grip=T, head="pan",
                 into=("cartridge_handle",), min_thread=5.0)
    _, pr1 = _span("pad_retainer")
    for x, y in L.RETAINER_SCREWS:
        fastener("pad_retainer_screws", (x, y, pr1), -Z, 3, 6, grip=3.0, head="csk",
                 into=("plunger_carrier",), min_thread=2.5, parent=SP)

    # ---- make the objects
    if "Fasteners" not in bpy.data.collections:
        bpy.context.scene.collection.children.link(bpy.data.collections.new("Fasteners"))
    for joint, (bm, parent) in _FB.items():
        m = M["chrome"] if joint.endswith("brackets") else M["motor"]
        o = new_obj(joint, bm, "Fasteners", m)
        if parent:
            o.parent = obj[parent]
            o.matrix_parent_inverse = obj[parent].matrix_world.inverted()
    # D-shaft levers: an M3 x 6 cone-point set screw in the hub, into the dimple (turns with the lever)
    zc = dshaft_axis_z()
    r = L.DSHAFT_D / 2
    for sx in (-1, 1):
        lv = obj[f"dshaft_lever_{'LR'[sx > 0]}"]
        ym = -100.0 - LEVER_HUB[1] / 2 - 6.0
        bm = bmesh.new()
        _frustum(bm, (sx * L.DSHAFT_X, ym, zc - r + 1.0), (sx * L.DSHAFT_X, ym, zc - LEVER_HUB[0] - 0.5), 1.4, 1.4, seg=12)
        o = new_obj(f"dshaft_setscrew_{'LR'[sx > 0]}", bm, "Fasteners", M["motor"])
        bpy.context.view_layer.update()
        o.parent = lv
        o.matrix_parent_inverse = lv.matrix_world.inverted()
    for w in FAST_WARN:
        print("FASTENER", w)


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


# (frame, lift fraction, plunger fraction): the poses collision_report() samples (raise, aspirate,
# lower, raise, dispense, lower, eject)
KEYS = [(1, 0, 0), (28, 1, 0), (34, 1, 0), (58, 1, 1), (64, 1, 1), (90, 0, 1), (100, 0, 1),
        (126, 1, 1), (132, 1, 1), (156, 1, 0), (162, 1, 0), (188, 0, 0), (196, 0, 0)]
EJ_A = -EJECT_MM / ASPIRATE       # plunger fraction for the eject pose
KEYS += [(220, 0, EJ_A), (228, 0, EJ_A), (252, 0, 0), (260, 0, 0)]

DRAWER_OUT = 210.0                # cartridge pulled this far forward: its back edge well clear of the front posts


# ================================================================ labware and the full cycle
# Demo labware, all on the SBS footprint in the nest (parented to the platform) and loaded from the
# front over its lip: a tip rack, a 1-well reservoir, the 96-well plate and a waste tray. Whatever
# goes in while tips are on the head has to pass under them with the bed down (tip bottoms 139.3),
# so tips are ejected into the shallow tray, not back into the rack.
NEST_Z = LIFT0 + T + TRAY_H                   # nest base = labware bottom, bed down
SBS = (127.76, 85.48)
TIP_TOP = TIP_BOTTOM + 56.0
TIP_LOAD_MM = LIFT_TRAVEL - 3.9              # bed height that presses the nozzles into the rack's tips
RACK_DECK = (60.0, 39.0)                      # raised deck half sizes: inside the ejector rods (y >= 41.2)
RACK_H = (TIP_TOP - 4.0) - (NEST_Z + TIP_LOAD_MM)   # a tip rests where its collar is 5.5 wide, 4 mm below its top
TRAY_DEPTH = 30.0
LW_FLOOR = 1.5
TIP_FALL = TIP_BOTTOM - (NEST_Z + LW_FLOOR)   # ejected tips drop onto the tray floor (bed down)
TIP_FALL_FRAMES = 6
CYCLE_UL = 100.0                              # per channel
SYR_AREA = math.pi * (4.78 / 2) ** 2          # 1 mL syringe bore
CYCLE_STROKE = CYCLE_UL / SYR_AREA
WELL_R, WELL_DEPTH = 3.4, 10.9
RES_LIQ = 10.0                                # reservoir liquid depth
HOP, LW_OUT = 5.0, 300.0                      # labware lifts this much over the nest's lip; out = this far forward
LABWARE = {"tip_rack": "rack", "reservoir": "res", "well_plate_96": "plate", "waste_tray": "tray"}
LIQUIDS = ("tip_liquid_x96", "reservoir_liquid", "well_liquid_x96")
_LW_BASE = {}


def _tip_liquid_r(z):
    """Liquid radius z mm above the tip's bottom (inside the tip's taper)."""
    return 0.3 + 1.8 * z / 48.0


def _parent_keep(child, parent):
    bpy.context.view_layer.update()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()


def labware():
    """Build the demo labware, split the tips into 8 rows and add the liquids (bed down, drawer in)."""
    obj = bpy.data.objects
    M["liquid"] = g["mat"]("Liquid_Blue", (0.1, 0.35, 0.95, 1), 0, 0.05, 1.0, 0.55)
    M["rack"] = g["mat"]("TipRack_Blue", (0.1, 0.18, 0.42, 1), 0, 0.45)
    plat = obj["lift_platform"]
    z0 = NEST_Z
    hx, hy = SBS[0] / 2, SBS[1] / 2

    def shell(name, h, m):                    # open-top SBS box: 1.5 mm walls and floor
        o = box(name, (SBS[0], SBS[1], h), (0, 0, z0 + h / 2), "Bed", m)
        bm = bmesh.new()
        _block(bm, -hx + 1.5, hx - 1.5, -hy + 1.5, hy - 1.5, z0 + LW_FLOOR, z0 + h + 1)
        boolean(o, bm)
        return o

    # tip rack: a skirt with a 2 mm top, a raised deck, a hole per tip through both
    rk = box("tip_rack", (SBS[0], SBS[1], RACK_H - 4), (0, 0, z0 + (RACK_H - 4) / 2), "Bed", M["rack"])
    bm = bmesh.new()
    _block(bm, -hx + 1.5, hx - 1.5, -hy + 1.5, hy - 1.5, z0 - 1, z0 + RACK_H - 6)
    boolean(rk, bm)
    bm = bmesh.new()
    _block(bm, -RACK_DECK[0], RACK_DECK[0], -RACK_DECK[1], RACK_DECK[1], z0 + RACK_H - 4.2, z0 + RACK_H)
    boolean(rk, bm, 'UNION', self_intersect=True)
    bm = bmesh.new()
    for x, y in g["GRID"]:
        _cone(bm, 2.75, 2.75, z0 + RACK_H - 8, z0 + RACK_H + 1, seg=20, xy=(x, y))
    boolean(rk, bm)
    res = shell("reservoir", PLATE_H, M["white"])
    tray = shell("waste_tray", TRAY_DEPTH, M["pla_grey"])
    wp = obj["well_plate_96"]
    wtop = z0 + PLATE_H
    bm = bmesh.new()
    for x, y in g["GRID"]:
        _cone(bm, WELL_R, WELL_R, wtop - WELL_DEPTH, wtop + 1, seg=24, xy=(x, y))
    boolean(wp, bm)
    for o in (rk, res, tray):
        _parent_keep(o, plat)
    for n in LABWARE:
        _LW_BASE[n] = obj[n].location.copy()

    # liquids: reservoir slab and well columns scale up from their floors; the tips' liquid is a
    # shape key whose top ring slides up the taper (both ends on the same straight wall)
    bm = bmesh.new()
    _block(bm, -hx + 1.6, hx - 1.6, -hy + 1.6, hy - 1.6, 0, RES_LIQ)
    rl = new_obj("reservoir_liquid", bm, "Bed", M["liquid"], (0, 0, z0 + LW_FLOOR))
    _parent_keep(rl, res)
    well_h = CYCLE_UL / (math.pi * (WELL_R - 0.2) ** 2)
    bm = bmesh.new()
    for x, y in g["GRID"]:
        _cone(bm, WELL_R - 0.2, WELL_R - 0.2, 0, well_h, seg=20, xy=(x, y))
    wl = new_obj("well_liquid_x96", bm, "Bed", M["liquid"], (0, 0, wtop - WELL_DEPTH + 0.02))
    _parent_keep(wl, wp)
    h, v = 0.0, 0.0                                   # height of CYCLE_UL in the tip
    while v < CYCLE_UL:
        h += 0.05
        v += math.pi * _tip_liquid_r(h) ** 2 * 0.05
    bm = bmesh.new()
    tops, n = [], 16
    zb = TIP_BOTTOM + 0.4
    for x, y in g["GRID"]:
        ring = lambda z, r: [bm.verts.new((x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n), z))
                             for i in range(n)]
        lo, hi = ring(zb, _tip_liquid_r(0)), ring(zb + 0.05, _tip_liquid_r(0.05))
        for i in range(n):
            bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
        bm.faces.new(lo[::-1])
        bm.faces.new(hi)
        tops += [(v_, x, y, i) for i, v_ in enumerate(hi)]
    bm.verts.index_update()
    top_idx = [(v_.index, x, y, i) for v_, x, y, i in tops]
    tl = new_obj("tip_liquid_x96", bm, "Syringes", M["liquid"])
    tl.shape_key_add(name="Basis")
    key = tl.shape_key_add(name="fill")
    r = _tip_liquid_r(h)
    for vi, x, y, i in top_idx:
        key.data[vi].co = (x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n), zb + h)

    # tips: 8 rows (front to back), so the tilted ejector plate can strip them a row at a time
    for ri, ry in enumerate(sorted({y for _, y in g["GRID"]}), 1):
        bm = bmesh.new()
        for x, y in g["GRID"]:
            if y == ry:
                _cone(bm, 2.5, 3.0, TIP_TOP - 8, TIP_TOP, seg=24, xy=(x, y))
                _cone(bm, 0.4, 2.5, TIP_BOTTOM, TIP_TOP - 8, seg=24, xy=(x, y))
        o = new_obj(f"pipette_tips_row{ri}", bm, "Syringes", M["tip"])
        o["row_y"] = ry
        for p in o.data.polygons:
            p.use_smooth = True


def _lw_offset(s):
    """Labware slide: s 0 = seated in the nest, 1 = LW_OUT forward; it rises HOP over the lip first."""
    if s > 0.1:
        return -LW_OUT * (s - 0.1) / 0.9, HOP
    return 0.0, HOP * s / 0.1


# One step per row: (frames, changes, caption); each change eases in over the step. tips: where
# the tips are ("rack" on the bed, "head" on the nozzles, "eject" once the ejector takes them).
CYCLE = [
    (12, {}, "Empty head, empty bed"),
    (30, {"rack": 0.0}, "Load a full tip rack"),
    (30, {"lift": TIP_LOAD_MM}, "Bed up: the nozzles press into the tips"),
    (6, {"tips": "head"}, "Bed up: the nozzles press into the tips"),
    (30, {"lift": 0.0}, "Bed down: the tips stay on the nozzles"),
    (24, {"rack": 1.0}, "Swap the empty rack for a reservoir"),
    (24, {"res": 0.0}, "Swap the empty rack for a reservoir"),
    (30, {"lift": LIFT_TRAVEL}, "Bed up: tips into the liquid"),
    (36, {"plg": CYCLE_STROKE, "tipfill": 1.0, "res_level": RES_LIQ - 96 * CYCLE_UL / ((SBS[0] - 3.2) * (SBS[1] - 3.2))},
     "Aspirate 100 uL per channel"),
    (6, {}, "Aspirate 100 uL per channel"),
    (30, {"lift": 0.0}, "Bed down"),
    (24, {"res": 1.0}, "Swap the reservoir for a 96-well plate"),
    (24, {"plate": 0.0}, "Swap the reservoir for a 96-well plate"),
    (30, {"lift": LIFT_TRAVEL}, "Bed up: tips into the wells"),
    (36, {"plg": 0.0, "tipfill": 0.0, "wells": 1.0}, "Dispense"),
    (6, {}, "Dispense"),
    (30, {"lift": 0.0}, "Bed down"),
    (24, {"plate": 1.0}, "Swap the plate for a waste tray"),
    (24, {"tray": 0.0}, "Swap the plate for a waste tray"),
    (6, {"tips": "eject"}, "Eject: the plunger runs past home, the ejector strips the tips"),
    (36, {"plg": -EJECT_MM}, "Eject: the plunger runs past home, the ejector strips the tips"),
    (8, {}, "Eject: the plunger runs past home, the ejector strips the tips"),
    (24, {"plg": 0.0}, "Plunger back to home"),
    (24, {"tray": 1.0}, "Take the used tips away"),
    (12, {}, "Open the D-shaft levers"),
    (24, {"turn": 1.0}, "Open the D-shaft levers"),
    (6, {}, "Open the D-shaft levers"),
    (60, {"out": 1.0}, "Slide the syringe cartridge out"),
    (24, {}, "Slide the syringe cartridge out"),
]


def cycle_frames():
    """CYCLE expanded to one state per frame (smoothstep within each step), and (frame, caption)
    at each caption change."""
    st = dict(lift=0.0, plg=0.0, turn=0.0, out=0.0, rack=1.0, res=1.0, plate=1.0, tray=1.0,
              tipfill=0.0, wells=0.0, res_level=RES_LIQ, tips="rack")
    frames, caps = [], []
    for n, ch, cap in CYCLE:
        a, b = st, dict(st, **ch)
        if not caps or caps[-1][1] != cap:
            caps.append((len(frames) + 1, cap))
        for i in range(1, n + 1):
            s = i / n
            s = s * s * (3 - 2 * s)
            frames.append({k: (a[k] + (b[k] - a[k]) * s if isinstance(a[k], float) else b[k]) for k in a})
        st = b
    return frames, caps


def animate_cycle():
    """Key the whole demo, every frame: see CYCLE."""
    sc = bpy.context.scene
    obj = bpy.data.objects
    frames, _ = cycle_frames()
    lift_s, plg_s = spinners()
    mech = [obj["lift_platform"], obj["plunger_carriage"]] + lift_s + plg_s
    mech += [o for o in obj if o.name.startswith(("eject_rod_", "eject_plate", "eject_spring_"))]
    cart, levers = drawer_parts()
    lw = {n: obj[n] for n in LABWARE}
    rows = [o for o in obj if o.name.startswith("pipette_tips_row")]
    tl, rl, wl = (obj[n] for n in LIQUIDS)
    key = tl.data.shape_keys.key_blocks["fill"]
    for o in mech + cart + levers + list(lw.values()) + rows + [tl, rl, wl]:
        o.animation_data_clear()
    tl.data.shape_keys.animation_data_clear()
    released = {}
    for f, s in enumerate(frames, 1):
        pose(s["lift"], s["plg"])
        pose_drawer(s["turn"], s["out"])
        for n, o in lw.items():
            y, z = _lw_offset(s[LABWARE[n]])
            o.location = _LW_BASE[n] + Vector((0, y, z))
            o.hide_render = s[LABWARE[n]] > 0.999        # render only: viewport-hidden objects stop updating
        ry, rz = _lw_offset(s["rack"])
        ty, tz = _lw_offset(s["tray"])
        e = max(0.0, -s["plg"])
        df, db = max(0.0, e - EJ_GAP_F), max(0.0, e - EJ_GAP_B)
        for o in rows:
            if s["tips"] == "rack":
                o.location = (0, ry, s["lift"] - TIP_LOAD_MM + rz)
            elif s["tips"] == "head":
                o.location = (0, 0, 0)
            else:                                     # pushed by the tilted plate, then dropped into the tray
                push = df + (db - df) * (o["row_y"] + L.EJ_ROD_Y) / (2 * L.EJ_ROD_Y)
                if o.name not in released and push >= EJ_STROKE:
                    released[o.name] = f
                if o.name in released:
                    k = min(1.0, (f - released[o.name]) / TIP_FALL_FRAMES)
                    o.location = (0, ty, -(EJ_STROKE + (TIP_FALL - EJ_STROKE) * k * k) + s["lift"] + tz)
                else:
                    o.location = (0, 0, -push)
            o.hide_render = ((s["tips"] == "rack" and s["rack"] > 0.999) or
                             (s["tips"] == "eject" and s["tray"] > 0.999))
        key.value = s["tipfill"] ** (1 / 3)           # height goes as the cube root of the volume in a cone
        tl.hide_render = s["tipfill"] < 0.002
        rl.scale.z = s["res_level"] / RES_LIQ
        rl.hide_render = s["res"] > 0.999
        wl.scale.z = max(0.001, s["wells"])
        wl.hide_render = s["wells"] < 0.002 or s["plate"] > 0.999
        for o in mech:
            for p in ("location", "rotation_euler", "scale"):
                o.keyframe_insert(p, frame=f)
        for o in cart:
            o.keyframe_insert("delta_location", frame=f)
        for o in levers:
            o.keyframe_insert("delta_rotation_euler", frame=f)
        for o in list(lw.values()) + rows + [tl, rl, wl]:
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("scale", frame=f)
            o.keyframe_insert("hide_render", frame=f)
        key.keyframe_insert("value", frame=f)
    sc.frame_start, sc.frame_end, sc.render.fps = 1, len(frames), 24
    sc.frame_set(1)


def drawer_parts():
    obj = bpy.data.objects
    cart = [o for o in obj if o.type == 'MESH' and o.name.startswith(CARTRIDGE)]
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




def world_bvh(o):
    dg = bpy.context.evaluated_depsgraph_get()
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    mw = o.matrix_world
    t = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [p.vertices[:] for p in me.polygons])
    oe.to_mesh_clear()
    return t


def eject_clearance():
    """Gap from each tip cone's end down to the ejector plate's underside at full eject (EJECT_MM),
    per row front to back: the tips rest against the plate, so this is how far they end up clear."""
    p = bpy.data.objects["eject_plate"]
    pose(0, -EJECT_MM)
    bpy.context.view_layer.update()
    vs = [p.matrix_world @ v.co for v in p.data.vertices]
    gaps = [round(CONE_Z - CONE_LEN - min(v.z for v in vs if abs(v.y - y) < 4.0), 2)
            for y in sorted({y for _, y in g["GRID"]})]
    pose(0, 0)
    return gaps


def collision_report():
    """Check every mesh pair that can meet: moving groups vs everything at each keyframe, plus
    the new static drive parts vs the rest at rest. Intended contacts are whitelisted. Checked with
    the tips on the nozzles and the well plate in the nest (the other labware is out)."""
    obj = bpy.data.objects
    for o in obj:
        if o.name.startswith("pipette_tips_row"):
            o.location = (0, 0, 0)
    if _LW_BASE:
        obj["well_plate_96"].location = _LW_BASE["well_plate_96"]
    pose_drawer(0, 0)
    skip = ("LCD", "encoder") + tuple(n for n in LABWARE if n != "well_plate_96") + LIQUIDS
    meshes = [o for o in obj if o.type == 'MESH' and o.name != "Ground" and not o.name.startswith(skip)]
    def rig(o):
        while o.parent:
            o = o.parent
            if o.name in ("lift_platform", "plunger_carriage"):
                return o.name
        return None
    lift_g = {o.name for o in meshes if rig(o) == "lift_platform"}
    plg_g = {o.name for o in meshes if rig(o) == "plunger_carriage"}
    fast = {o.name for o in meshes if o.users_collection and o.users_collection[0].name == "Fasteners"} | \
           {n for n in ("inside_corner_brackets", "stiffener_corner_brackets") if n in obj}
    grp = lambda n: "lift" if n in lift_g else "plg" if n in plg_g else "static"
    new_static = {o.name for o in meshes if o.name.startswith(("lift_screw", "lift_pulley", "lift_belt", "lift_motor",
                  "KFL08", "lift_base", "plunger_screw", "plunger_pulley", "plunger_belt", "plunger_motor",
                  "lift_idler", "lift_tensioner", "lift_home_switch", "plunger_idler", "plunger_tensioner",
                  "ext_head", "head_bracket", "plunger_switch", "ScreenHousing", "control_box_base", "syringe_lock_frame", "usb_panel_socket", "eject_", "plunger_optical", "cartridge_plate", "syringe_grip", "top_plate",
                  "cart_ledge", "cart_spacer", "cart_detent", "cartridge_handle", "tip_cone"))}
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
               ("tip_cone", "syringe_barrels"), ("tip_cone", "pipette_tips"),   # on the nozzles, inside the (solid) tips
               ("plunger_optical", "pipette_plate"), ("plunger_optical", "plunger_optical"),
               ("cartridge_plate", "pipette_plate"), ("cartridge_plate", "syringe_barrels"),
               ("cartridge_plate", "syringe_lock_frame"), ("cartridge_plate", "syringe_grip"),
               ("cartridge_plate", "eject_spring"),
               ("eject_rod", "plunger_carrier"),
               ("top_plate", "ext_top"), ("top_plate", "post_"), ("top_plate", "angle_bracket"), ("KFL08_plunger", "top_plate"), ("plunger_motor", "top_plate"),
               ("plunger_tensioner", "top_plate"), ("plunger_idler", "top_plate"), ("plunger_idler", "plunger_tensioner"),
               ("plunger_screw", "top_plate"), ("cart_spacer", "pipette_plate"), ("cart_ledge", "cart_spacer"),
               ("cart_detent", "cart_ledge"), ("cartridge_handle", "cartridge_plate"), ("usb_panel_socket", "ScreenHousing"), ("usb_panel_socket", "usb_panel_socket"), ("syringe_lock_frame", "syringe_barrels"),
               ("syringe_lock_frame", "pipette_plate"), ("ScreenHousing", "LCD_2004"), ("ScreenHousing", "encoder"),
               ("fast_rails", "MGN9H_carriage"),     # the rail screws' heads sit in the rail, which the carriage wraps
               ("dshaft_setscrew", "dshaft")]         # bolts in slots
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
                if (na in fast or nb in fast) and grp(na) == grp(nb):
                    continue                              # a fastener in its own joint: see fasteners()
                if bv[na].overlap(bv[nb]):
                    hits.setdefault(f"{na} x {nb}", []).append((round(l * LIFT_TRAVEL, 1), round(a * ASPIRATE, 1)))
    pose(0, 0)
    return hits


if __name__ != "motor_lib":        # exec with this name to load functions only
    g["build"]()
    g["stage"]()
    belts = modify()
    fasteners()                      # every screw, bolt, nut and T-nut (rigs still at build positions)
    pose(0, 0)
    labware()
    animate_cycle()                  # the full demo on the timeline: tips on, aspirate, dispense, eject, cartridge out
summary = {
    "lift_travel_mm": round(LIFT_TRAVEL, 2),
    "lift_revs": round(LIFT_TRAVEL / LIFT_LEAD, 1),
    "wellplate_top_mm": [round(LIFT0 + T + TRAY_H + PLATE_H, 1), round(LIFT0 + T + TRAY_H + PLATE_H + LIFT_TRAVEL, 1)],
    "tip_bottom_mm": round(TIP_BOTTOM, 1),
    "tip_eject_clear_mm": eject_clearance() if "eject_plate" in bpy.data.objects else None,
}
