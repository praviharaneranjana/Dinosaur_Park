"""Reference camera model (shared by layout + Blender). Pixel space = traced space 2212x1652 full-res reference 2400x1792."""
import math
IMG_W, IMG_H = 2400.0, 1792.0
LENS, SENSOR = 50.0, 36.0
PITCH = 42.0          # deg below horizontal
HC = 224.0           # camera height (m): pads come out 24 x 8 m (12 x 4 tiles)
CY = 0.0              # camera Y (m), camera looks +Y (north)
def _basis():
    p = math.radians(PITCH)
    f = (0.0, math.cos(p), -math.sin(p)); up = (0.0, math.sin(p), math.cos(p)); return f, up
def unproject(px, py, z=0.0):
    tan_h = SENSOR/2/LENS; tan_v = tan_h*IMG_H/IMG_W
    xc = (2*px/IMG_W - 1)*tan_h; yc = (1 - 2*py/IMG_H)*tan_v
    f, up = _basis(); d = (xc, f[1] + yc*up[1], f[2] + yc*up[2])
    t = (z - HC)/d[2]; return (xc*t, CY + d[1]*t)
def project(x, y, z):
    tan_h = SENSOR/2/LENS; tan_v = tan_h*IMG_H/IMG_W
    f, up = _basis(); r = (x, y - CY, z - HC)
    zf = r[1]*f[1] + r[2]*f[2]; yu = r[1]*up[1] + r[2]*up[2]
    return ((x/zf/tan_h + 1)*IMG_W/2, (1 - yu/zf/tan_v)*IMG_H/2)
def height_for(px, py_base, py_top, zb=0.0):
    """height (m) of a vertical feature whose foot is at pixel (px,py_base) on plane zb and top at py_top"""
    x, y = unproject(px, py_base, zb); lo, hi = zb, zb + 200
    for _ in range(60):
        mid = (lo+hi)/2
        if project(x, y, mid)[1] > py_top: lo = mid
        else: hi = mid
    return mid - zb
