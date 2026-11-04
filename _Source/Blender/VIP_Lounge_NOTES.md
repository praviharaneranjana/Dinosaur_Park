# VIP Lounge

File: VIP_Lounge.blend (scene VIP_Lounge). This is the official VIP lounge; the earlier ChatGPT version was removed on 4 Nov 2026.
Front is -Y, Z up, metres. Root: VL_ROOT at base centre. Core 16 x 9 m, two storeys, reserve ~20 x 13 m incl. stair and planters.

Shell: cream plinth, footprint pier (three-toe print engraved by boolean, darker VL_Footprint faces), recessed glass entrance with green canopy, amber glow strip, two lanterns, carpet runner, ramp, curved walkway, blank sign stand.
Glass: VL_Glass is transparent teal (alpha 0.22, BLENDED) so the interior shows. In Unity use a URP transparent material; watch sort order on mobile.
Wave roof: high over the cafe (7.3 m), dips to 6.5 m at the right. Green fascia, amber line, timber soffit, raised cream rim. Nothing on the roof by design.
Upper left: open-air cafe deck at the top of the curved timber stair, 5 bistro sets, bench, planters, hanging lanterns, steel railing, two roof posts.
Interior ground: VIP bar (marble top, brass rail, backlit bottle wall), 6 bar stools, 4 lounge sets, 3 bistro tables, velvet booth, host stand, plants, pendants.
Interior upper: 5 dining tables (20 chairs), champagne bar + stools, sofa lounge, pendants.
Kit (linked duplicates of Hangar.blend CMP parts): right = AC, vent, drain, meter, ground box, upper lamp, timber slats; back = staff door + canopy, lamp, 3+3 windows, vent, AC, meter + elbow, 2 drains; left = 2 windows, vent, meter, lamp.
Sockets: SOCKET_ACUnit_*, SOCKET_Vent_*, SOCKET_MeterBox_*, SOCKET_WallLamp_*, SOCKET_Window_* in VL_Sockets. No solar socket (roof kept clean).
Triangles: ~34k total, interior ~12k (VL_Interior collection can be a near-camera LOD). Presentation_only (sun, floor, cameras) and CMP_Library are not for export.
Renders: renders/VIP_Lounge_front.png, renders/VIP_Lounge_rear.png.
