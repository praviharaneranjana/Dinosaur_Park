"""Shared helpers for the v02 island build (exec'd inside Blender)."""
import bpy, json, math, random
import numpy as np
ROOT = r"D:\Unity Projects\Dinosaur_Park\Dinosaur_Park\_Source\Blender"
TOOLS = ROOT + r"\00_Shared\Tools"
ISL = ROOT + r"\02_Environment\Island"
J = json.load(open(ISL + r"\island_map_v02.json"))
S = J["shapes"]; SEA = J["sea_level_m"]; HP = J["plateau_m"]; HV = J["headland_m"]
def sstep(a, b, x):
    t = np.clip((np.asarray(x, float) - a)/(b - a), 0, 1); return t*t*(3 - 2*t)
def pip(poly, X, Y):
    P = np.asarray(poly, float); inside = np.zeros(np.shape(X), bool); n = len(P)
    for i in range(n):
        x1, y1 = P[i]; x2, y2 = P[(i+1) % n]
        c = ((y1 > Y) != (y2 > Y)) & (X < (x2 - x1)*(Y - y1)/((y2 - y1) + 1e-12) + x1)
        inside ^= c
    return inside
def seg_d(P, X, Y, closed):
    P = np.asarray(P, float); d = np.full(np.shape(X), 1e9); tt = np.zeros(np.shape(X)); n = len(P); L = 0.0; acc = []
    segs = list(range(n if closed else n - 1))
    lens = [math.hypot(*(P[(i+1) % n] - P[i])) for i in segs]; tot = sum(lens)
    for k, i in enumerate(segs):
        a = P[i]; b = P[(i+1) % n]; ab = b - a; l2 = ab @ ab + 1e-12
        t = np.clip(((X - a[0])*ab[0] + (Y - a[1])*ab[1])/l2, 0, 1)
        dd = np.hypot(X - (a[0] + t*ab[0]), Y - (a[1] + t*ab[1])); m = dd < d
        d = np.where(m, dd, d); tt = np.where(m, (L + t*lens[k])/max(tot, 1e-9), tt); L += lens[k]
    return d, tt
def sdf(poly, X, Y):
    d, _ = seg_d(poly, X, Y, True); return np.where(pip(poly, X, Y), d, -d)
def pline(pts, X, Y): return seg_d(pts, X, Y, False)
def vnoise(X, Y, scale, seed=0):
    rs = np.random.RandomState(seed); u = X/scale + rs.uniform(0, 100); v = Y/scale + rs.uniform(0, 100)
    i0 = np.floor(u).astype(int); j0 = np.floor(v).astype(int); fu = u - i0; fv = v - j0
    fu = fu*fu*(3-2*fu); fv = fv*fv*(3-2*fv)
    def h(i, j):
        n = (i*374761393 + j*668265263 + seed*1442695041) & 0xffffffff
        n = ((n ^ (n >> 13))*1274126177) & 0xffffffff; return (n & 0xffff)/65535.0*2 - 1
    return (h(i0, j0)*(1-fu)*(1-fv) + h(i0+1, j0)*fu*(1-fv) + h(i0, j0+1)*(1-fu)*fv + h(i0+1, j0+1)*fu*fv)
def fbm(X, Y, scale, oct=4, seed=0):
    a, s, out, norm = 1.0, scale, 0.0, 0.0
    for o in range(oct): out = out + a*vnoise(X, Y, s, seed + o*17); norm += a; a *= 0.5; s *= 0.5
    return out/norm
def box_blur(a, r):
    if r <= 0: return a
    p = np.pad(a, r, mode="edge"); c = np.cumsum(np.cumsum(p, 0), 1); c = np.pad(c, ((1, 0), (1, 0)))
    k = 2*r + 1; return (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k])/(k*k)
def coll(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    par = parent or bpy.context.scene.collection
    if c.name not in [x.name for x in par.children]: par.children.link(c)
    return c
def clear_coll(c):
    for o in list(c.objects): bpy.data.objects.remove(o, do_unlink=True)
def lin(c): return tuple((x/255.0)**2.2 if x > 1 else x**2.2 for x in c)

import glob as _glob
_TRN_INDEX = {}
def _trn_index():
    if _TRN_INDEX: return _TRN_INDEX
    for p in sorted(_glob.glob(ROOT + r"\01_Terrain\**\*.blend", recursive=True), reverse=True):
        if p.endswith("1.blend1") or "_Archive" in p: continue
        try:
            with bpy.data.libraries.load(p, link=True) as (src, dst):
                for n in src.objects: _TRN_INDEX.setdefault(("O", n), p)
                for n in src.materials: _TRN_INDEX.setdefault(("M", n), p)
        except Exception: pass
    return _TRN_INDEX
def ensure_trn(name):
    if name in bpy.data.objects: return bpy.data.objects[name]
    p = _trn_index().get(("O", name))
    with bpy.data.libraries.load(p, link=True) as (src, dst): dst.objects = [name]
    return bpy.data.objects[name]
def ensure_mat(name):
    if name in bpy.data.materials: return bpy.data.materials[name]
    p = _trn_index().get(("M", name))
    with bpy.data.libraries.load(p, link=True) as (src, dst): dst.materials = [name]
    return bpy.data.materials[name]
