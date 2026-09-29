"""Variant: fixed head, motorized lead-screw bed lift, belt-synced plunger drive.

Builds the baseline (build_pipette.py) and then modifies it:
  * lever mechanism, fixed bed and the bed ring's front/back members are removed
  * LIFT: one NEMA17 drives two T8 screws (x = +/-72, clear of the tray) through a closed GT2 loop.
    Screws run in KFL08 flange bearings under a steel base plate hung beneath the bed-ring side
    members; the motor hangs below that plate. Brass nuts under the platform, which rides the same
    four MGN9H rails as before. Positions are programmable per labware; the screw holds position.
  * PLUNGER: the four per-screw steppers become one NEMA17 + closed GT2 loop around four T8 screws
    moved out to (+/-65, +/-58.9) so the belt passes outside the 96-syringe array. With the head
    fixed, motor, bearings and pulleys all sit on the stationary pipette plate; only the nuts ride
    on the plunger plate. Mechanically synced -> the plate cannot rack if a step is missed.
    Accuracy upgrades: T8x2 plunger screws with anti-backlash nuts (spring + second nut), a 2020
    stiffening frame on the plunger holder plate so the plate bends less under stopper friction,
    and a 48 mm (~0.5 N m class) motor so one motor matches the original four's thrust.
  * both belts have a smooth-idler tensioner on a slotted printed bracket; the lift homes onto a
    micro switch pressed by the platform underside at the bottom of travel
  * frees two of the CNC shield's four driver slots (X = plunger, Y = lift)
Run: blender --python 04_Blender/variant_motor_lift.py  (or open it in Blender's Text Editor and Run Script)
"""
import bpy, bmesh, math, os
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

D = math.radians
M = None
box, cyl, dxf_part, dup, new_obj = g["box"], g["cyl"], g["dxf_part"], g["dup"], g["new_obj"]
IF_X, IX, PY, T, P, FH = g["IF_X"], g["IX"], g["PY"], g["T"], g["P"], g["FH"]
PLG_MID, PLG_TOP, BED_RECT_Z = g["PLG_MID"], g["PLG_TOP"], g["BED_RECT_Z"]

# ---------------------------------------------------------------- parameters
PULLEY_R = 6.37                   # GT2 20T pitch radius
# lift
LIFT_X = 72.0                     # screws at (+/-72, 0): outside the tray (+/-63.9)
LIFT_MOTOR_XY = (0.0, 36.0)
BASE_Z = BED_RECT_Z - 10 - T      # base plate top = underside of bed-ring side members (52..55)
LIFT_PLUS = BASE_Z + T + 1        # pulley stack starts 1 mm above the base plate
LIFT0 = 78.0                      # platform underside at the bottom of travel
TRAY_H, PLATE_H = 15.0, 14.4
TIP_DEPTH = 9.0                   # tips this far into the wells at the top of travel
LIFT_TRAVEL = (P - 112 + TIP_DEPTH) - (LIFT0 + T + TRAY_H + PLATE_H)
LIFT_LEAD = 2.0                   # T8x2 on the lift: force + self-locking
# plunger
PS_XY = [(sx * 65.0, sy * 58.9) for sy in (-1, 1) for sx in (-1, 1)]
PLG_MOTOR_XY = (0.0, -85.0)
SWITCH_TOP = P + 39 + 11.5        # limit-switch lever tops on the pipette-plate corner blocks
PLG_REST = (SWITCH_TOP + 0.5) - (PLG_MID - T / 2)   # home = plate just off the switches (firmware homes onto them)
ASPIRATE = 12.0                   # animation stroke (~215 uL in a 4.78 mm-bore 1 mL syringe)
PLG_LEAD = 2.0                    # T8x2: 4x the resolution and thrust of the original T8x8
# tensioners / homing
IDLER_R = 8.8                     # belt pitch-line radius on a 16 mm smooth idler (back-side wrap)
TENSION_TAKEUP = 16.0             # idler deflects the run this far; slot gives +/-6 mm.
                                  # (take-up ~ deflection^2 / span, so a shallow idler takes up almost nothing)
HOME_SW_XY = (-40.0, -35.0)       # lift home switch: under the platform, clear of belt + nuts
HOME_OVERTRAVEL = 0.8             # lever deflection when the platform is home


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


def tensioner(prefix, x, y_idler, z_base, height, coll, through=None):
    """Printed bracket with a 12 mm adjustment slot along y: the idler's shoulder bolt clamps
    anywhere in the slot. The model shows it at TENSION_TAKEUP (mid-slot)."""
    br = box(prefix + "_bracket", (30, 34, height), (x, y_idler, z_base + height / 2), coll, M["pla"], bevel=1.0)
    bm = bmesh.new()
    slot_prism(bm, x, y_idler, 17.2, 5.2, z_base - 5, z_base + height + 5)
    cut = new_obj(prefix + "_slotcut", bm, coll)
    mod = br.modifiers.new("slot", 'BOOLEAN')
    mod.object, mod.operation, mod.solver = cut, 'DIFFERENCE', 'EXACT'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    baked = bpy.data.meshes.new_from_object(br.evaluated_get(dg))
    br.modifiers.clear()
    br.data = baked
    bpy.data.objects.remove(cut)
    if through is not None:           # matching slot in the plate below so the bolt + nut can slide
        bm = bmesh.new()
        slot_prism(bm, x, y_idler, 17.2, 5.2, -500, 500)
        cut = new_obj(prefix + "_plateslot", bm, coll)
        mod = through.modifiers.new("slot", 'BOOLEAN')
        mod.object, mod.operation, mod.solver = cut, 'DIFFERENCE', 'EXACT'
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        mats = list(through.data.materials)
        through.data = bpy.data.meshes.new_from_object(through.evaluated_get(dg))
        through.modifiers.clear()
        if not through.data.materials:
            for m in mats:
                through.data.materials.append(m)
        bpy.data.objects.remove(cut)
    return br


def microswitch(prefix, x, y, z_base, lever_top, coll):
    """Printed holder + micro limit switch, lever tip at lever_top."""
    sw_h, lev = 10.0, 1.0
    hold_h = lever_top - lev - 0.5 - sw_h - z_base
    box(prefix + "_holder", (26, 14, hold_h), (x, y, z_base + hold_h / 2), coll, M["pla"], bevel=0.8)
    zs = z_base + hold_h
    box(prefix + "_body", (20, 6.5, sw_h), (x, y, zs + sw_h / 2), coll, M["pla_grey"])
    box(prefix + "_lever", (18, 4, lev), (x + 1, y, lever_top - lev / 2), coll, M["chrome"])


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
    # pipette plate fixed to the posts
    for o in [o for o in obj if o.name.startswith("MGN9H_carriage_low")]:
        o.name = o.name.replace("MGN9H_carriage_low", "head_fixed_mount")
        o.data.materials.clear()
        o.data.materials.append(M["pla"])

    # ---------------- LIFT
    box("lift_base_plate", (2 * (IX + 20), 120, T), (0, 0, BASE_Z + T / 2), "Frame", M["steel"], bevel=0.5)
    drill(obj["lift_base_plate"], [(-LIFT_X, 0), (LIFT_X, 0)], 4.5)
    drill(obj["lift_base_plate"], [LIFT_MOTOR_XY], 11.5)
    nema17("lift_motor", *LIFT_MOTOR_XY, BASE_Z, True, "Bed")
    obj["lift_motor_shaft"].location.z = BASE_Z + 9
    for sx in (-1, 1):
        tag = "LR"[sx > 0]
        kfl08(f"KFL08_lift_{tag}", sx * LIFT_X, 0, BASE_Z, True, "Bed")
        cyl(f"lift_screw_{tag}", 4, 118, (sx * LIFT_X, 0, BASE_Z - 14 + 59), "Bed", M["chrome"], seg=16)
        pulley(f"lift_pulley_{tag}", sx * LIFT_X, 0, LIFT_PLUS, "Bed")
    pulley("lift_pulley_motor", *LIFT_MOTOR_XY, LIFT_PLUS, "Bed")
    # tensioner: idler pushes the long lower run (between the screws) inward (+y)
    li_y = -(PULLEY_R + IDLER_R) + TENSION_TAKEUP
    idler("lift_idler", 0, li_y, LIFT_PLUS, "Bed")
    tensioner("lift_tensioner", 0, li_y, BASE_Z + T, LIFT_PLUS + 6 - (BASE_Z + T) - 0.5, "Bed",
              through=obj["lift_base_plate"])
    lift_seq = [(-LIFT_X, 0, PULLEY_R), (0, li_y, -IDLER_R), (LIFT_X, 0, PULLEY_R), (*LIFT_MOTOR_XY, PULLEY_R)]
    lift_belt = belt("lift_belt", lift_seq, LIFT_PLUS + 11, "Bed")
    # homing: the platform underside presses the lever at the bottom of travel
    microswitch("lift_home_switch", *HOME_SW_XY, BASE_Z + T, LIFT0 + HOME_OVERTRAVEL, "Bed")

    # platform (+ carriages, interface plates, nuts, tray, plate)
    lp = box("lift_plate", (160, 200, T), (0, 0, LIFT0 + T / 2), "Bed", M["steel"], bevel=0.5)
    drill(lp, [(-LIFT_X, 0), (LIFT_X, 0)], 5.5)
    members = [lp]
    src = dxf_part("interface_plate_high.DXF", "lift_interface", T, "Bed", M["steel"])
    zc = LIFT0 + T / 2 - 10
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        o = src if i == 0 else dup(src, f"lift_interface.{i:03d}")
        g["frame_to"](o, -sy * Vector((0, 1, 0)), Vector((0, 0, 1)), (-10, 0), (sx * IF_X, sy * PY, zc))
        members += [o, box(f"MGN9H_carriage_lift_{'LR'[sx > 0]}{'FB'[sy > 0]}", (6.5, 20, 39.9),
                           (sx * (IX - 6.75), sy * PY, zc + 4), "Frame", M["chrome"], bevel=0.5)]
    for sx in (-1, 1):
        tag = "LR"[sx > 0]
        members.append(cyl(f"lift_nut_flange_{tag}", 11, 3.5, (sx * LIFT_X, 0, LIFT0 - 1.75), "Bed", M["brass"]))
        members.append(cyl(f"lift_nut_body_{tag}", 5.1, 15, (sx * LIFT_X, 0, LIFT0 + 7.5), "Bed", M["brass"]))
    tray, wp = obj["vertical_tray"], obj["well_plate_96"]
    tray.location.z = LIFT0 + T
    wp.location.z = LIFT0 + T + TRAY_H + PLATE_H / 2
    members += [tray, wp]
    rig_empty("lift_platform", "Bed", members)

    # ---------------- PLUNGER drive on the fixed pipette plate
    pip, plg, hold = obj["pipette_plate"], obj["plunger_plate"], obj["plunger_holder_plate"]
    drill(pip, PS_XY, 4.5)
    drill(pip, [PLG_MOTOR_XY], 11.5)
    drill(plg, PS_XY, 5.5)
    drill(hold, PS_XY, 6.0)
    for i, (x, y) in enumerate(PS_XY, 1):
        kfl08(f"KFL08_plunger_{i}", x, y, P - T, True, "Motors", rot=D(90))   # flange along y: clears interface plates
        cyl(f"plunger_screw_{i}", 4, FH - 35 - (P - 16), (x, y, (FH - 35 + P - 16) / 2), "Motors", M["chrome"], seg=16)
        pulley(f"plunger_pulley_{i}", x, y, P + 1, "Motors")
    nema17("plunger_motor", *PLG_MOTOR_XY, P - T, True, "Motors", length=48.0)
    obj["plunger_motor_shaft"].location.z = P + 6
    pulley("plunger_pulley_motor", *PLG_MOTOR_XY, P + 1, "Motors")
    # tensioner: idler pushes the back run (behind the array) inward (-y)
    pi_y = 58.9 + PULLEY_R + IDLER_R - TENSION_TAKEUP
    idler("plunger_idler", 0, pi_y, P + 1, "Motors")
    tensioner("plunger_tensioner", 0, pi_y, P, 5.5, "Motors", through=pip)
    lf, rf, lb, rb = PS_XY          # PS_XY order: LF, RF, LB, RB
    plg_seq = [(*lf, PULLEY_R), (*PLG_MOTOR_XY, PULLEY_R), (*rf, PULLEY_R), (*rb, PULLEY_R),
               (0, pi_y, -IDLER_R), (*lb, PULLEY_R)]
    plg_belt = belt("plunger_belt", plg_seq, P + 11, "Motors")

    # moving plunger carriage: plate, holder, plungers, corner blocks, carriages, nuts, stiffener
    zb = PLG_MID - T / 2
    members = [plg, hold, obj["plungers_x96"]]
    members += [o for o in obj if o.name.startswith(("LimitSwitch_holder_A", "interface_plate_high",
                                                      "MGN9H_carriage_high"))]
    for i, (x, y) in enumerate(PS_XY, 1):
        # anti-backlash T8 nut: flange nut + preload spring + second nut, hanging under the plate
        members.append(cyl(f"plunger_nut_flange_{i}", 11, 3.5, (x, y, zb - 1.75), "Motors", M["brass"]))
        members.append(cyl(f"plunger_nut_body_{i}", 5.1, 16, (x, y, zb + 8), "Motors", M["brass"]))
        members.append(spring(f"plunger_nut_spring_{i}", x, y, zb - 11.5, zb - 3.5, 6.0, 0.6, 4, "Motors", M["chrome"]))
        members.append(cyl(f"plunger_nut_lower_{i}", 7.0, 10, (x, y, zb - 16.5), "Motors", M["brass"], seg=6))
    # 2020 stiffening frame on the holder plate, around the syringe array and inside the screws:
    # two bars along x carry the load toward the screw rows, two short bars close the frame.
    zf = g["HOLD_TOP"] + 10
    for sy in (-1, 1):
        members.append(box(f"plunger_stiffener_{'FB'[sy > 0]}", (150, 20, 20), (0, sy * 42, zf), "Head", M["ext"], bevel=1.0))
    for sx in (-1, 1):
        members.append(box(f"plunger_stiffener_{'LR'[sx > 0]}", (20, 64, 20), (sx * 48, 0, zf), "Head", M["ext"], bevel=1.0))
    rig_empty("plunger_carriage", "Head", members)
    def span(seq, idx, sign):         # belt length with the idler at each end of its slot
        out = []
        for take in (TENSION_TAKEUP - 6, TENSION_TAKEUP + 6):
            q = list(seq)
            cx, cy, r = q[idx]
            q[idx] = (cx, cy + sign * (take - TENSION_TAKEUP), r)
            out.append(round(belt_route(q)[1], 1))
        return out
    return {"lift_belt_mm": round(lift_belt, 1), "plunger_belt_mm": round(plg_belt, 1),
            "lift_belt_range": span(lift_seq, 1, +1), "plunger_belt_range": span(plg_seq, 4, -1)}


# ================================================================ motion
def spinners():
    obj = bpy.data.objects
    lift = [o for o in obj if o.name.startswith(("lift_screw_", "lift_pulley_"))]
    plg = [o for o in obj if o.name.startswith(("plunger_screw_", "plunger_pulley_"))]
    return lift, plg


def pose(lift_mm, plg_mm):
    obj = bpy.data.objects
    obj["lift_platform"].location.z = lift_mm
    obj["plunger_carriage"].location.z = PLG_REST + plg_mm
    lift, plg = spinners()
    for o in lift:
        o.rotation_euler.z = D(360) * lift_mm / LIFT_LEAD
    for o in plg:
        o.rotation_euler.z = D(360) * (PLG_REST + plg_mm) / PLG_LEAD


# (frame, lift mm, plunger mm): raise -> aspirate -> lower -> raise -> dispense -> lower
KEYS = [(1, 0, 0), (28, 1, 0), (34, 1, 0), (58, 1, 1), (64, 1, 1), (90, 0, 1), (100, 0, 1),
        (126, 1, 1), (132, 1, 1), (156, 1, 0), (162, 1, 0), (188, 0, 0), (196, 0, 0)]


def animate():
    sc = bpy.context.scene
    lift, plg = spinners()
    movers = [bpy.data.objects["lift_platform"], bpy.data.objects["plunger_carriage"]] + lift + plg
    for o in movers:
        o.animation_data_clear()
    for f, l, a in KEYS:
        pose(l * LIFT_TRAVEL, a * ASPIRATE)
        for o in movers:
            o.keyframe_insert("location", frame=f)
            o.keyframe_insert("rotation_euler", frame=f)
    sc.frame_start, sc.frame_end, sc.render.fps = 1, KEYS[-1][0], 24
    sc.frame_set(1)


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
                  "lift_idler", "lift_tensioner", "lift_home_switch", "plunger_idler", "plunger_tensioner"))}
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
               ("lift_home_switch_lever", "lift_plate")]   # the platform presses the lever at home
    ok = lambda a, b: any((a.startswith(p) and b.startswith(q)) or (a.startswith(q) and b.startswith(p)) for p, q in allowed)
    hits = {}
    samples = sorted({(l, a) for _, l, a in KEYS} | {(0.5, 0), (0.5, 1), (1, 0.5), (0, 0.5)})
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
summary = {
    "lift_travel_mm": round(LIFT_TRAVEL, 2),
    "lift_revs": round(LIFT_TRAVEL / LIFT_LEAD, 1),
    "wellplate_top_mm": [round(LIFT0 + T + TRAY_H + PLATE_H, 1), round(LIFT0 + T + TRAY_H + PLATE_H + LIFT_TRAVEL, 1)],
    "tip_bottom_mm": round(P - 112, 1),
}
