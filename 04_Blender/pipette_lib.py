"""Shared helpers and the base parts for build_pipette.py (mm units, Z up, front = -Y): the frame,
materials, mesh/DXF/STL helpers, and the parts the build starts from before build_pipette.py adds
the rest. Not run on its own. The frame layout was reconstructed from the original design's build
video (youtu.be/2TTu-Lkz2Eo).
"""
import bpy, bmesh, math, os, glob
from mathutils import Vector, Matrix

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
DXF = os.path.normpath(os.path.join(HERE, "..", "01_Hardware", "ToLaserCut-DXF"))   # parts cut as-is
SOURCE = os.path.join(HERE, "source")      # original parts that printed parts are derived from
D = math.radians
X, Y, Z = Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))

# ---------------------------------------------------------------- key dimensions
FX, FY, FH = 229.2, 218.0, 430.0          # frame outer size (bed footprint = frame footprint)
PX, PY = FX / 2 - 10, FY / 2 - 10          # post center lines (104.6, 99)
IX = FX / 2 - 20                           # inner face of side posts (94.6)
BED_RECT_Z = 65.0                          # center of the bed-level extrusion ring
T = 3.0                                    # laser-cut steel thickness
RAIL_H = 10.0                              # MGN9H rail + carriage height
IF_X = IX - RAIL_H - T / 2                 # rail plate mid-plane (83.1)
PIP_MID = 287.772                          # pipette plate mid-plane: the original's, raised 30 mm so an
P = PIP_MID + T / 2                        #   empty tip rack slides out under loaded tips; P = its top
PLG_MID = P + 55 + T / 2                   # drive (plunger) plate mid-plane at build height
PLG_TOP = PLG_MID + T / 2
ZC_HIGH = PLG_MID - 10                     # plunger rail plates' DXF y = 0 edge
GRID = [(-49.5 + 9 * c, -31.5 + 9 * r) for r in range(8) for c in range(12)]


# ---------------------------------------------------------------- scene reset
def reset():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for blk in (bpy.data.meshes, bpy.data.curves, bpy.data.lights, bpy.data.cameras):
        for d in list(blk):
            if d.users == 0:
                blk.remove(d)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 0.001
    sc.unit_settings.length_unit = 'MILLIMETERS'
    for n in ["Frame", "Bed", "Head", "Syringes", "Motors", "Electronics", "Scene_Setup"]:
        sc.collection.children.link(bpy.data.collections.new(n))


# ---------------------------------------------------------------- materials
def mat(name, rgba, metal=0.0, rough=0.5, alpha=1.0, trans=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgba
    b.inputs["Metallic"].default_value = metal
    b.inputs["Roughness"].default_value = rough
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Transmission Weight"].default_value = trans
    m.diffuse_color = (rgba[0], rgba[1], rgba[2], alpha)
    try:
        m.surface_render_method = 'DITHERED'
    except Exception:
        pass
    return m


def materials():
    return {
        "ext": mat("Extrusion_BlackAnodized", (0.02, 0.02, 0.025, 1), 0.5, 0.45),
        "steel": mat("Steel_LaserCut", (0.52, 0.53, 0.55, 1), 0.85, 0.5),
        "chrome": mat("Steel_Polished", (0.75, 0.75, 0.77, 1), 1.0, 0.2),
        "pla": mat("PLA_Peach", (0.95, 0.5, 0.25, 1), 0, 0.5),
        "pla_grey": mat("PLA_Grey", (0.45, 0.46, 0.48, 1), 0, 0.55),
        "white": mat("Nylon_White", (0.9, 0.9, 0.88, 1), 0, 0.4),
        "syr": mat("Syringe_PP", (0.95, 0.97, 1.0, 1), 0, 0.2, 0.45, 0.6),
        "plunger": mat("Plunger_Blue", (0.08, 0.12, 0.35, 1), 0, 0.4),
        "rubber": mat("Rubber_Black", (0.02, 0.02, 0.02, 1), 0, 0.8),
        "tip": mat("Tip_Yellow", (1.0, 0.9, 0.35, 1), 0, 0.2, 0.55, 0.6),
        "motor": mat("Motor_Black", (0.03, 0.03, 0.035, 1), 0.3, 0.4),
        "brass": mat("Brass", (0.85, 0.6, 0.25, 1), 1.0, 0.3),
        "wellplate": mat("Wellplate_Clear", (0.95, 0.95, 0.98, 1), 0, 0.1, 0.5, 0.7),
        "lcd": mat("LCD_Screen", (0.25, 0.75, 1.0, 1), 0, 0.2),
        "lcd_frame": mat("LCD_Bezel", (0.02, 0.02, 0.02, 1), 0, 0.5),
    }


# ---------------------------------------------------------------- mesh helpers
def coll(name):
    return bpy.data.collections[name]


def new_obj(name, bm, c, m=None, loc=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    coll(c).objects.link(o)
    o.location = loc
    if m:
        me.materials.append(m)
    return o


def box(name, size, loc, c, m, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if bevel:
        bmesh.ops.bevel(bm, geom=bm.edges[:], offset=min(bevel, 0.45 * min(size)),
                        segments=2, affect='EDGES', clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return new_obj(name, bm, c, m, loc)


def _tslot_profile():
    """2020 B-type (6 mm slot) outline, CCW: a slot in each face (6.2 opening, 1.8 lip, cavity
    widening to 11 then tapering to the core 6.1 deep), 0.5 chamfered corners. No center bore."""
    side = [(9.5, 10), (3.1, 10), (3.1, 8.2), (5.5, 8.2), (5.5, 6.5), (2.9, 3.9), (-2.9, 3.9),
            (-5.5, 6.5), (-5.5, 8.2), (-3.1, 8.2), (-3.1, 10), (-9.5, 10)]
    pts = []
    for k in range(4):                                # +y face, then rotated a quarter turn at a time
        c, s = math.cos(k * math.pi / 2), math.sin(k * math.pi / 2)
        pts += [(round(x * c - y * s, 6), round(x * s + y * c, 6)) for x, y in side]
    return pts


def tslot_bar(name, L, loc, axis, c, m):
    """A length of 2020 T-slot along X, Y or Z, centered on loc (geometry baked, no rotation)."""
    to_world = {'X': lambda u, v, w: (w, u, v), 'Y': lambda u, v, w: (u, w, v), 'Z': lambda u, v, w: (u, v, w)}[axis]
    bm = bmesh.new()
    prof = _tslot_profile()
    lo = [bm.verts.new(to_world(u, v, -L / 2)) for u, v in prof]
    hi = [bm.verts.new(to_world(u, v, L / 2)) for u, v in prof]
    n = len(prof)
    for i in range(n):
        bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    caps = [bm.faces.new(lo[::-1]), bm.faces.new(hi)]
    bmesh.ops.triangulate(bm, faces=caps)             # the outline is concave
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return new_obj(name, bm, c, m, loc)


def bolt_mesh(bm, p, d, head_d, head_h, length, r):
    """Button-head bolt: head on p's outer side (direction d), shank `length` into -d."""
    d = Vector(d).normalized()
    rot = d.to_track_quat('Z', 'Y').to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=head_d / 2, radius2=head_d / 2 - 1.0,
                          depth=head_h, matrix=Matrix.Translation(Vector(p) + d * head_h / 2) @ rot)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=r, radius2=r, depth=length,
                          matrix=Matrix.Translation(Vector(p) - d * length / 2) @ rot)


def cyl(name, r, h, loc, c, m, axis='Z', seg=32, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r,
                          radius2=r if r2 is None else r2, depth=h)
    o = new_obj(name, bm, c, m, loc)
    o.rotation_euler = {'X': (0, D(90), 0), 'Y': (D(90), 0, 0), 'Z': (0, 0, 0)}[axis]
    return o


def dup(src, name, c=None):
    o = src.copy()
    o.name = name
    (coll(c) if c else src.users_collection[0]).objects.link(o)
    return o


def frame_to(o, xcol, ycol, anchor_local, anchor_world):
    """Orient o so its local X/Y map to xcol/ycol and anchor_local lands on anchor_world."""
    xcol, ycol = Vector(xcol).normalized(), Vector(ycol).normalized()
    R = Matrix((xcol, ycol, xcol.cross(ycol))).transposed()
    loc = Vector(anchor_world) - R @ Vector((list(anchor_local) + [0, 0])[:3])
    o.matrix_world = Matrix.Translation(loc) @ R.to_4x4()
    return o


# ---------------------------------------------------------------- DXF import (native coordinates)
def read_dxf(path):
    L = [l.strip() for l in open(path, errors='ignore').read().splitlines()]
    ents, cur, ins = [], None, False
    for c, v in zip(L[0::2], L[1::2]):
        if c == '2' and v == 'ENTITIES':
            ins = True
            continue
        if not ins:
            continue
        if c == '0':
            if cur:
                ents.append(cur)
            if v == 'ENDSEC':
                break
            cur = {'t': v}
        elif cur is not None and c not in cur:
            cur[c] = v
    loops, segs = [], []
    for e in ents:
        if e['t'] == 'CIRCLE':
            cx, cy, r = float(e['10']), float(e['20']), float(e['40'])
            n = max(12, int(r * 4))
            loops.append([(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n))
                          for i in range(n)])
        elif e['t'] == 'LINE':
            segs.append([(float(e['10']), float(e['20'])), (float(e['11']), float(e['21']))])
        elif e['t'] == 'ARC':
            cx, cy, r = float(e['10']), float(e['20']), float(e['40'])
            a0, a1 = float(e['50']), float(e['51'])
            if a1 < a0:
                a1 += 360
            n = max(2, int((a1 - a0) / 10) + 1)
            segs.append([(cx + r * math.cos(D(a0 + (a1 - a0) * i / n)),
                          cy + r * math.sin(D(a0 + (a1 - a0) * i / n))) for i in range(n + 1)])
    near = lambda a, b: abs(a[0] - b[0]) < 1e-3 and abs(a[1] - b[1]) < 1e-3
    while segs:
        loop = segs.pop(0)[:]
        grown = True
        while grown and not near(loop[0], loop[-1]):
            grown = False
            for i, s in enumerate(segs):
                if near(loop[-1], s[0]):
                    loop += s[1:]
                elif near(loop[-1], s[-1]):
                    loop += s[::-1][1:]
                else:
                    continue
                segs.pop(i)
                grown = True
                break
        if near(loop[0], loop[-1]):
            loop = loop[:-1]
        loops.append(loop)
    return loops


def dxf_part(fname, name, thick, c, m, xform=None):
    """xform(x, y) -> (x, y) lets a variant derive a modified cut (e.g. a shorter arm)."""
    cu = bpy.data.curves.new(name, 'CURVE')
    cu.dimensions, cu.fill_mode, cu.extrude = '2D', 'BOTH', thick / 2
    for l in read_dxf(os.path.join(DXF, fname)):
        if xform:
            l = [xform(x, y) for x, y in l]
        sp = cu.splines.new('POLY')
        sp.points.add(len(l) - 1)
        for i, (x, y) in enumerate(l):
            sp.points[i].co = (x, y, 0, 1)
        sp.use_cyclic_u = True
    tmp = bpy.data.objects.new(name + "_crv", cu)
    coll(c).objects.link(tmp)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    o = bpy.data.objects.new(name, me)
    coll(c).objects.link(o)
    me.materials.append(m)
    return o


# ---------------------------------------------------------------- STL import (Y-up -> Z-up, origin bottom-center)
def import_stl(fname, c, m, rot=None):
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.wm.stl_import(filepath=os.path.join(SOURCE, fname), up_axis='Y', forward_axis='NEGATIVE_Z')
    o = bpy.context.selected_objects[0]
    o.name = os.path.splitext(os.path.basename(fname))[0]
    for cc in list(o.users_collection):
        cc.objects.unlink(o)
    coll(c).objects.link(o)
    M = o.matrix_basis.copy()        # matrix_world is stale until the depsgraph updates
    if rot:
        M = rot.to_4x4() @ M
    o.data.transform(M)
    o.matrix_world = Matrix.Identity(4)
    bm = bmesh.new()                     # STL repeats each shared vertex per triangle: weld them so
    bm.from_mesh(o.data)                 # the mesh is watertight (booleans and exports need that)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-4)
    bm.to_mesh(o.data)
    bm.free()
    vs = [v.co for v in o.data.vertices]
    mn = Vector([min(v[i] for v in vs) for i in range(3)])
    mx = Vector([max(v[i] for v in vs) for i in range(3)])
    o.data.transform(Matrix.Translation(-Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))))
    o.data.update()
    bpy.context.view_layer.update()      # refresh bound_box so .dimensions is valid for placement
    o.data.materials.clear()
    o.data.materials.append(m)
    return o


# ================================================================ BUILD
def build():
    reset()
    M = materials()

    # ---------------- frame: 4 posts + 3 rings of 2020, L brackets at the corners
    def ext(name, L, loc, axis):
        return tslot_bar(name, L, loc, axis, "Frame", M["ext"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            ext(f"post_{'LR'[sx > 0]}{'FB'[sy > 0]}", FH, (sx * PX, sy * PY, FH / 2), 'Z')
    for lvl, z in (("bottom", 10), ("bed", BED_RECT_Z), ("top", FH - 10)):
        for s in (-1, 1):
            if lvl != "bed":                   # the bed level has side bars only, clear of the bed
                ext(f"ext_{lvl}_{'FB'[s > 0]}", FX - 40, (0, s * PY, z), 'X')
            ext(f"ext_{lvl}_{'LR'[s > 0]}", FY - 40, (s * PX, 0, z), 'Y')
    br_src = dxf_part("corner_bracket.dxf", "angle_bracket", T, "Frame", M["steel"])
    # Each bracket's 4 M5 holes (DXF coordinates; the corner is at (-18, -18)) are 9 mm in from its
    # edges, so it sits 1 mm in from the frame's corner to put them on the slot centerlines (10 mm).
    # Button-head M5 x 8 through the 3 mm plate into a T-nut in the slot (x 10 would bottom out on
    # the extrusion's core).
    holes = [(-9.0, 17.0), (-9.0, 37.0), (17.0, -9.0), (37.0, -9.0)]
    bolts, nuts = bmesh.new(), bmesh.new()
    n = 0
    for normal, h, half_h, half_n in ((-Y, X, FX / 2, FY / 2), (Y, X, FX / 2, FY / 2),
                                      (-X, Y, FY / 2, FX / 2), (X, Y, FY / 2, FX / 2)):
        for sh in (-1, 1):
            for top in (False, True):
                o = br_src if n == 0 else dup(br_src, f"angle_bracket.{n:03d}")
                corner = h * sh * half_h + normal * (half_n + T / 2) + Z * (FH if top else 0)
                frame_to(o, -h * sh, -Z if top else Z, (-19, -19), corner)
                bpy.context.view_layer.update()
                for hx, hy in holes:
                    face = o.matrix_world @ Vector((hx, hy, 0)) - normal * T / 2      # extrusion face
                    bolt_mesh(bolts, face + normal * T, normal, 9.5, 2.75, 8.0, 2.5)
                    along = Z if hx < 0 else h                                    # post leg / ring-bar leg
                    across = normal.cross(along)
                    c = face - normal * (1.9 + 1.15)                                # behind the 1.8 mm lip
                    g_ = bmesh.ops.create_cube(nuts, size=1)
                    bmesh.ops.transform(nuts, verts=g_["verts"], matrix=Matrix(
                        [[along[i] * 10.0, across[i] * 9.5, normal[i] * 2.3, c[i]] for i in range(3)] + [[0, 0, 0, 1]]))
                n += 1
    new_obj("frame_bolts", bolts, "Frame", M["motor"])
    new_obj("frame_tnuts", nuts, "Frame", M["chrome"])

    # ---------------- well plate (build_pipette.py seats it in the nest)
    wp = box("well_plate_96", (127.76, 85.48, 14.4), (0, 0, 7.2), "Bed", M["wellplate"], bevel=1.5)
    bm = bmesh.new()
    for (x, y) in GRID:
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=3.4, radius2=3.4, depth=12.5,
                              matrix=Matrix.Translation((x, y, 14.4 - 5.25 - 7.2)))
    cut = new_obj("wells_cut", bm, "Bed", loc=wp.location)   # cutter is in plate-local coords
    mod = wp.modifiers.new("wells", 'BOOLEAN')
    mod.object, mod.operation, mod.solver = cut, 'DIFFERENCE', 'EXACT'
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    baked = bpy.data.meshes.new_from_object(wp.evaluated_get(dg))   # bake without operator context
    wp.modifiers.clear()
    wp.data = baked
    assert len(wp.data.polygons) > 500, "well boolean failed"
    bpy.data.objects.remove(cut)

    # ---------------- head: pipette plate, drive (plunger) plate, the barrel grip (all in the DXFs'
    # own frame: the syringe array's center is at DXF (-49.5, +/-31.5))
    pip = dxf_part("pipette_plate.dxf", "pipette_plate", T, "Head", M["steel"])
    pip.location = (49.5, -31.5, PIP_MID)
    plg = dxf_part("plunger_plate.dxf", "plunger_plate", T, "Head", M["steel"])
    plg.location = (49.5, 31.5, PLG_MID)
    grip = import_stl("syringe_grip_static.STL", "Head", M["pla"], rot=Matrix.Rotation(D(90), 3, 'Z'))
    grip.location = (0, 0, P - T - grip.dimensions.z)

    # plunger rail plates + their carriages on the posts' rails
    src = dxf_part("plunger_rail_plate.dxf", "interface_plate_high", T, "Head", M["steel"])
    for i, (sx, sy) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        o = src if i == 0 else dup(src, f"{src.name}.{i:03d}")
        frame_to(o, -sy * Y, Z, (-10, 0), (sx * IF_X, sy * PY, ZC_HIGH))
        box(f"MGN9H_carriage_high_{'LR'[sx > 0]}{'FB'[sy > 0]}", (6.5, 20, 39.9),
            (sx * (IX - 6.5 - 3.25 + 3), sy * PY, ZC_HIGH + 4), "Frame", M["chrome"], bevel=0.5)

    # ---------------- electronics box, as the original hung it on the front face (LCD 20x4 +
    # encoder); build_pipette.py lays it down in front of the base
    hs = import_stl("ScreenHousing.STL", "Electronics", M["pla"], rot=Matrix.Rotation(D(90), 3, 'X'))
    hs.location = (0, -FY / 2 - hs.dimensions.y / 2 - 4.5, FH - hs.dimensions.z)
    lid = import_stl("electronics_lid.STL", "Electronics", M["pla"], rot=Matrix.Rotation(D(90), 3, 'X'))
    lid.location = (0, -FY / 2 - lid.dimensions.y / 2, FH - hs.dimensions.z / 2 - lid.dimensions.z / 2)
    fy = hs.location.y - hs.dimensions.y / 2
    # window (98x38) and encoder hole positions found by ray-casting the housing face; heights are
    # from the housing's top (FH), so they follow it
    box("LCD_2004_bezel", (98, 1.5, 60), (36, fy + 3.5, FH - 35), "Electronics", M["lcd_frame"])
    box("LCD_2004_screen", (76, 1, 26), (36, fy + 2.5, FH - 35), "Electronics", M["lcd"])
    cyl("encoder_knob", 7, 12, (37, fy - 6, FH - 76), "Electronics", M["motor"], axis='Y')

def stage():
    sc = bpy.context.scene
    cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
    coll("Scene_Setup").objects.link(cam)
    cam.data.lens, cam.data.clip_start, cam.data.clip_end = 50, 10, 20000
    cam.location = (620, -860, 520)
    cam.rotation_euler = (Vector((0, 0, 190)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    for n, loc, e, s in (("Key", (500, -600, 900), 9000, 600), ("Fill", (-800, -300, 400), 2500, 800),
                         ("Rim", (-200, 700, 900), 3500, 500)):
        l = bpy.data.objects.new(n, bpy.data.lights.new(n, 'AREA'))
        coll("Scene_Setup").objects.link(l)
        l.data.energy, l.data.size, l.location = e, s, loc
        l.rotation_euler = (Vector((0, 0, 200)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    g = box("Ground", (3000, 3000, 1), (0, 0, -0.5), "Scene_Setup",
            mat("Bench", (0.62, 0.5, 0.36, 1), 0, 0.7))
    sc.render.engine = 'CYCLES'   # EEVEE washes out at this (mm-as-unit) scale
    sc.cycles.samples, sc.cycles.use_denoising = 64, True
    sc.render.resolution_x, sc.render.resolution_y = 1600, 1200
    if sc.world is None:
        sc.world = bpy.data.worlds.new("World")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.8, 0.82, 0.86, 1)
    bg.inputs[1].default_value = 0.5
    # Every saved screen (not just the active one, which is None under `blender -b`), so a .blend
    # saved headless opens with the view far enough out and without clipping the 3 m ground
    # (mm-as-unit: Blender's default 1000-unit clip end is only 1 m here).
    target = Vector((0, 0, 190))
    for scr in bpy.data.screens:
        for a in scr.areas:
            if a.type != 'VIEW_3D':
                continue
            s = a.spaces[0]
            s.clip_start, s.clip_end = 1, 20000
            s.shading.type = 'MATERIAL'
            r = s.region_3d
            r.view_perspective = 'PERSP'
            r.view_location = target
            r.view_rotation = cam.rotation_euler.to_quaternion()
            r.view_distance = (cam.location - target).length
