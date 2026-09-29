"""Variant: fixed pipette head, lever raises the bed.

Builds the baseline (build_pipette.py) and then modifies it:
  * pipette plate is fixed to the posts (its rail carriages become printed fixed mounts);
    the plunger plate still rides the upper carriages, driven by the 4 steppers
  * bed_left/right + the bed ring's front/back members are removed; a steel lift platform
    carrying the tray + well plate rides the lower part of the same 4 rails
  * the geared arms (shortened to 65 mm) drive the platform through 4 short 47 mm links, laid out as
    a toggle: at the top of travel arm and link go collinear, so force multiplication climbs steeply
    exactly where tips are pressed on. The lever runs 1.5 deg over center onto a hard stop, so the
    raised bed locks itself. Each labware adapter (tray, tip-rack riser) is sized so its engagement
    point is this one repeatable top position.
  * the handle (lengthened to a 250 mm grip radius) moves to the back shaft, extended through the
    RIGHT face: the back shaft counter-rotates, so pushing the handle DOWN raises and locks the bed;
    lifting it releases the toggle and the bed drops
Run: blender --python 04_Blender/variant_raise_bed.py  (or open it in Blender's Text Editor and Run Script)
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
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))
M = None
box, frame_to, dxf_part, dup = g["box"], g["frame_to"], g["dxf_part"], g["dup"]
IF_X, IX, PY, T = g["IF_X"], g["IX"], g["PY"], g["T"]
SHAFT_Y, SHAFT_Z, ARM_L, P = g["SHAFT_Y"], g["SHAFT_Z"], g["ARM_L"], g["P"]
ARM_X, LINK_X = IF_X, IF_X - 3

# ---------------------------------------------------------------- lift geometry (toggle)
PIN_Y = 96.0          # platform hinge pins (y), just inside the posts
HINGE_H = 6.0         # hinge block: pin sits 6 mm below the platform plate
TRAY_H = 15.0         # vertical_tray.STL thickness
PLATE_H = 14.4
STACK = HINGE_H + T + TRAY_H                 # pin -> tray top (= well-plate base)
Z_TDC = (P - 112 + 9) - STACK - PLATE_H      # pin height that puts the tips 9 mm into the wells
ARM_A = 65.0                                 # shortened arm (pivot -> pin); stock lever_cutout is 89
ARM_SHIFT = ARM_L - ARM_A                    # cut the stock arm's straight section by this much
_R = math.hypot(PIN_Y - SHAFT_Y, Z_TDC - SHAFT_Z)
LINK2 = _R - ARM_A                           # arm + link collinear at the top -> toggle
TH_TDC = math.atan2(Z_TDC - SHAFT_Z, PIN_Y - SHAFT_Y)
TH_HIGH = TH_TDC + D(1.5)                    # over center onto the hard stop: self-locking
TH_LOW = D(-11)                              # arm tip stays clear of the bottom ring
HANDLE_R = 250.0                             # grip-center radius (stock bar gives 189)
HANDLE_EXT = HANDLE_R - 189.0                # lengthen the stock handle bar's straight section
HANDLE_X = IX + 20 + T + 8.5                 # outside the RIGHT face; 15 mm grip clears posts + brackets
HANDLE_H_END = D(0)                          # handle level when locked (clears the bench)
HANDLE_H0 = HANDLE_H_END + (TH_HIGH - TH_LOW)


def tip_of(th, sy):
    return Vector((0, sy * (SHAFT_Y + ARM_A * math.cos(th)), SHAFT_Z + ARM_A * math.sin(th)))


def pin_z(th):
    t = tip_of(th, 1)
    return t.z + math.sqrt(max(0.0, LINK2 ** 2 - (PIN_Y - t.y) ** 2))


def mech_adv(th):
    """Force at the platform per unit force at the grip (virtual work, frictionless)."""
    h = 1e-5
    return HANDLE_R / ((pin_z(th + h) - pin_z(th - h)) / (2 * h))


def stadium(name, c2c, w, t, coll, m):
    """Laser-cut link: slot-ended bar, local X along the link, holes' centers at +/-c2c/2."""
    r, h = w / 2, c2c / 2
    pts = [(h + r * math.cos(D(a)), r * math.sin(D(a))) for a in range(-90, 91, 15)] + \
          [(-h + r * math.cos(D(a)), r * math.sin(D(a))) for a in range(90, 271, 15)]
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x, y, -t / 2)) for x, y in pts])
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, verts=[v for v in ext['geom'] if isinstance(v, bmesh.types.BMVert)], vec=(0, 0, t))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return g["new_obj"](name, bm, coll, m)


def modify():
    global M
    M = g["materials"]()
    obj = bpy.data.objects
    # -- remove what the new layout replaces
    for n in ["bed_left", "bed_right", "ext_bed_F", "ext_bed_B", "lever_handle_bar", "lever_handle", "square_shaft_ext_front",
              "square_shaft.001", "lever_arm", "lever_arm.001", "lever_arm_offset", "lever_arm_offset.001"] + [o.name for o in obj if o.name.startswith(("linkage", "MGN9H_rail_"))]:
        if n in obj:
            obj.remove(obj[n])

    # -- rails now run from just above the bottom ring to the top ring
    r0, r1 = 22.0, g["FH"] - 25
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(f"MGN9H_rail_{'LR'[sx > 0]}{'FB'[sy > 0]}", (6.5, 9, r1 - r0),
                (sx * (IX - 3.25), sy * PY, (r0 + r1) / 2), "Frame", M["chrome"], bevel=0.3)

    # -- pipette plate is now fixed: its carriages become printed clamp blocks on the posts
    for o in [o for o in obj if o.name.startswith("MGN9H_carriage_low")]:
        o.name = o.name.replace("MGN9H_carriage_low", "head_fixed_mount")
        o.data.materials.clear()
        o.data.materials.append(M["pla"])

    # -- shortened gear-arms: move the tip end of the stock cut inward (straight section only)
    shorten = lambda x, y: (x - ARM_SHIFT, y) if x > 0 else (x, y)
    for src_dxf, n in (("lever_cutout.DXF", "lever_arm"), ("lever_cutout_offset.DXF", "lever_arm_offset")):
        dup(dxf_part(src_dxf, n, T, "Lever", M["steel"], xform=shorten), n + ".001")

    # -- back shaft extended through the right face for the external handle
    box("square_shaft_back_long", (HANDLE_X + 6 + 91.2, 10, 10),
        ((HANDLE_X + 6 - 91.2) / 2, SHAFT_Y, SHAFT_Z), "Lever", M["chrome"])
    # -- printed hard stop outboard of the right-face bracket: the bar lands on it just past center
    box("handle_stop", (HANDLE_X + 4 - (IX + 23.2), 20, 32.2),
        ((HANDLE_X + 4 + IX + 23.2) / 2, SHAFT_Y - 80, 16.1), "Lever", M["pla"], bevel=1.0)

    # -- lift platform (an Empty carries everything that rises)
    rig = obj.new("lift_platform", None)
    bpy.data.collections["Bed"].objects.link(rig)
    rig.empty_display_type, rig.empty_display_size = 'ARROWS', 40
    z0 = pin_z(TH_LOW)
    rig.location = (0, 0, z0)
    kids = []
    kids.append(box("lift_plate", (160, 200, T), (0, 0, z0 + HINGE_H + T / 2), "Bed", M["steel"], bevel=0.5))
    for sx in (-1, 1):
        for sy in (-1, 1):
            kids.append(box(f"lift_hinge_{'LR'[sx > 0]}{'FB'[sy > 0]}", (6.6, 12, 9),
                            (sx * (LINK_X - 1.5 - 3.3), sy * PIN_Y, z0 + 1.5), "Bed", M["pla"]))
    src = dxf_part("interface_plate_high.DXF", "lift_interface", T, "Bed", M["steel"])
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        o = src if i == 0 else dup(src, f"lift_interface.{i:03d}")
        zc = z0 + HINGE_H + T / 2 - 10
        frame_to(o, -sy * Y, Z, (-10, 0), (sx * IF_X, sy * PY, zc))
        kids.append(o)
        kids.append(box(f"MGN9H_carriage_lift_{'LR'[sx > 0]}{'FB'[sy > 0]}", (6.5, 20, 39.9),
                        (sx * (IX - 6.75), sy * PY, zc + 4), "Frame", M["chrome"], bevel=0.5))
    tray, wp = obj["vertical_tray"], obj["well_plate_96"]
    tray.location.z = z0 + STACK - TRAY_H
    wp.location.z = z0 + STACK + PLATE_H / 2
    kids += [tray, wp]
    bpy.context.view_layer.update()
    for k in kids:                      # parent with the offsets expressed relative to the rig
        mb = k.matrix_basis.copy()
        k.parent = rig
        k.matrix_parent_inverse = Matrix.Identity(4)
        k.matrix_basis = Matrix.Translation((0, 0, -z0)) @ mb

    # -- 4 short links
    for sx in (-1, 1):
        for sy in (-1, 1):
            stadium(f"lift_link_{'LR'[sx > 0]}{'FB'[sy > 0]}", LINK2, 10, T, "Lever", M["steel"])

    # -- external handle on the back shaft + grip
    lengthen = lambda x, y: (x + HANDLE_EXT, y) if x > 100 else (x, y)
    hb = dxf_part("lever_cutout_long.DXF", "lever_handle_bar", T, "Lever", M["steel"], xform=lengthen)
    g["seat_grip"](g["import_stl"]("lever_handle.STL", "Lever", M["pla"]), hb, end_x=144.5 + HANDLE_EXT)


def pose(th):
    """Place every moving part for arm angle th (radians)."""
    obj = bpy.data.objects
    names = {-1: ["lever_arm", "lever_arm.001"], 1: ["lever_arm_offset", "lever_arm_offset.001"]}
    for sy in (-1, 1):
        d = Vector((0, sy * math.cos(th), math.sin(th)))
        for sx, n in zip((-1, 1), names[sy]):
            frame_to(obj[n], d, Vector((0, -d.z, d.y)), (-44.5, 0), (sx * ARM_X, sy * SHAFT_Y, SHAFT_Z))
            tip = tip_of(th, sy) + Vector((sx * LINK_X, 0, 0))
            pin = Vector((sx * LINK_X, sy * PIN_Y, pin_z(th)))
            u = (pin - tip).normalized()
            frame_to(obj[f"lift_link_{'LR'[sx > 0]}{'FB'[sy > 0]}"], u, Vector((0, -u.z, u.y)), (-LINK2 / 2, 0), tip)
    obj["lift_platform"].location.z = pin_z(th)
    # shafts: front turns with -th, back with +th (meshing gears)
    frame_to(obj["square_shaft"], Matrix.Rotation(-(th - TH_LOW), 3, 'X') @ Y, X, (0, 91.2),
             (0, -SHAFT_Y, SHAFT_Z))
    obj["square_shaft_back_long"].rotation_euler = (th - TH_LOW, 0, 0)
    # handle rides the back shaft: elevation falls as the arms rise
    h = HANDLE_H0 - (th - TH_LOW)
    hd = Vector((0, -math.cos(h), math.sin(h)))
    frame_to(obj["lever_handle_bar"], hd, Vector((0, -hd.z, hd.y)), (-44.5, 0), (HANDLE_X, SHAFT_Y, SHAFT_Z))


def world_bvh(o):
    dg = bpy.context.evaluated_depsgraph_get()
    oe = o.evaluated_get(dg)
    me = oe.to_mesh()
    mw = o.matrix_world
    bvh = BVHTree.FromPolygons([mw @ v.co for v in me.vertices], [p.vertices[:] for p in me.polygons])
    oe.to_mesh_clear()
    return bvh


def collision_report(samples=9):
    obj = bpy.data.objects
    moving = [o for o in obj if o.type == 'MESH' and (
        o.name.startswith(("lever_arm", "lift_", "lever_handle", "square_shaft", "MGN9H_carriage_lift"))
        or o.name in ("vertical_tray", "well_plate_96"))]
    static = [o for o in obj if o.type == 'MESH' and o not in moving and o.name != "Ground"
              and not o.name.startswith(("LCD", "encoder"))]
    # expected contacts: pins/bearings/carriages that are meant to touch
    ok = lambda a, b: any(sorted([a, b])[0].startswith(p) and sorted([a, b])[1].startswith(q) or
                          sorted([a, b])[1].startswith(p) and sorted([a, b])[0].startswith(q)
                          for p, q in (("MGN9H_carriage_lift", "MGN9H_rail"),
                                       ("MGN9H_carriage_lift", "lift_interface"),
                                       ("square_shaft", "bearing"), ("lever_arm", "square_shaft"),
                                       ("lever_handle_bar", "square_shaft")))
    hits = {}
    for k in range(samples):
        th = TH_LOW + (TH_HIGH - TH_LOW) * k / (samples - 1)
        pose(th)
        bpy.context.view_layer.update()
        mv = {o.name: world_bvh(o) for o in moving}
        st = {o.name: world_bvh(o) for o in static}
        for a, ba in mv.items():
            for b, bb in st.items():
                if not ok(a, b) and ba.overlap(bb):
                    hits.setdefault((a, b), []).append(round(math.degrees(th), 1))
    pose(TH_LOW)
    return {f"{a} x {b}": v for (a, b), v in hits.items()}


def animate(up=40, hold=16, down=40):
    sc = bpy.context.scene
    obj = bpy.data.objects
    movers = [n for n in ("lever_arm", "lever_arm.001", "lever_arm_offset", "lever_arm_offset.001",
                          "square_shaft", "square_shaft_back_long", "lever_handle_bar", "lift_platform")] + \
             [o.name for o in obj if o.name.startswith("lift_link_")]
    for n in movers:
        obj[n].rotation_mode = 'QUATERNION'
        obj[n].animation_data_clear()
    ease = lambda s: 0.5 - 0.5 * math.cos(math.pi * s)
    frames = [(f, ease(f / up)) for f in range(up + 1)] + \
             [(up + f, 1.0) for f in range(1, hold + 1)] + \
             [(up + hold + f, 1 - ease(f / down)) for f in range(1, down + 1)]
    for f, s in frames:
        pose(TH_LOW + (TH_HIGH - TH_LOW) * s)
        for n in movers:
            o = obj[n]
            o.rotation_quaternion = o.matrix_basis.to_quaternion()
            o.keyframe_insert("location", frame=f + 1)
            o.keyframe_insert("rotation_quaternion", frame=f + 1)
    sc.frame_start, sc.frame_end = 1, up + hold + down + 1
    sc.render.fps = 24
    sc.frame_set(1)


if __name__ != "variant_lib":        # exec with this name to load functions only
    g["build"]()
    g["stage"]()
    modify()
    pose(TH_LOW)
    animate()                        # keyframe a full cycle for timeline playback
summary = {
    "arm_deg": [math.degrees(TH_LOW), math.degrees(TH_HIGH)],
    "handle_elev_deg": [math.degrees(HANDLE_H0), math.degrees(HANDLE_H0 - (TH_HIGH - TH_LOW))],
    "platform_travel": pin_z(TH_HIGH) - pin_z(TH_LOW),
    "wellplate_top": [pin_z(TH_LOW) + STACK + PLATE_H, pin_z(TH_HIGH) + STACK + PLATE_H],
    "tip_bottom": P - 112,
    "arm_link": [ARM_A, LINK2],
    "tdc_deg": math.degrees(TH_TDC),
    "mech_adv": {f"{mm} mm below top": round(mech_adv(
        min((TH_LOW + (TH_TDC - TH_LOW) * i / 4000 for i in range(4001)),
            key=lambda t: abs(pin_z(t) - (pin_z(TH_TDC) - mm)))), 1) for mm in (40, 20, 10, 5, 2, 1)},
    "over_center_drop_mm": pin_z(TH_TDC) - pin_z(TH_HIGH),
}
