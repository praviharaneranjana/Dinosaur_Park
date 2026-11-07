"""Dino Park Tycoon - ISLAND LAYOUT v01 (pure python, no Blender needed).
Hand-traced from the reference aerial image (pixel polygons, ~2213x1652) into the 96x72 tile grid (1 tile = 2 m).
Grid: x 0..95 west->east, y 0..71 south->north, cell centre = (i+0.5, j+0.5). Blender: X=(gx-48)*2 m, Y=(gy-36)*2 m, Z up, +Y = north.
Outputs: 02_Environment/Island/island_map_v01.json (single source of truth for Blender AND Unity) + renders/island/ISL_zonemap_v01.png
Run: python3 isl_layout.py [ROOT]"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
W, H, SS = 96, 72, 4
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/mnt/Blender")

# ---------- reference pixel -> grid ----------
_YK = [(90,66),(250,59.5),(450,51),(650,42),(900,31),(1250,18),(1650,7),(1750,4.5),(1800,3.5)]
def _s(py): return 0.0462 - (py-430)*5e-6
def P(px, py):
    return (50 + (px-1100)*_s(py), float(np.interp(py, [a for a,_ in _YK], [b for _,b in _YK])))
def PP(pts): return [P(*p) for p in pts]
def ell(cx, cy, rx, ry, n=28, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    return [P(cx + rx*math.cos(2*math.pi*k/n)*c - ry*math.sin(2*math.pi*k/n)*s,
              cy + rx*math.cos(2*math.pi*k/n)*s + ry*math.sin(2*math.pi*k/n)*c) for k in range(n)]

Z = dict(ocean=0, shelf=1, sand=2, grass_short=3, grass_lush=4, grass_dry=5, dirt=6, rock=7, mud=8, plateau=9, cliff=10,
         swamp=11, swamp_water=12, desert=13, basalt=14, lava=15, river=16, pond=17, jungle=18, reef=19, pad=20, ramp=21)
ZN = {v: k for k, v in Z.items()}
COL = {0:(20,70,120),1:(60,170,190),2:(232,210,160),3:(120,170,60),4:(70,130,50),5:(190,170,70),6:(170,130,80),7:(130,130,125),8:(90,60,40),
       9:(50,100,40),10:(80,75,70),11:(70,95,45),12:(60,120,90),13:(225,150,80),14:(60,55,55),15:(255,110,20),16:(60,160,200),17:(70,170,170),
       18:(40,120,60),19:(230,90,150),20:(150,150,150),21:(180,140,90)}

LAND = PP([(190,440),(215,340),(300,230),(420,150),(560,100),(700,80),(850,85),(1000,120),(1150,170),(1300,210),(1390,270),(1420,300),(1520,290),
  (1650,250),(1760,250),(1880,290),(1960,370),(1985,470),(1930,560),(1890,600),(1960,680),(2020,790),(2030,880),(2000,960),(1930,1010),(1800,1050),
  (1700,1110),(1660,1200),(1620,1290),(1625,1390),(1670,1470),(1720,1550),(1750,1650),(1760,1780),(-10,1780),(-10,1200),(100,1090),(220,990),(250,960),
  (240,900),(215,840),(200,760),(215,650),(235,560),(215,520)])
PLATEAU = PP([(215,430),(240,330),(330,220),(470,140),(640,95),(820,85),(1000,125),(1180,185),(1300,225),(1385,280),(1370,330),(1250,370),(1170,395),
  (1130,412),(1040,420),(1000,400),(930,420),(860,470),(780,520),(700,500),(640,500),(560,505),(470,500),(330,480),(240,455)])
RAMP = PP([(745,610),(800,600),(940,470),(1030,395),(1005,365),(940,345),(905,385),(840,465),(770,555)])
RAMP_A, RAMP_B = P(775,590), P(985,395)       # low end, high end
SWAMP = PP([(280,520),(400,540),(520,555),(650,575),(740,620),(760,680),(690,730),(600,760),(520,800),(480,860),(400,930),(320,950),(270,990),(245,900),(230,780),(240,660)])
POOLS = [ell(520,670,125,48,rot=-0.05), ell(440,780,42,55), ell(470,880,70,50,rot=0.4)]
MUD = PP([(420,1010),(480,975),(600,930),(700,880),(790,820),(850,760),(870,730),(820,725),(780,770),(700,840),(580,900),(470,950),(390,990)])
JUNGLE_NE = PP([(1230,330),(1400,300),(1430,420),(1330,480),(1240,460)])
VOLCANO_LAND = PP([(1420,300),(1520,290),(1650,255),(1760,255),(1880,290),(1960,370),(1985,470),(1930,560),(1850,572),(1700,548),(1560,540),(1450,520),(1410,430)])
LAVA = PP([(1470,420),(1560,400),(1650,410),(1720,440),(1700,492),(1600,482),(1500,476)])
DESERT = PP([(1580,700),(1680,690),(1770,640),(1890,650),(1960,700),(1990,800),(1960,900),(1880,930),(1790,940),(1700,900),(1650,820),(1600,760)])
RIVER_UP = [(960,310),(1010,335),(1060,372),(1095,420)]
RIVER = [(1095,470),(1140,520),(1085,568),(1000,605),(900,640),(810,668),(720,710),(620,745),(540,800),(480,870),(430,930),(370,990),(300,1030),(215,1052)]
POND = ell(1270,572,88,32,rot=-0.1)
DRY = [ell(1230,745,150,45), ell(750,1040,110,60), ell(1330,880,60,70), ell(1020,1080,70,40), ell(1500,455,95,40)]
LUSH = [PP([(0,1380),(700,1380),(1050,1450),(1050,1780),(0,1780)]), ell(1150,1000,0,0)] # second is dummy
HILLS = [dict(c=(1460,640), rx=170, ry=80, h=2.6, rock=ell(1500,610,105,42)), dict(c=(170,1560), rx=230, ry=100, h=1.5, rock=None)]
VOLCANO_C = (1740,345); VOLCANO_R = (190,110); VOLCANO_H = 8.0
ROADS = [  # (polyline px, width in cells)
 ([(1105,1760),(1105,1340)],3),([(1105,1170),(1140,1100),(1150,900),(1120,820),(1050,770),(960,720),(870,680)],3),
 ([(990,1240),(750,1240),(692,1282),(702,1322),(762,1345),(990,1345)],2),([(1225,1240),(1400,1240),(1460,1282),(1450,1322),(1400,1345),(1225,1345)],2),
 ([(800,600),(900,480),(990,390),(950,350),(830,312)],2)]
PLAZA = PP([(990,1170),(1225,1170),(1225,1345),(990,1345)])
PADS = [PP([(740,1170),(995,1170),(995,1232),(740,1232)]), PP([(1220,1170),(1392,1170),(1392,1232),(1220,1232)]),
        PP([(745,1265),(985,1265),(985,1332),(745,1332)]), PP([(1222,1268),(1385,1268),(1385,1332),(1222,1332)])]
REEF = [ell(110,1050,110,70), ell(1850,1330,150,280,rot=0.15), ell(1890,1560,110,140)]
ROCKY_COAST = [VOLCANO_LAND, PLATEAU]   # no sand on these coasts
START = PP([(650,1120),(1500,1120),(1500,1780),(650,1780)])
REGIONS = [  # id, name, polygon, unlocked, clear cost per cell (placeholder)
 ("start","Starting meadow",START,True,0),("sw_woods","South-west woods",PP([(-10,1100),(650,1100),(650,1780),(-10,1780)]),False,3),
 ("se_shore","South-east shore",PP([(1500,1100),(1790,1100),(1790,1780),(1500,1780)]),False,3),
 ("plateau","Forest plateau",PLATEAU+[],False,6),("swamp","West swamp",SWAMP,False,5),("mud_valley","Footprint mud valley",MUD,False,4),
 ("volcano","Volcano island",VOLCANO_LAND,False,8),("desert","Desert shore",DESERT,False,6),("jungle_ne","Waterfall jungle",JUNGLE_NE,False,5),
 ("meadow_north","Central meadow",PP([(430,590),(1600,590),(1700,1120),(430,1120)]),False,2)]

def draw_poly(cv, pts, v): cv.polygon([(x*SS, (H-y)*SS) for x, y in pts], fill=v)
def draw_line(cv, pts, wcells, v):
    xy = [(x*SS, (H-y)*SS) for x, y in pts]; cv.line(xy, fill=v, width=max(1, int(wcells*SS)), joint="curve")
    r = wcells*SS/2
    for x, y in xy: cv.ellipse([x-r, y-r, x+r, y+r], fill=v)
def canvas(): im = Image.new("L", (W*SS, H*SS), 0); return im, ImageDraw.Draw(im)
def down(im):
    a = np.asarray(im).reshape(H, SS, W, SS).transpose(0, 2, 1, 3).reshape(H, W, SS*SS)[::-1]
    out = np.zeros((H, W), np.uint8)
    for j in range(H):
        for i in range(W): out[j, i] = np.bincount(a[j, i], minlength=22).argmax()
    return out
def mask_of(pts_list, lines=None):
    im, cv = canvas()
    for p in pts_list: draw_poly(cv, p, 255)
    for pl, w in (lines or []): draw_line(cv, [P(*q) for q in pl], w, 255)
    a = np.asarray(im).reshape(H, SS, W, SS).mean(axis=(1, 3))[::-1]
    return a > 127
def dist_from(mask):  # BFS chamfer distance in cells to nearest True
    d = np.full((H, W), 99.0); q = [(j, i) for j in range(H) for i in range(W) if mask[j, i]]
    for j, i in q: d[j, i] = 0
    k = 0
    while k < len(q):
        j, i = q[k]; k += 1
        for dj, di, c in ((1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.41),(1,-1,1.41),(-1,1,1.41),(-1,-1,1.41)):
            jj, ii = j+dj, i+di
            if 0 <= jj < H and 0 <= ii < W and d[jj, ii] > d[j, i]+c: d[jj, ii] = d[j, i]+c; q.append((jj, ii))
    return d

def build():
    land = mask_of([LAND]); zone = np.zeros((H, W), np.uint8)
    def paint(m, v, only=None):
        sel = m if only is None else (m & only(zone)); zone[sel] = v
    paint(land, Z["grass_short"])
    paint(mask_of([LUSH[0]]) & land, Z["grass_lush"])
    for p in DRY: paint(mask_of([p]) & land, Z["grass_dry"])
    plateau = mask_of([PLATEAU]); ramp = mask_of([RAMP])
    paint(plateau, Z["plateau"])
    paint(mask_of([SWAMP]) & land, Z["swamp"]); paint(mask_of([JUNGLE_NE]), Z["jungle"])
    paint(mask_of(POOLS) & land, Z["swamp_water"])
    paint(mask_of([MUD]), Z["mud"])
    vol = mask_of([VOLCANO_LAND]); paint(vol, Z["basalt"]); paint(mask_of([ell(1530,450,95,38)]) & vol, Z["grass_dry"]); paint(mask_of([LAVA]), Z["lava"])
    paint(mask_of([DESERT]) & land, Z["desert"])
    for hl in HILLS:
        if hl["rock"]: paint(mask_of([hl["rock"]]), Z["rock"])
    paint(mask_of([RAMP]), Z["ramp"])
    roads = mask_of([PLAZA], [(pl, w) for pl, w in ROADS]) & land
    paint(roads & ~plateau | (roads & ramp), Z["dirt"]); paint(mask_of([PLAZA]), Z["dirt"])
    for p in PADS: paint(mask_of([p]), Z["pad"])
    # rivers / pond (water zones)
    river = mask_of([], [(RIVER, 2.6), ([(1095,430)]+RIVER[:1], 2.6)]) & land
    river_up = mask_of([], [(RIVER_UP, 2.0)]) & plateau
    paint(river | river_up, Z["river"]); paint(mask_of([POND]) & land, Z["pond"])
    # cliff rim: plateau cells touching non-plateau (not ramp, not river)
    pl_ = zone == Z["plateau"]; rim = np.zeros((H, W), bool)
    for j in range(H):
        for i in range(W):
            if not (plateau[j, i]): continue
            for dj, di in ((1,0),(-1,0),(0,1),(0,-1)):
                jj, ii = j+dj, i+di
                if not (0 <= jj < H and 0 <= ii < W) or (not plateau[jj, ii] and not ramp[jj, ii]): rim[j, i] = True
    rim &= (zone == Z["plateau"]) | (zone == Z["jungle"]); zone[rim & (zone == Z["plateau"])] = Z["cliff"]
    # water shelf + beach
    wat = ~land | np.isin(zone, [Z["river"]]) & False
    dw = dist_from(~land)                  # distance (cells) from open water for land cells
    dl = dist_from(land)                   # distance from land for ocean cells
    rocky = mask_of(ROCKY_COAST)
    sandable = np.isin(zone, [Z["grass_short"], Z["grass_lush"], Z["grass_dry"], Z["swamp"], Z["desert"], Z["mud"], Z["jungle"]])
    zone[land & (dw <= 2.5) & sandable & ~rocky] = Z["sand"]
    zone[~land & (dl <= 4)] = Z["shelf"]
    reef = mask_of(REEF); zone[reef & ~land & (dl <= 8)] = Z["reef"]
    zone[~land & ~reef & (dl > 4)] = Z["ocean"]
    # heights (m, land only; builder smooths)
    h = np.zeros((H, W), np.float32); yy, xx = np.mgrid[0:H, 0:W]; gx, gy = xx+0.5, yy+0.5
    h[plateau] = 4.0
    a, b = np.array(RAMP_A), np.array(RAMP_B); ab = b-a; t = ((gx-a[0])*ab[0] + (gy-a[1])*ab[1])/(ab@ab); t = np.clip(t, 0, 1)
    h = np.where(ramp, 4.0*(t*t*(3-2*t)), h)
    for hl in HILLS:
        cx, cy = P(*hl["c"]); rx, ry = hl["rx"]*_s(hl["c"][1]), hl["ry"]*0.045
        r2 = ((gx-cx)/rx)**2 + ((gy-cy)/ry)**2; h += hl["h"]*np.clip(1-r2, 0, 1)**2
    vc = P(*VOLCANO_C); vrx, vry = VOLCANO_R[0]*_s(VOLCANO_C[1]), VOLCANO_R[1]*0.045
    rr = np.sqrt(((gx-vc[0])/vrx)**2 + ((gy-vc[1])/vry)**2); cone = VOLCANO_H*np.clip(1-rr, 0, 1)**1.5
    cone = np.where(rr < 0.12, cone - 1.2, cone); h += cone*vol
    h[~land] = 0
    # regions
    region = np.full((H, W), -1, np.int16); rdefs = []
    for k, (rid, name, poly, unl, cost) in enumerate(REGIONS):
        m = mask_of([poly]) & land & (region < 0)
        if rid == "start": m = mask_of([poly]) & land
        region[m & (region < 0 if rid != "start" else True)] = k
        rdefs.append(dict(index=k, id=rid, name=name, unlocked=unl, clear_cost_per_cell=cost, cells=int((region == k).sum())))
    region[land & (region < 0)] = len(REGIONS)-1
    return dict(zone=zone, height=h, region=region, rim=rim, land=land, rdefs=rdefs, ramp=ramp, dw=dw, dl=dl)

def features():
    f = []
    def add(t, px, py, **k): x, y = P(px, py); f.append(dict(type=t, x=round(x, 2), y=round(y, 2), **k))
    add("waterfall_big", 1095, 440, rot_deg=180, note="drop 4 m; TRN_Waterfall_Big scaled Z x1.33 or stack"); add("bridge", 810, 668, rot_deg=-20, length_cells=6)
    add("volcano_cone", *VOLCANO_C, radius_cells=[round(VOLCANO_R[0]*_s(VOLCANO_C[1]), 1), round(VOLCANO_R[1]*0.045, 1)], height_m=VOLCANO_H)
    for nm, px, py, sc in (("mesa_big",1835,640,1.0),("mesa_small",1762,690,0.7),("mesa_front",1710,890,0.9),("arch",1885,735,0.8)): add(nm, px, py, scale=sc)
    for px, py in ((1800,780),(1700,810),(1850,850)): add("dune", px, py)
    add("stone_circle", 1250, 710); add("pier", 1760, 1180, rot_deg=-30); add("pier", 250, 655, rot_deg=90); add("fence_ring", 1520, 1050, radius_cells=3.2)
    add("dead_tree_group", 1500, 400); add("bridge_stairs", 880, 470, note="timber stairs beside ramp road")
    add("start_plaza", 1105, 1255, size_cells=[12, 9]); add("vehicle_bay_hint", 870, 1200)
    return f

def scatter_regions():
    mk = lambda name, poly, mix, dens, **k: dict(name=name, poly=[[round(x, 2), round(y, 2)] for x, y in poly], mix=mix, per_100m2=dens, **k)
    return [
     mk("plateau_forest", PLATEAU, dict(Broadleaf=.34, Conifer=.28, FernTree=.06, Palm=.04, Bushes=.12, Ferns=.10, StumpsLogs=.02, Flowers=.04), 5.5, only_zones=["plateau"]),
     mk("plateau_ginkgo", PP([(620,300),(820,300),(830,420),(640,440)]), dict(Ginkgo=.7, Bushes=.2, Flowers=.1), 5.0, only_zones=["plateau"]),
     mk("plateau_giants", PP([(480,130),(900,110),(900,260),(480,260)]), dict(GiantTree=1.0), 0.45, only_zones=["plateau"], min_dist_m=14),
     mk("jungle_ne", JUNGLE_NE, dict(Palm=.35, FernTree=.2, Cycad=.15, Ferns=.2, Bushes=.1), 5.0, only_zones=["jungle"]),
     mk("swamp", SWAMP, dict(Palm=.18, FernTree=.14, Cycad=.1, Ferns=.2, Horsetails=.12, Mangrove=.1, Bushes=.08, Flowers=.08), 4.5, only_zones=["swamp"]),
     mk("marsh_reeds", PP([(380,700),(560,700),(560,860),(400,880)]), dict(ReedsCattails=1.0), 6.0, only_zones=["swamp"]),
     mk("sw_woods", PP([(180,1090),(700,1090),(700,1350),(500,1385),(200,1260)]), dict(Broadleaf=.5, Conifer=.2, Bushes=.2, Hedges=0.0, Ferns=.1), 4.0, only_zones=["grass_short","grass_lush"]),
     mk("se_woods", PP([(1430,1150),(1570,1150),(1570,1350),(1430,1350)]), dict(Broadleaf=.45, Conifer=.3, Bushes=.25), 4.0, only_zones=["grass_short","grass_lush"]),
     mk("south_belt_w", PP([(700,1345),(1060,1345),(1060,1460),(700,1460)]), dict(Broadleaf=.5, Bushes=.3, Conifer=.2), 2.4, only_zones=["grass_short","grass_lush"]),
     mk("south_belt_e", PP([(1150,1345),(1520,1345),(1520,1450),(1150,1450)]), dict(Broadleaf=.5, Bushes=.3, Conifer=.2), 2.4, only_zones=["grass_short","grass_lush"]),
     mk("south_sparse", PP([(0,1450),(1700,1450),(1700,1780),(0,1780)]), dict(Broadleaf=.35, Bushes=.35, Conifer=.1, Flowers=.2), 0.7, only_zones=["grass_short","grass_lush"]),
     mk("meadow_sparse", PP([(430,590),(1600,590),(1700,1120),(430,1120)]), dict(Bushes=.45, Broadleaf=.15, Flowers=.2, StumpsLogs=.1, Hedges=0.0, Ferns=.1), 0.35, only_zones=["grass_short","grass_lush","grass_dry"]),
     mk("beach_palms", LAND, dict(Palm=0.8, Bushes=0.2), 0.9, only_zones=["sand"]),
     mk("desert_plants", DESERT, dict(DesertPlants=1.0), 1.2, only_zones=["desert"]),
     mk("volcano_dead", VOLCANO_LAND, dict(DeadTrees=.5, StrippedTrees=.3, Palm=.2), 0.9, only_zones=["basalt","grass_dry"]),
     mk("purple_flowers", PP([(300,860),(420,860),(420,930),(300,930)]), dict(Flowers=.7, ToxicBloom=.3), 6.0, only_zones=["swamp","grass_short","grass_lush","sand"]),
     mk("pond_plants", POND, dict(WaterPlants=1.0), 5.0, only_zones=["pond"]),
     mk("pool_plants", sum(POOLS, []), dict(WaterPlants=.6, ToxicBloom=.4), 4.0, only_zones=["swamp_water"]),
     mk("reef", sum(REEF, []), dict(Coral=.5, Kelp=.25, Seaweed=.25), 1.6, only_zones=["reef"]),
     mk("grass_tufts", LAND, dict(GrassPatches=1.0), 1.0, only_zones=["grass_short","grass_lush","grass_dry","plateau"]),
    ]

def main():
    r = build(); zone = r["zone"]
    out = dict(version="v01", grid=[W, H], cell_m=2.0, origin_cell=[48, 36], zones=Z, sea_level_m=-0.45, plateau_m=4.0,
        note="x west->east, y south->north; rows of zone/height/region are listed south (y=0) first. Blender X=(gx-48)*2, Y=(gy-36)*2.",
        zone=zone.tolist(), height_m=np.round(r["height"], 2).tolist(), region=r["region"].tolist(), regions=r["rdefs"],
        dist_water=np.round(np.minimum(r["dw"], 30), 1).tolist(), dist_land=np.round(np.minimum(r["dl"], 30), 1).tolist(),
        rivers=[[list(map(lambda v: round(v, 2), P(*q))) for q in RIVER_UP], [list(map(lambda v: round(v, 2), P(*q))) for q in RIVER]],
        roads=[dict(width_cells=w, pts=[[round(v, 2) for v in P(*q)] for q in pl]) for pl, w in ROADS],
        ramp=dict(low=list(map(lambda v: round(v, 2), RAMP_A)), high=list(map(lambda v: round(v, 2), RAMP_B))),
        cliff_rim=[[int(i), int(j)] for j, i in zip(*np.nonzero(r["rim"] & (zone == Z["cliff"])))],
        features=features(), scatter_regions=scatter_regions(),
        buildable=((np.isin(zone, [Z["grass_short"], Z["grass_lush"], Z["grass_dry"], Z["dirt"], Z["pad"]])) & (r["region"] == 0)).astype(int).tolist())
    os.makedirs(os.path.join(ROOT, "02_Environment", "Island"), exist_ok=True); os.makedirs(os.path.join(ROOT, "renders", "island"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "02_Environment", "Island", "island_map_v01.json"), "w"))
    # preview
    S = 10; im = Image.new("RGB", (W*S, H*S))
    px = im.load(); hh = r["height"]
    for j in range(H):
        for i in range(W):
            c = COL[int(zone[j, i])]; sh = 0.75 + 0.06*hh[j, i]; c = tuple(min(255, int(v*sh)) for v in c)
            for a in range(S):
                for b in range(S): px[i*S+a, (H-1-j)*S+b] = c
    d = ImageDraw.Draw(im)
    for i in range(0, W, 8): d.line([(i*S, 0), (i*S, H*S)], fill=(0, 0, 0), width=1); d.text((i*S+2, 2), str(i), fill=(255, 255, 255))
    for j in range(0, H, 8): d.line([(0, (H-j)*S), (W*S, (H-j)*S)], fill=(0, 0, 0), width=1); d.text((2, (H-j)*S-12), str(j), fill=(255, 255, 255))
    for f in out["features"]:
        x, y = f["x"]*S, (H-f["y"])*S; d.ellipse([x-4, y-4, x+4, y+4], outline=(255, 255, 255), fill=(255, 0, 0)); d.text((x+6, y-5), f["type"], fill=(255, 255, 255))
    for k, (zn, zid) in enumerate(Z.items()):
        d.rectangle([4, 4+k*13+14, 14, 14+k*13+14], fill=COL[zid]); d.text((18, 4+k*13+14), zn, fill=(255, 255, 255))
    im.save(os.path.join(ROOT, "renders", "island", "ISL_zonemap_v01.png"))
    cnt = {ZN[int(k)]: int(v) for k, v in zip(*np.unique(zone, return_counts=True))}
    ch = {0:"~",1:"-",2:".",3:"g",4:"G",5:"y",6:"=",7:"R",8:"m",9:"F",10:"#",11:"s",12:"w",13:"d",14:"b",15:"L",16:"r",17:"p",18:"J",19:"c",20:"P",21:"/"}
    print("\n".join("".join(ch[int(zone[j, i])] for i in range(W)) for j in range(H-1, -1, -1)))
    print(cnt); print([ (x["id"], x["cells"]) for x in r["rdefs"]]); print("cliff rim cells", len(out["cliff_rim"]), "max h", float(r["height"].max()))
main()
