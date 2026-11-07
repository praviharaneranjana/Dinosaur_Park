"""Dino Park Tycoon - island wind v01 (isl_wind.py).

exec inside Blender:   ns = {}; exec(open(path).read(), ns); ns["apply_wind_many"](objs)

Gives every plant object its OWN wind animation: geometry-nodes group 'ISL_Wind' (same maths as pln_kit.PLN_Motion
plus per-instance TimeOffset / PhaseOffset, a world-space island gust field, slow wind-direction wander, rare strong
gust waves, global WindStrength and an optional control Empty).  Driven by Scene Time, no keyframes.
Reads the per-vertex float attributes bend / flutter / phase (mesh attributes are NOT touched).
Objects must be LOCAL (library-linked objects cannot get modifiers).  Linked duplicates (shared mesh) are fine:
every object has its own modifier.

Wind control Empty ("ISL_WindControl", make_wind_control()):
   scale.x    = global wind strength multiplier (1 = normal, 0.3 = calm, 2 = storm)
   rotation_euler.z = extra wind direction rotation in radians (added to each plant's own direction)
   Animate with keyframes, e.g. ctl.scale = (0.4,)*3; ctl.keyframe_insert("scale", frame=1); ctl.scale = (2,)*3;
   ctl.keyframe_insert("scale", frame=240).  Plants only see it if the object is assigned (apply_wind does this
   automatically when the Empty exists in bpy.data.objects, or pass control=).  If no control object is assigned
   the group falls back to strength 1, rotation 0.
"""
import bpy, math, random

# amp, gust, freq, wave_k, flutter, bob, droop   (copy of pln_kit.MOTION; keep in sync)
MOTION = {
    "tree":      (0.10, 0.9, 0.9, 0.0, 0.030, 0.0, 1.0),
    "tree_big":  (0.16, 0.9, 0.6, 0.0, 0.035, 0.0, 1.0),
    "conifer":   (0.08, 0.8, 0.8, 0.0, 0.020, 0.0, 1.0),
    "palm":      (0.22, 1.0, 0.8, 0.0, 0.060, 0.0, 1.0),
    "shrub":     (0.04, 0.9, 1.3, 0.0, 0.025, 0.0, 1.0),
    "fern":      (0.05, 0.9, 1.2, 0.0, 0.040, 0.0, 1.0),
    "grass":     (0.07, 1.2, 1.9, 0.0, 0.020, 0.0, 1.0),
    "reed":      (0.12, 1.1, 1.4, 0.0, 0.030, 0.0, 1.0),
    "flower":    (0.05, 1.0, 1.7, 0.0, 0.030, 0.0, 1.0),
    "hedge":     (0.004, 0.5, 1.0, 0.0, 0.010, 0.0, 0.0),
    "deadwood":  (0.015, 0.6, 1.2, 0.0, 0.0,   0.0, 0.0),
    "kelp":      (0.34, 0.5, 0.45, 1.5, 0.070, 0.0, 1.0),
    "seaweed":   (0.15, 0.5, 0.6, 2.6, 0.050, 0.0, 1.0),
    "coral_fan": (0.03, 0.4, 0.5, 1.0, 0.010, 0.0, 0.0),
    "float":     (0.0,  0.0, 1.0, 0.0, 0.006, 0.010, 0.0),
}
MOTION_FIELDS = ("Amp", "Gust", "Freq", "WaveK", "Flutter", "Bob", "Droop")
GROUP_NAME = "ISL_Wind"
MOD_NAME = "ISL_Wind"
GUST_SPEED = 5.0          # m/s, speed of the gust front across the island
DEFAULT_GUST_SCALE = 0.03  # noise cycles per metre (~30 m gust cells)

# ---------------------------------------------------------------- node group
def _sock(ng, name, in_out="INPUT"):
    for s in ng.interface.items_tree:
        if getattr(s, "item_type", "SOCKET") == "SOCKET" and s.name == name and s.in_out == in_out:
            return s
    return None

def make_wind_group(rebuild=False):
    ng = bpy.data.node_groups.get(GROUP_NAME)
    if ng and not rebuild:
        return ng
    if ng:
        bpy.data.node_groups.remove(ng)
    ng = bpy.data.node_groups.new(GROUP_NAME, 'GeometryNodeTree')
    itf = ng.interface
    itf.new_socket("Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    for nm, dv in (("Amp", 0.1), ("Gust", 0.9), ("Freq", 1.0), ("WaveK", 0.0), ("Flutter", 0.03), ("Bob", 0.0),
                   ("Droop", 1.0), ("DirX", 1.0), ("DirY", 0.25), ("TimeOffset", 0.0), ("PhaseOffset", 0.0)):
        s = itf.new_socket(nm, in_out='INPUT', socket_type='NodeSocketFloat'); s.default_value = dv
    s = itf.new_socket("InstancePos", in_out='INPUT', socket_type='NodeSocketVector'); s.default_value = (0, 0, 0)
    for nm, dv in (("GustScale", DEFAULT_GUST_SCALE), ("WindStrength", 1.0)):
        s = itf.new_socket(nm, in_out='INPUT', socket_type='NodeSocketFloat'); s.default_value = dv
    itf.new_socket("Control", in_out='INPUT', socket_type='NodeSocketObject')
    itf.new_socket("Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    N = ng.nodes; Lk = ng.links
    gi = N.new("NodeGroupInput"); go = N.new("NodeGroupOutput")
    I = gi.outputs

    def M(op, a, b=None, c=None, clamp=False):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, x in enumerate((a, b, c)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[i].default_value = float(x)
            else: Lk.new(x, n.inputs[i])
        return n.outputs[0]
    def A(name):
        n = N.new("GeometryNodeInputNamedAttribute"); n.data_type = 'FLOAT'; n.inputs["Name"].default_value = name
        return n.outputs["Attribute"]
    def VM(op, a, b=None, s=None):
        n = N.new("ShaderNodeVectorMath"); n.operation = op
        for i, x in ((0, a), (1, b)):
            if x is None: continue
            if isinstance(x, tuple): n.inputs[i].default_value = x
            else: Lk.new(x, n.inputs[i])
        if s is not None:
            if isinstance(s, (int, float)): n.inputs["Scale"].default_value = s
            else: Lk.new(s, n.inputs["Scale"])
        return n.outputs[0]
    def NZ(vec, w, scale, detail=2.0):
        n = N.new("ShaderNodeTexNoise"); n.noise_dimensions = '4D'
        n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        Lk.new(vec, n.inputs["Vector"]); Lk.new(w, n.inputs["W"]); return n
    def CXYZ(x, y, z):
        n = N.new("ShaderNodeCombineXYZ")
        for i, v in enumerate((x, y, z)):
            if isinstance(v, (int, float)): n.inputs[i].default_value = float(v)
            else: Lk.new(v, n.inputs[i])
        return n.outputs[0]
    def SXYZ(v):
        n = N.new("ShaderNodeSeparateXYZ"); Lk.new(v, n.inputs[0]); return n.outputs
    def SEL(cond, a, b):   # cond>0.5 -> a else b  (float)
        return M('ADD', M('MULTIPLY', cond, a), M('MULTIPLY', M('SUBTRACT', 1.0, cond), b))

    tg = N.new("GeometryNodeInputSceneTime").outputs["Seconds"]      # shared (global) time
    st = M('ADD', tg, I["TimeOffset"])                                # per-instance time
    pos = N.new("GeometryNodeInputPosition").outputs[0]
    pz = SXYZ(pos)[2]
    bend, flut, ph0 = A("bend"), A("flutter"), A("phase")
    ph = M('ADD', ph0, I["PhaseOffset"])

    # ---- control empty (Object Info): scale.x = strength, rotation.z = direction
    oi = N.new("GeometryNodeObjectInfo"); oi.transform_space = 'ORIGINAL'
    Lk.new(I["Control"], oi.inputs["Object"])
    r2e = N.new("FunctionNodeRotationToEuler"); Lk.new(oi.outputs["Rotation"], r2e.inputs[0])
    cs_raw = SXYZ(oi.outputs["Scale"])[0]
    cs_ok = M('GREATER_THAN', cs_raw, 0.0001)
    ctl_str = SEL(cs_ok, cs_raw, 1.0)                                 # no control object -> 1
    ctl_rot = SXYZ(r2e.outputs[0])[2]                                 # no control object -> 0

    # ---- wind direction: normalise (DirX,DirY), add control rotation + slow global wander (+-~20 deg)
    dn = VM('NORMALIZE', CXYZ(I["DirX"], I["DirY"], 0.0))
    dxy = SXYZ(dn)
    ipx, ipy = SXYZ(I["InstancePos"])[0], SXYZ(I["InstancePos"])[1]
    wander = M('ADD', M('MULTIPLY', M('SINE', M('ADD', M('MULTIPLY', tg, 0.071), M('MULTIPLY', ipx, 0.004))), 0.25),
                      M('MULTIPLY', M('SINE', M('ADD', M('MULTIPLY', tg, 0.173), M('MULTIPLY', ipy, 0.006), 1.7)), 0.10))
    ang = M('ADD', wander, ctl_rot)
    ca, sa = M('COSINE', ang), M('SINE', ang)
    dx = M('SUBTRACT', M('MULTIPLY', dxy[0], ca), M('MULTIPLY', dxy[1], sa))
    dy = M('ADD', M('MULTIPLY', dxy[0], sa), M('MULTIPLY', dxy[1], ca))
    dvec = CXYZ(dx, dy, 0.0)

    # ---- island gust field (world space, travelling along the wind)
    wp = VM('ADD', pos, I["InstancePos"])
    travel = VM('SCALE', dvec, s=M('MULTIPLY', M('MULTIPLY', tg, GUST_SPEED), I["GustScale"]))
    gvec = VM('SUBTRACT', VM('SCALE', wp, s=I["GustScale"]), travel)
    gn = NZ(gvec, M('MULTIPLY', tg, 0.05), 1.0, 2.0)                       # per vertex (coherent between neighbours)
    g = M('MULTIPLY', M('SUBTRACT', gn.outputs[0], 0.5), 2.0)
    gg = M('MULTIPLY', g, I["Gust"])
    # rare strong gust waves: low-frequency noise at InstancePos only (constant per object -> evaluated once)
    ivec = VM('SUBTRACT', VM('SCALE', I["InstancePos"], s=M('MULTIPLY', I["GustScale"], 0.35)),
                          VM('SCALE', dvec, s=M('MULTIPLY', M('MULTIPLY', tg, GUST_SPEED * 1.6), M('MULTIPLY', I["GustScale"], 0.35))))
    bn = NZ(ivec, M('ADD', M('MULTIPLY', tg, 0.03), 11.0), 1.0, 1.0)
    strong = M('MULTIPLY', M('MAXIMUM', M('SUBTRACT', bn.outputs[0], 0.55), 0.0), 3.0)     # 0..~1.3, mostly 0
    ampmul = M('MULTIPLY', M('MULTIPLY', I["WindStrength"], ctl_str), M('ADD', 1.0, M('MULTIPLY', strong, 1.5)))

    # ---- PLN_Motion maths with per-instance time / phase
    t = M('MULTIPLY', st, I["Freq"])
    ph6 = M('MULTIPLY', ph, 6.2832)
    kz = M('MULTIPLY', pz, I["WaveK"])
    w1 = M('SINE', M('SUBTRACT', M('ADD', M('MULTIPLY', t, 6.2832 * 0.55), M('MULTIPLY', ph6, 0.35)), kz))
    w2 = M('SINE', M('SUBTRACT', M('ADD', M('MULTIPLY', t, 6.2832 * 0.92), M('MULTIPLY', ph6, 0.6)), M('MULTIPLY', kz, 1.3)))
    ab = M('MULTIPLY', M('MULTIPLY', I["Amp"], ampmul), bend)
    ox = M('MULTIPLY', ab, M('ADD', M('ADD', M('MULTIPLY', w1, 0.6), gg), 0.22))
    oy = M('MULTIPLY', ab, M('MULTIPLY', w2, 0.45))
    rx = M('SUBTRACT', M('MULTIPLY', ox, dx), M('MULTIPLY', oy, dy))
    ry = M('ADD', M('MULTIPLY', ox, dy), M('MULTIPLY', oy, dx))
    hs = M('ADD', M('MULTIPLY', rx, rx), M('MULTIPLY', ry, ry))
    oz = M('MULTIPLY', M('DIVIDE', hs, M('MAXIMUM', M('MULTIPLY', pz, 2.0), 0.3)), M('MULTIPLY', I["Droop"], -1.0))
    bob = M('MULTIPLY', I["Bob"], M('SINE', M('ADD', M('MULTIPLY', st, 1.3), ph6)))
    oz = M('ADD', oz, bob)
    cm = CXYZ(rx, ry, oz)
    fl = NZ(VM('SCALE', pos, s=3.0), M('ADD', M('MULTIPLY', st, M('MULTIPLY', I["Freq"], 2.2)), ph6), 1.0)
    fv = VM('SCALE', VM('SUBTRACT', fl.outputs["Color"], (0.5, 0.5, 0.5)),
            s=M('MULTIPLY', M('MULTIPLY', M('MULTIPLY', flut, I["Flutter"]), 2.0), M('MAXIMUM', ampmul, 0.25)))
    off = VM('ADD', cm, fv)
    spn = N.new("GeometryNodeSetPosition")
    Lk.new(I["Geometry"], spn.inputs["Geometry"]); Lk.new(off, spn.inputs["Offset"])
    Lk.new(spn.outputs[0], go.inputs[0])
    return ng

# ---------------------------------------------------------------- helpers
def _set_input(md, ng, name, value):
    """Set a modifier input robustly (Blender 5.x: ID-properties keyed by socket identifier)."""
    sock = _sock(ng, name)
    if sock is None: raise KeyError(name)
    key = sock.identifier
    if isinstance(value, (tuple, list)): value = [float(v) for v in value]
    elif isinstance(value, (int, float)) and not isinstance(value, bool): value = float(value)
    try:
        md[key] = value
    except Exception:
        getattr(md.properties.inputs, key).value = value
    return key

def get_inputs(md):
    """Return {socket name: value} of an ISL_Wind modifier (for tests/debug)."""
    out = {}
    for s in md.node_group.interface.items_tree:
        if getattr(s, "item_type", "") == "SOCKET" and s.in_out == 'INPUT' and s.name != "Geometry":
            v = md.get(s.identifier)
            try: v = list(v) if hasattr(v, "__len__") and not isinstance(v, str) else v
            except Exception: pass
            out[s.name] = v
    return out

def get_wind_control(name="ISL_WindControl"):
    return bpy.data.objects.get(name)

def make_wind_control(name="ISL_WindControl", scene=None, location=(0, 0, 0), strength=1.0, direction_deg=0.0):
    """Create (or fetch) the control Empty.  scale.x = strength, rotation_euler.z = extra wind direction (rad)."""
    ob = bpy.data.objects.get(name)
    if ob is None:
        ob = bpy.data.objects.new(name, None)
        ob.empty_display_type = 'SINGLE_ARROW'; ob.empty_display_size = 3.0
        (scene or bpy.context.scene).collection.objects.link(ob)
    ob.location = location
    ob.scale = (strength, strength, strength)
    ob.rotation_euler = (0.0, 0.0, math.radians(direction_deg))
    return ob

def apply_wind(ob, preset=None, seed=0, strength=1.0, prevailing_deg=20.0, control="auto", gust_scale=DEFAULT_GUST_SCALE):
    """Replace PLN_Motion / ISL_Wind on a LOCAL object by ISL_Wind with deterministic per-seed jitter.
    Returns the modifier, or None for rigid presets (amp 0 and bob 0) / non-mesh / library-linked objects."""
    if ob is None or ob.type != 'MESH' or ob.library is not None or (ob.override_library is not None and False):
        return None
    if preset is None:
        preset = ob.get("motion") or "tree"
    vals = MOTION.get(preset) or MOTION["tree"]
    for m in list(ob.modifiers):
        if m.type == 'NODES' and (m.name in ("PLN_Motion", MOD_NAME) or
                                  (m.node_group and m.node_group.name in ("PLN_Motion", GROUP_NAME))):
            ob.modifiers.remove(m)
    amp, gust, freq, wavek, flut, bob, droop = vals
    if amp <= 0.0 and bob <= 0.0:          # rigid: no modifier
        return None
    rnd = random.Random(int(seed) * 7919 + 13)
    amp_j = amp * rnd.uniform(0.75, 1.3)
    freq_j = freq * rnd.uniform(0.85, 1.2)
    toff = rnd.uniform(0.0, 30.0)
    poff = rnd.uniform(0.0, 1.0)
    ang = math.radians(prevailing_deg + rnd.uniform(-25.0, 25.0))
    ng = make_wind_group()
    md = ob.modifiers.new(MOD_NAME, 'NODES'); md.node_group = ng
    ob.update_tag()
    ob["motion"] = preset
    pos = ob.matrix_world.translation
    for nm, v in (("Amp", amp_j), ("Gust", gust), ("Freq", freq_j), ("WaveK", wavek), ("Flutter", flut), ("Bob", bob),
                  ("Droop", droop), ("DirX", math.cos(ang)), ("DirY", math.sin(ang)), ("TimeOffset", toff),
                  ("PhaseOffset", poff), ("InstancePos", (pos.x, pos.y, pos.z)), ("GustScale", gust_scale),
                  ("WindStrength", strength)):
        _set_input(md, ng, nm, v)
    if control == "auto": control = get_wind_control()
    elif isinstance(control, str): control = bpy.data.objects.get(control)
    if control is not None:
        _set_input(md, ng, "Control", control)
    ob.update_tag()
    return md

def apply_wind_many(objs, base_seed=1, strength=1.0, **kw):
    """apply_wind to many objects, seed = base_seed + index.  Returns list of modifiers (None where skipped)."""
    return [apply_wind(o, seed=base_seed + i, strength=strength, **kw) for i, o in enumerate(objs)]

def refresh_positions(objs):
    """Call after moving objects (InstancePos is a stored copy of the world position)."""
    for o in objs:
        md = o.modifiers.get(MOD_NAME)
        if md:
            p = o.matrix_world.translation
            _set_input(md, md.node_group, "InstancePos", (p.x, p.y, p.z)); o.update_tag()

def describe():
    lines = ["ISL_Wind presets (amp, gust, freq, wave_k, flutter, bob, droop):"]
    for k, v in MOTION.items():
        lines.append("  %-10s %s%s" % (k, v, "   (rigid/none)" if v[0] <= 0 and v[5] <= 0 else ""))
    lines.append("Jitter per object: Amp x0.75-1.3, Freq x0.85-1.2, TimeOffset 0-30 s, PhaseOffset 0-1, dir +/-25 deg around prevailing.")
    summary = ("ISL_Wind inputs: Geometry, Amp, Gust, Freq, WaveK, Flutter, Bob, Droop, DirX, DirY, TimeOffset(s), PhaseOffset(0-1), "
               "InstancePos(world xyz), GustScale(1/m, def %.3f), WindStrength(x), Control(Empty: scale.x=strength, rot.z=direction)." % DEFAULT_GUST_SCALE)
    return {"presets": dict(MOTION), "text": "\n".join(lines), "summary": summary}
