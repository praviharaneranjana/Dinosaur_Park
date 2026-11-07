"""Dino Park Tycoon - ISLAND LAYOUT v02 (camera-matched to the reference image).
All shapes are traced in FULL-RES reference pixels (2400x1792) and un-projected through isl_cam (the reconstructed
reference camera) onto the height they sit at. Output: Blender-space metres (X east, Y north, Z up) + a 2 m game grid.
Run: python3 isl_layout_v02.py"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import isl_cam as C
ROOT = os.path.dirname(os.path.dirname(HERE))
YOFF = 250.0                                   # world Y -> Blender Y shift (map centre)
HP, HV = 15.0, 3.0                             # plateau top, volcano headland top (m)
def U(px, py, z=1.0):
    x, y = C.unproject(px, py, z); return (round(x, 2), round(y - YOFF, 2))
def UP(pts, z=1.0): return [U(p[0], p[1], z) for p in pts]
CANOPY_Z = HP + 12.0                            # north edge is only visible as forest canopy -> project at canopy height
def zc(p): return CANOPY_Z if (p[1] < 290 and 270 < p[0] < 1490) else 0.0
def UPC(pts): return [U(p[0], p[1], zc(p)) for p in pts]
def ellpx(cx, cy, rx, ry, n=24): return [(cx + rx*math.cos(2*math.pi*k/n), cy + ry*math.sin(2*math.pi*k/n)) for k in range(n)]

# ---------------- traced shapes (full-res px) ----------------
COAST = [(205,470),(230,560),(240,600),(250,700),(228,800),(232,900),(262,1000),(292,1060),(212,1130),(150,1190),(80,1240),(0,1265),(-150,1300),(-320,1420),
         (-320,2400),(1990,2400),(1960,1792),(1930,1700),(1880,1600),(1840,1520),(1822,1420),(1832,1330),(1900,1240),(1960,1180),(2010,1140),(2080,1080),(2140,1000),
         (2180,950),(2200,850),(2190,780),(2160,700),(2100,650),(2070,610),(2110,560),(2145,500),(2140,420),(2110,350),(2060,310),(1950,280),(1800,265),(1700,275),
         (1620,295),(1590,330),(1545,345),(1510,330),(1490,260),(1480,235),(1450,195),(1350,160),(1200,130),(1000,108),(800,102),(650,120),(520,150),(420,180),(330,225),(285,285),(250,350),(215,420)]
COAST_Z = 0.0
PLATEAU_S = [(300,438),(400,452),(500,470),(600,490),(700,500),(800,505),(870,495),(905,470),(1010,445),(1100,420),(1150,415),(1185,418),
           (1230,410),(1300,385),(1400,330),(1450,280),(1482,242)]            # cliff TOP edge (z = HP)
PLATEAU_C = [(1500,300),(1490,258),(1478,232),(1448,192),(1350,156),(1200,126),(1000,104),(800,98),(650,116),(520,146),(420,176),(330,221),(282,282),(246,348),(210,420),(198,470),(232,478)]  # sea-level cliff foot
PLATEAU = PLATEAU_S + PLATEAU_C
RAMP_ROAD = [(832,688),(842,640),(870,595),(930,525),(985,465),(1010,438),(995,405),(940,380),(880,365)]
STAIRS = [(880,590),(1030,422)]
CLEARING = [(830,300),(1000,300),(1020,360),(1000,410),(900,410),(830,380)]
PLATEAU_STREAM = [(990,290),(1040,322),(1084,346),(1086,362),(1120,378),(1160,396),(1196,420)]
FALL_TOP, FALL_BASE = (1200,420), (1200,515)
POOL = [(1130,525),(1230,512),(1335,540),(1345,590),(1260,612),(1160,605),(1115,565)]
LILY = [(1395,545),(1500,530),(1600,548),(1655,598),(1600,640),(1480,642),(1405,610)]
RIVER = [(1185,590),(1100,615),(1000,632),(920,652),(880,692),(862,742),(830,790),(770,822),(700,862),(620,920),(540,960),(460,1000),(390,1040),(330,1078),(268,1110),(190,1145),(120,1180)]
RIVER_W = [8.0,7.0,7.0,7.0,7.0,7.0,7.5,7.5,8.0,8.0,8.5,8.5,9.0,9.0,10.0,12.0,14.0]   # metres
SWAMP = [(330,600),(450,598),(600,615),(760,640),(822,682),(822,760),(760,792),(680,850),(600,930),(520,968),(440,1000),(330,1000),(298,900),(300,700)]
ALGAE = [(470,690),(560,668),(680,678),(705,720),(640,762),(560,772),(482,760)]
DARK_POOLS = [ellpx(482,860,42,38), ellpx(590,850,48,22), ellpx(700,790,30,18)]
MUD = [(440,1065),(520,995),(620,945),(720,885),(800,835),(858,785),(905,800),(885,880),(800,950),(700,1012),(600,1062),(500,1102),(430,1112)]
FOOTPRINTS = [(560,1040),(600,1020),(640,1000),(680,985),(720,965),(760,940),(800,915),(840,890),(870,860),(835,820),(870,800)]
PUDDLES = [ellpx(585,1080,40,14), ellpx(720,985,32,12), ellpx(812,825,25,12), ellpx(440,1130,35,14)]
JUNGLE = [(1430,350),(1520,340),(1590,335),(1600,450),(1615,560),(1520,555),(1440,520),(1380,470),(1340,420)]
HEADLAND = [(1600,320),(1700,290),(1800,282),(1950,292),(2062,302),(2128,345),(2162,420),(2168,500),(2128,572),(2082,614),(1990,598),(1900,603),(1800,598),(1700,582),(1612,562),(1592,450)]
CONE_C = (1885,418); CONE_PEAK = (1900,290); CONE_FOOT_L, CONE_FOOT_R = (1700,410), (2060,430)
LAVA = [(1608,432),(1700,418),(1800,428),(1880,462),(1905,522),(1852,562),(1760,552),(1660,522),(1600,482)]
LAVA_STREAMS = [[(1860,315),(1850,350),(1838,385),(1825,420)], [(1918,308),(1922,340),(1930,370)]]
HILL = dict(c=(1600,690), foot=[(1350,640),(1460,600),(1600,590),(1720,610),(1780,680),(1740,760),(1600,780),(1450,760),(1360,710)], h=5.5, crag=(1665,670))
DESERT = [(1700,640),(1800,600),(1900,610),(2000,600),(2068,602),(2100,650),(2150,700),(2140,800),(2120,900),(2080,980),(2000,1050),(1940,1060),(1850,1050),(1760,1000),(1700,900),(1680,800),(1660,700)]
DUNES = [((1950,880),40,3.0),((2050,820),30,2.2),((1830,830),35,2.0),((2000,950),30,1.8)]   # (px, radius m, height m)
MESAS = [dict(name="mesa_big", px=(1995,760), top=650, w=130, kind="tall"), dict(name="mesa_small", px=(1905,790), top=700, w=70, kind="tall"),
         dict(name="mesa_front", px=(1855,1048), top=900, w=150, kind="tall"), dict(name="arch", px=(2050,842), top=760, w=100, kind="arch")]
SW_HILL = dict(c=(470,1650), r=28.0, h=4.0); S_HILL2 = dict(c=(1500,1700), r=26.0, h=2.0); W_HILL = dict(c=(180,1450), r=22.0, h=2.5)
DRY = [ellpx(1350,760,110,45), ellpx(1000,1080,140,70), ellpx(1700,690,70,40), ellpx(560,1700,90,40)]
ROADS = [ # (px polyline, width m)
  ([(1200,1460),(1200,1792),(1200,2400)], 6.5),
  ([(1240,1230),(1240,960),(1228,885),(1170,840),(1060,800),(960,768),(950,760)], 6.0),
  ([(832,688),(842,640),(870,595),(930,525),(985,465),(1010,438),(995,405),(940,380),(880,365)], 5.5),
  ([(1075,1350),(800,1350),(768,1368),(762,1402),(775,1440),(805,1457),(1075,1457)], 3.2),
  ([(1325,1350),(1555,1350),(1585,1372),(1592,1402),(1580,1435),(1550,1457),(1325,1457)], 3.2),
  ([(560,1580),(520,1620),(470,1650),(360,1690),(260,1700)], 2.0), ([(620,1500),(600,1550),(560,1580)], 2.0)]
BRIDGE = [(825,690),(950,757)]
PLAZA = [(1075,1228),(1325,1228),(1325,1460),(1075,1460)]
PADS = [[(805,1265),(1075,1265),(1075,1336),(805,1336)], [(810,1372),(1070,1372),(1070,1440),(810,1440)],
        [(1325,1272),(1505,1272),(1505,1336),(1325,1336)], [(1325,1380),(1505,1380),(1505,1445),(1325,1445)]]
FENCE_RING = dict(c=(1660,1145), rpx=60)
PIERS = [[(1812,1258),(1930,1305)], [(255,710),(300,712)]]
REEFS = [ellpx(130,1050,110,70), ellpx(2000,1450,120,200), ellpx(2080,1650,130,140), ellpx(2180,690,90,60), ellpx(2240,1080,70,60)]
# rocks: (px, py, kind, count, spread_m, size_m)
ROCKS = [((215,540),"coast",9,6,2.6),((240,1150),"coast",4,4,1.8),((2050,1095),"coast",10,9,3.2),((1940,1705),"coast",9,8,3.0),((2110,460),"coast",14,14,3.0),
         ((1530,320),"coast",6,5,2.4),((1280,770),"circle",9,0,1.8),((1190,940),"ground",7,4,1.4),((1500,680),"ground",14,22,1.6),((1700,700),"ground",8,10,1.4),
         ((1050,640),"ground",6,6,1.2),((1300,580),"high",4,5,1.6),((700,1000),"mud",1,0,2.5),((1460,1020),"ground",2,2,1.2),((300,1210),"coast",3,3,1.6),
         ((450,430),"high",8,25,1.4),((900,250),"high",6,25,1.3),((1250,250),"high",6,20,1.3),((1700,470),"lava",10,20,2.0),((2000,470),"lava",12,18,2.2),
         ((1660,330),"lava",4,8,2.0),((1880,1060),"desert",4,8,1.6),((2000,1000),"desert",4,6,1.4),((1760,620),"ground",6,10,1.3),((1360,610),"ground",5,8,1.4)]
DEAD_TREES = [(1650,300),(1740,282),(1678,372),(1862,540),(1950,512),(2000,520),(1640,520),(1760,540)]
DRIFTWOOD = [(265,920),(108,1310),(1740,1340),(1730,1530),(1748,1460)]
# forests / plant regions (px polygons, z=1 unless given)
FOREST = dict(
  plateau=PLATEAU, sw_woods=[(180,1230),(760,1230),(760,1300),(720,1480),(560,1500),(330,1460),(180,1330)],
  s_belt_w=[(800,1470),(1080,1470),(1080,1600),(800,1600)], s_belt_e=[(1330,1470),(1680,1470),(1680,1560),(1330,1560)],
  se_woods=[(1560,1230),(1720,1230),(1720,1460),(1590,1460)], south_far=[(-300,1560),(1150,1560),(1150,2400),(-300,2400)],
  south_far_e=[(1250,1580),(1960,1580),(1960,2400),(1250,2400)], palms_w=[(250,600),(330,600),(330,1000),(280,1000)],
  palms_sw=[(140,1210),(330,1170),(330,1240),(160,1280)], palms_e=[(1690,1140),(1800,1140),(1800,1520),(1700,1520)],
  jungle=JUNGLE, swamp=SWAMP, desert=DESERT, headland=HEADLAND)

# ---------------- grid + rasterising ----------------
CELL = 2.0
def bounds():
    pts = [U(p[0], p[1], zc(p)) for p in COAST if 0 <= p[0] <= 2400 and p[1] <= 1792]; xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    xs += [U(0, 1792, 0)[0], U(2400, 1792, 0)[0]]
    return min(xs), max(xs), U(1200, 1792)[1], max(ys)
def main():
    x0, x1, y0, y1 = bounds(); M = 14.0
    gx0 = math.floor((x0 - M)/CELL)*CELL; gx1 = math.ceil((x1 + M)/CELL)*CELL; gy0 = math.floor(y0/CELL)*CELL; gy1 = math.ceil((y1 + M)/CELL)*CELL
    W, H = int((gx1-gx0)/CELL), int((gy1-gy0)/CELL); SS = 4
    def raster(polys, lines=()):
        im = Image.new("L", (W*SS, H*SS), 0); d = ImageDraw.Draw(im)
        tr = lambda x, y: ((x-gx0)/CELL*SS, (gy1-y)/CELL*SS)
        for p in polys: d.polygon([tr(*q) for q in p], fill=255)
        for pl, w in lines:
            q = [tr(*a) for a in pl]; d.line(q, fill=255, width=max(1, int(w/CELL*SS)), joint="curve")
            for a in q: r = w/CELL*SS/2; d.ellipse([a[0]-r, a[1]-r, a[0]+r, a[1]+r], fill=255)
        a = np.asarray(im, float).reshape(H, SS, W, SS).mean(axis=(1, 3))[::-1]; return a > 127
    Z = dict(ocean=0, shelf=1, sand=2, grass=3, grass_lush=4, grass_dry=5, dirt=6, rock=7, mud=8, plateau=9, cliff=10, swamp=11, swamp_water=12,
             desert=13, basalt=14, lava=15, river=16, pond=17, jungle=18, reef=19, pad=20, ramp=21, headland=22, cone=23, forest=24)
    land = raster([UPC(COAST)]); zone = np.where(land, Z["grass"], Z["ocean"]).astype(np.uint8)
    put = lambda m, k: zone.__setitem__(m & land, Z[k])
    put(raster([UP(FOREST["sw_woods"]), UP(FOREST["south_far"]), UP(FOREST["south_far_e"])]), "grass_lush")
    put(raster([UP(p) for p in DRY]), "grass_dry")
    put(raster([UP(SWAMP, .5)]), "swamp"); put(raster([UP(ALGAE, .2)] + [UP(p, .2) for p in DARK_POOLS]), "swamp_water")
    put(raster([UP(MUD, .6)]), "mud"); put(raster([UP(JUNGLE)]), "jungle")
    put(raster([UP(HEADLAND, HV)]), "headland"); put(raster([UP(LAVA, HV)]), "lava")
    cc = U(*CONE_C, HV); R = (U(*CONE_FOOT_R, HV)[0] - U(*CONE_FOOT_L, HV)[0])/2
    put(raster([[(cc[0]+R*math.cos(a/12*math.pi), cc[1]+R*0.95*math.sin(a/12*math.pi)) for a in range(24)]]), "cone")
    put(raster([UP(DESERT)]), "desert")
    plat_px = UP(PLATEAU_S, HP) + [U(p[0], p[1], zc(p) if zc(p) else -0.3) for p in PLATEAU_C]
    put(raster([plat_px]), "plateau")
    put(raster([], [(UP(RIVER, .3), 7.0)]), "river"); put(raster([UP(POOL, 0), UP(LILY, .5)]), "pond")
    put(raster([UP(PLAZA)], [(UP(pl), w) for pl, w in ROADS]), "dirt"); put(raster([UP(p) for p in PADS]), "pad")
    sea = ~land; reef = raster([UP(p, -1) for p in REEFS]) & sea; zone[reef] = Z["reef"]
    # shelf: sea within 3 cells of land
    from itertools import product
    near = np.zeros_like(land)
    for dj, di in product(range(-3, 4), repeat=2):
        near |= np.roll(np.roll(land, dj, 0), di, 1)
    zone[sea & near & ~reef] = Z["shelf"]
    def chamfer(mask):
        d = np.where(mask, 0.0, 99.0)
        for _ in range(40):
            p = np.pad(d, 1, constant_values=99.0)
            d = np.minimum.reduce([d, p[:-2,1:-1]+1, p[2:,1:-1]+1, p[1:-1,:-2]+1, p[1:-1,2:]+1, p[:-2,:-2]+1.41, p[2:,2:]+1.41, p[:-2,2:]+1.41, p[2:,:-2]+1.41])
        return d
    dist_land = chamfer(land); dist_water = chamfer(sea)
    shapes = dict(
        coast=UPC(COAST), plateau=plat_px, ramp_road=[list(U(*p, [1.3, 1.6, 2.5, 7.0, 12.0, HP, HP, HP, HP][k])) + [[1.3, 1.6, 2.5, 7.0, 12.0, HP, HP, HP, HP][k]] for k, p in enumerate(RAMP_ROAD)],
        stairs=[U(*STAIRS[0], 2), U(*STAIRS[1], HP)], clearing=UP(CLEARING, HP), plateau_stream=UP(PLATEAU_STREAM, HP),
        fall_top=U(*FALL_BASE, 0.0), fall_base=U(*FALL_BASE, 0.0), pool=UP(POOL, 0), lily=UP(LILY, .5),
        river=UP(RIVER, .3), river_w=RIVER_W, swamp=UP(SWAMP, .5), algae=UP(ALGAE, .2), dark_pools=[UP(p, .2) for p in DARK_POOLS],
        mud=UP(MUD, .6), footprints=UP(FOOTPRINTS, .6), puddles=[UP(p, .6) for p in PUDDLES], jungle=UP(JUNGLE), headland=UP(HEADLAND, HV),
        cone=dict(c=U(*CONE_C, HV), r=round(R*1.15, 2), peak_h=round(C.height_for(CONE_PEAK[0], CONE_C[1], CONE_PEAK[1], HV)*1.25 + HV, 2)),
        lava=UP(LAVA, HV), lava_streams=[[U(p[0], p[1], HV + 12*(1-k/(len(s)-1))) for k, p in enumerate(s)] for s in LAVA_STREAMS],
        hill=dict(c=U(*HILL["c"]), foot=UP(HILL["foot"]), h=HILL["h"], crag=U(*HILL["crag"], 3)),
        desert=UP(DESERT), dunes=[dict(c=U(*p), r=r, h=h) for p, r, h in DUNES],
        mesas=[dict(name=m["name"], kind=m["kind"], c=U(*m["px"]), h=round(C.height_for(m["px"][0], m["px"][1], m["top"], 1.0)*0.82, 1),
                    w=round(abs(U(m["px"][0] + m["w"]/2, m["px"][1])[0] - U(m["px"][0] - m["w"]/2, m["px"][1])[0]), 1)) for m in MESAS],
        hills=[dict(c=U(*h_["c"]), r=h_["r"], h=h_["h"]) for h_ in (SW_HILL, S_HILL2, W_HILL)], dry=[UP(p) for p in DRY],
        roads=[dict(pts=UP(pl, 1.2), w=w) for pl, w in ROADS], bridge=UP(BRIDGE, 1.0), plaza=UP(PLAZA, 1.2), pads=[UP(p, 1.2) for p in PADS],
        fence_ring=dict(c=U(*FENCE_RING["c"]), r=round(abs(U(FENCE_RING["c"][0] + FENCE_RING["rpx"], FENCE_RING["c"][1])[0] - U(*FENCE_RING["c"])[0]), 2)),
        piers=[UP(p, 0) for p in PIERS], reefs=[UP(p, -1) for p in REEFS],
        rocks=[dict(c=U(*p, HV if k == "lava" else (HP if k == "high" else 1)), kind=k, n=n, spread=s, size=sz) for p, k, n, s, sz in ROCKS],
        dead_trees=[U(*p, HV) for p in DEAD_TREES], driftwood=UP(DRIFTWOOD, 0.3),
        forest={k: UP(v, HP if k == "plateau" else (HV if k == "headland" else 1)) if k != "plateau" else plat_px for k, v in FOREST.items()})
    cam = dict(location=[0.0, C.CY - YOFF, C.HC], pitch_deg=C.PITCH, lens=C.LENS, sensor=C.SENSOR, res=[2400, 1792])
    out = dict(version="v02", note="camera-matched; Blender metres; grid rows south->north", grid=[W, H], cell_m=CELL, grid_origin_m=[gx0, gy0],
               origin_cell=[-gx0/CELL, -gy0/CELL], dist_land=np.round(np.minimum(dist_land, 30), 1).tolist(), dist_water=np.round(np.minimum(dist_water, 30), 1).tolist(),
               sea_level_m=-0.45, plateau_m=HP, headland_m=HV, zones=Z, zone=zone.tolist(), shapes=shapes, camera=cam)
    os.makedirs(os.path.join(ROOT, "02_Environment", "Island"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "02_Environment", "Island", "island_map_v02.json"), "w"))
    print("grid", W, H, "origin", gx0, gy0, "extent", gx1, gy1); print("cone", shapes["cone"]); print("mesas", shapes["mesas"])
    print("fall", shapes["fall_top"], shapes["fall_base"], "ring", shapes["fence_ring"]); print({k: int((zone == v).sum()) for k, v in Z.items()})
main()
