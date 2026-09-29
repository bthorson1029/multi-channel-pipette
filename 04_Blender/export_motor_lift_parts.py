"""Export the motorized-lift build's new and modified printed parts as STL.

    blender -b --python 04_Blender/export_motor_lift_parts.py

Builds variant_motor_lift.py, then writes each part to 01_Hardware/MotorLift/ToPrint-STL in
millimeters, oriented for printing (flat face on the bed, resting at z = 0). Each part is checked
for open edges first; the script fails rather than write a mesh with holes in its surface.
"""
import bpy, bmesh, math, os, struct, sys
from mathutils import Matrix

here = os.path.dirname(os.path.abspath(__file__))
ns = {"__name__": "variant", "__file__": os.path.join(here, "variant_motor_lift.py")}
exec(compile(open(ns["__file__"], encoding="utf-8").read(), ns["__file__"], "exec"), ns)
ns["pose"](0, 0)

OUT = os.path.normpath(os.path.join(here, "..", "01_Hardware", "MotorLift", "ToPrint-STL"))
PARTS = {   # object -> (file, rotation for printing)
    "plunger_holder_plate": ("plunger_holder_plate_motorlift.stl", Matrix.Identity(3)),
    "lift_tensioner_bracket": ("tensioner_bracket_lift.stl", Matrix.Identity(3)),
    "plunger_tensioner_bracket": ("tensioner_bracket_plunger.stl", Matrix.Identity(3)),
    "lift_home_switch_holder": ("lift_home_switch_holder.stl", Matrix.Identity(3)),
    "plunger_switch_LF_holder": ("plunger_switch_post.stl", Matrix.Identity(3)),       # 3 alike
    "well_plate_nest": ("well_plate_nest.stl", Matrix.Identity(3)),
    "syringe_lock_frame": ("syringe_lock_frame.stl", Matrix.Rotation(math.pi, 3, "X")),   # slots up
    "syringe_grip_slipfit": ("syringe_grip_slipfit.stl", Matrix.Identity(3)),
    "control_box_base": ("control_box_base.stl", Matrix.Rotation(math.pi, 3, "X")),   # countersinks down
    "lift_carriage_bracket_RF": ("lift_carriage_bracket.stl", Matrix.Identity(3)),   # all 4 corners alike
    # hang under the plunger plate: print plate-face down, nut pockets and slots open upward.
    # Two mirror-image hands: RF is the same part as LB turned around, RB the same as LF.
    "plunger_carriage_bracket_RF": ("plunger_carriage_bracket_RF_LB.stl", Matrix.Rotation(math.pi, 3, "X")),
    "plunger_carriage_bracket_RB": ("plunger_carriage_bracket_RB_LF.stl", Matrix.Rotation(math.pi, 3, "X")),
    # L profile printed on its side: the y = -30 face goes down
    "head_bracket_R": ("head_bracket.stl", Matrix.Rotation(math.radians(-90), 3, 'X')),
    # sloped control box: panel face down (undo the slope, then flip), open side up
    "ScreenHousing": ("control_box_housing_sloped.stl",
                      Matrix.Rotation(math.pi, 3, 'X') @ Matrix.Rotation(-math.radians(ns["CONTROL_SLOPE_DEG"]), 3, 'X')),
}


def write_stl(path, tris):
    with open(path, "wb") as fh:
        fh.write(b"multi-channel-pipette motorized-lift part".ljust(80, b" "))
        fh.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            n = (b - a).cross(c - a)
            n = n.normalized() if n.length else n
            fh.write(struct.pack("<12fH", *n, *a, *b, *c, 0))


os.makedirs(OUT, exist_ok=True)
failed = False
for name, (fname, rot) in PARTS.items():
    o = bpy.data.objects[name]
    bm = bmesh.new()
    bm.from_mesh(o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh())
    open_edges = sum(1 for e in bm.edges if not e.is_manifold)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    bm.transform(rot.to_4x4() @ o.matrix_world.to_3x3().to_4x4())   # object rotation, then print pose
    zmin = min(v.co.z for v in bm.verts)
    cx = (min(v.co.x for v in bm.verts) + max(v.co.x for v in bm.verts)) / 2
    cy = (min(v.co.y for v in bm.verts) + max(v.co.y for v in bm.verts)) / 2
    bmesh.ops.translate(bm, verts=bm.verts[:], vec=(-cx, -cy, -zmin))
    tris = [tuple(v.co.copy() for v in f.verts) for f in bm.faces]
    size = [max(v.co[i] for v in bm.verts) - min(v.co[i] for v in bm.verts) for i in range(3)]
    vol = bm.calc_volume(signed=False)
    bm.free()
    if open_edges:
        failed = True
        print(f"EXPORT FAIL {fname}: {open_edges} open edges")
        continue
    write_stl(os.path.join(OUT, fname), tris)
    print(f"EXPORT {fname}: {len(tris)} triangles, {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm, "
          f"{vol / 1000:.1f} cm3, watertight")
if failed:
    sys.exit(1)
