#!/usr/bin/env python3
"""Parametric enclosure for ego-coil, in CadQuery (pip install cadquery).

    python cad/build_cad.py            # writes STL + SVG previews into cad/out/

Parts
  body        box that holds the power stage, Q3, supervisor; EGO dock on the back
  body_lid    screw-on top
  head        shell for the coil's capacitor bank with coil tails out the front
  head_lid

Everything is driven by the dictionaries at the top. Dimensions are mm.
The EGO dock is a POCKET for a bought or separately printed adapter plate,
not a model of the EGO rail (see docs/bom.md); set `dock` to the plate you
have.
"""
import os
import cadquery as cq

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

body = dict(
    L=160, W=95, H=75,          # outer, X = front-back, Y = width, Z = height
    wall=3.0,
    lid_t=3.0,
    corner_r=6.0,
    screw_d=3.2,                # M3 clearance through lid
    boss_d=8.0,
    boss_tap_d=2.5,             # M3 self-tap in boss
)
# ---- EGO dock: a printed plate that the pack slides onto ---------------------
# EVERY value marked MEASURE is a placeholder. Measure your own pack with
# calipers per docs/dock-measurement.md and fill them in before printing.
# Geometry convention for the dock part: pack slides on along +Y, plate lies in
# the XY plane with the rails standing up in +Z, terminals at the +Y end.
rail = dict(
    plate_w=78, plate_l=64, plate_t=5,      # matches the body's recess + 64x44 screw pattern
    rail_spacing=50.0,     # MEASURE: centre-to-centre of the pack's two grooves
    rail_w_top=9.0,        # MEASURE: groove width at the pack's opening
    rail_w_root=6.0,       # MEASURE: neck width (narrowest part of the groove)
    rail_h=6.0,            # MEASURE: groove depth
    rail_l=52,             # length of the rails along the slide direction
    stop_h=10,             # end stop the pack butts against
    latch_w=12.0,          # MEASURE: width of the pack's latch tongue
    latch_depth=3.0,       # MEASURE: how far the tongue drops
    latch_from_end=14.0,   # MEASURE: distance from the end stop to the latch face
    term_pitch=20.0,       # MEASURE: centre spacing of the two power blades
    term_from_end=8.0,     # MEASURE: distance from the end stop to the blade centres
    term_w=7.0, term_t=1.2,    # MEASURE: blade width / thickness (6.3 mm spade fits most)
    term_slot_depth=18,    # depth of the slot that holds the female spade
    clearance=0.3,         # printed-fit allowance, added to groove-side dimensions
)
# ---- EGO dock mounted UNDER the body (pack hangs below, slide axis along X) --
# cad/ego56v_dock.stl is the tool-side interface. Add four countersunk M3
# holes to it in your slicer at these (x, y) positions in the STL's own
# coordinates (origin as the file loads, z up), then it screws to the floor:
DOCK_STL_HOLES = [(34, -10), (34, 20), (-34, -10), (-34, 20)]   # mm, STL frame
DOCK_STL_CENTER_Y = -15.0     # STL y of the footprint centre (bounds -61..31)
dock_under = dict(offset_x=0.0, screw_d=3.2, boss_d=8.0, boss_h=6.0)

dock = dict(                    # legacy: pocket on the rear face for a flat adapter plate
    w=78, h=64, depth=1.5, screw_pitch=(64, 44), screw_d=3.2,   # depth < wall: a locating recess, plate screws through with nuts inside
    cable_hole_d=14,            # B+/B- pass-through inside the pocket
)
heatsink = dict(                # bay on the left side with a fan and exhaust slots
    fan=40, fan_hole=38.5, fan_screw=32, fan_screw_d=3.2,
    slot_w=3, slot_h=35, slot_n=8, slot_pitch=6,
)
front = dict(                   # XT90 panel mount + JST-XH 3-pin for head ID
    xt90_w=22.5, xt90_h=13.0, xt90_screw=30, xt90_screw_d=3.2,
    jst_w=10.5, jst_h=6.5,
)
top = dict(trigger_d=16.2, led_d=5.2, buzzer_d=12.2)
# (Pico is socketed on the main PCB; no separate standoffs)
powerboard = dict(hole_x=92, hole_y=72, standoff_h=10, standoff_d=7, tap_d=2.5)   # pcb/ main board, 100 x 80

head = dict(
    L=70, W=48, H=34,           # outer; X = toward the coil
    wall=2.4, lid_t=2.4, corner_r=4,
    tail_d=7.0, tail_pitch=14,  # 1/4" tube + sleeve clearance
    tail_standoff=10,           # ceramic/silicone standoff width around the tails
    lead_d=10.5,                # twisted 10 AWG pair exit at the back
    jst_w=10.5, jst_h=6.5,
    screw_d=2.5, boss_d=6.5,
)


# ------------------------------------------------------------------ helpers --
def rounded_box(L, W, H, r):
    return cq.Workplane("XY").box(L, W, H).edges("|Z").fillet(r)


def shell_box(L, W, H, wall, r, open_top=True):
    outer = rounded_box(L, W, H, r)
    inner = rounded_box(L - 2 * wall, W - 2 * wall, H, max(r - wall, 0.5)).translate((0, 0, wall))
    return outer.cut(inner)


def corner_points(L, W, inset):
    return [((L / 2 - inset) * sx, (W / 2 - inset) * sy) for sx in (-1, 1) for sy in (-1, 1)]


def bosses(part, L, W, H, wall, boss_d, tap_d, z0):
    pts = corner_points(L, W, wall + boss_d / 2)
    boss = (cq.Workplane("XY").workplane(offset=z0)
            .pushPoints(pts).circle(boss_d / 2).extrude(H - z0 - 0.01))
    hole = (cq.Workplane("XY").workplane(offset=z0 + 2)
            .pushPoints(pts).circle(tap_d / 2).extrude(H))
    return part.union(boss).cut(hole)


def standoffs(part, hx, hy, so_h, so_d, tap_d, center, z0):
    pts = [(center[0] + sx * hx / 2, center[1] + sy * hy / 2) for sx in (-1, 1) for sy in (-1, 1)]
    so = cq.Workplane("XY").workplane(offset=z0).pushPoints(pts).circle(so_d / 2).extrude(so_h)
    hole = cq.Workplane("XY").workplane(offset=z0 + 1).pushPoints(pts).circle(tap_d / 2).extrude(so_h)
    return part.union(so).cut(hole)


# --------------------------------------------------------------------- body --
def build_body():
    b = body
    L, W, H, wall, r = b["L"], b["W"], b["H"], b["wall"], b["corner_r"]
    part = shell_box(L, W, H, wall, r).translate((0, 0, H / 2))
    part = bosses(part, L, W, H, wall, b["boss_d"], b["boss_tap_d"], z0=wall)

    # --- rear face (−X): EGO dock pocket + screw holes + cable hole
    d = dock
    pocket = (cq.Workplane("YZ").workplane(offset=-L / 2 - 0.01)
              .center(0, H / 2).rect(d["w"], d["h"]).extrude(d["depth"] + 0.01))
    part = part.cut(pocket)
    sp = d["screw_pitch"]
    holes = (cq.Workplane("YZ").workplane(offset=-L / 2 - 1).center(0, H / 2)
             .rect(sp[0], sp[1], forConstruction=True).vertices().circle(d["screw_d"] / 2).extrude(wall + d["depth"] + 2))
    part = part.cut(holes)
    cable = (cq.Workplane("YZ").workplane(offset=-L / 2 - 1).center(0, H / 2)
             .circle(d["cable_hole_d"] / 2).extrude(wall + d["depth"] + 2))
    part = part.cut(cable)

    # --- left face (−Y): fan hole + screws; right face (+Y): exhaust slots
    hs = heatsink
    fan_c = (-L / 4, H / 2)
    fan = (cq.Workplane("XZ").workplane(offset=W / 2 + 1).center(*fan_c)  # XZ normal is −Y; offset +W/2 puts us on −Y side
           .circle(hs["fan_hole"] / 2).extrude(-(wall + 2)))
    fan_scr = (cq.Workplane("XZ").workplane(offset=W / 2 + 1).center(*fan_c)
               .rect(hs["fan_screw"], hs["fan_screw"], forConstruction=True).vertices()
               .circle(hs["fan_screw_d"] / 2).extrude(-(wall + 2)))
    part = part.cut(fan).cut(fan_scr)
    slots = cq.Workplane("XZ").workplane(offset=-W / 2 + wall + 1)
    for i in range(hs["slot_n"]):
        x = -L / 4 + (i - (hs["slot_n"] - 1) / 2) * hs["slot_pitch"]
        slots = slots.moveTo(x, H / 2).rect(hs["slot_w"], hs["slot_h"])
    part = part.cut(slots.extrude(-(wall + 2)))

    # --- front face (+X): XT90 + JST
    f = front
    xt = (cq.Workplane("YZ").workplane(offset=L / 2 - wall - 1).center(-12, H / 2)
          .rect(f["xt90_w"], f["xt90_h"]).extrude(wall + 2))
    xts = (cq.Workplane("YZ").workplane(offset=L / 2 - wall - 1).center(-12, H / 2)
           .pushPoints([(-f["xt90_screw"] / 2, 0), (f["xt90_screw"] / 2, 0)])
           .circle(f["xt90_screw_d"] / 2).extrude(wall + 2))
    jst = (cq.Workplane("YZ").workplane(offset=L / 2 - wall - 1).center(22, H / 2)
           .rect(f["jst_w"], f["jst_h"]).extrude(wall + 2))
    part = part.cut(xt).cut(xts).cut(jst)

    # --- dock under the floor: holes + nut bosses matching the STL's drilled holes
    du = dock_under
    pts = [(du["offset_x"] + (y - DOCK_STL_CENTER_Y), x) for x, y in DOCK_STL_HOLES]
    part = part.union(cq.Workplane("XY").workplane(offset=wall - 0.01).pushPoints(pts)
                      .circle(du["boss_d"] / 2).extrude(du["boss_h"]))
    part = part.cut(cq.Workplane("XY").workplane(offset=-1).pushPoints(pts)
                    .circle(du["screw_d"] / 2).extrude(wall + du["boss_h"] + 2))
    part = part.cut(cq.Workplane("XY").workplane(offset=-1).circle(dock["cable_hole_d"] / 2).extrude(wall + 2))

    # --- standoffs on the floor: power board (rear half), Pico (front right)
    pb = powerboard
    part = standoffs(part, pb["hole_x"], pb["hole_y"], pb["standoff_h"], pb["standoff_d"], pb["tap_d"],
                     center=(-25, 0), z0=wall)
    return part


def build_dock():
    """Printed EGO dock. Rails are T/dovetail profiles sized from `rail`."""
    r = rail
    c = r["clearance"]
    plate = (cq.Workplane("XY").box(r["plate_w"], r["plate_l"], r["plate_t"])
             .edges("|Z").fillet(4).translate((0, 0, r["plate_t"] / 2)))
    # screw holes matching the body recess pattern + centre cable hole
    sp = dock["screw_pitch"]
    plate = plate.cut(cq.Workplane("XY").workplane(offset=-1)
                      .rect(sp[0], sp[1], forConstruction=True).vertices()
                      .circle(dock["screw_d"] / 2).extrude(r["plate_t"] + 2))
    plate = plate.cut(cq.Workplane("XY").workplane(offset=-1).circle(dock["cable_hole_d"] / 2)
                      .extrude(r["plate_t"] + 2))

    # rails: trapezoid profile (narrow at root, wide at top) extruded along Y
    top = r["rail_w_top"] - c
    root = r["rail_w_root"] - c
    h = r["rail_h"] - c
    z0 = r["plate_t"]
    y0 = -r["plate_l"] / 2 + 2
    profile = [(-root / 2, 0), (root / 2, 0), (top / 2, h * 0.55), (top / 2, h), (-top / 2, h), (-top / 2, h * 0.55)]
    for sx in (-1, 1):
        x = sx * r["rail_spacing"] / 2
        rl = (cq.Workplane("XZ").workplane(offset=-y0).center(x, z0)
              .polyline(profile).close().extrude(-r["rail_l"]))
        plate = plate.union(rl)

    # end stop across the +Y end, with slots for the two spade terminals
    stop_y = y0 + r["rail_l"] + 3
    stop = (cq.Workplane("XY").workplane(offset=z0)
            .center(0, stop_y).rect(r["rail_spacing"] + top + 6, 6).extrude(r["stop_h"]))
    plate = plate.union(stop)
    for sx in (-1, 1):
        x = sx * r["term_pitch"] / 2
        slot = (cq.Workplane("XY").workplane(offset=z0 + 1)
                .center(x, stop_y - 3 - r["term_from_end"] + r["term_slot_depth"] / 2)
                .rect(r["term_w"] + 0.6, r["term_slot_depth"]).extrude(r["stop_h"]))
        plate = plate.cut(slot)
        # wire channel down through the plate behind each terminal
        plate = plate.cut(cq.Workplane("XY").workplane(offset=-1)
                          .center(x, stop_y - 3 - r["term_from_end"]).circle(2.5).extrude(z0 + 3))

    # latch catch: a ramped block the pack's tongue drops behind
    latch_y = stop_y - 3 - r["latch_from_end"]
    catch = (cq.Workplane("XY").workplane(offset=z0).center(0, latch_y)
             .rect(r["latch_w"] + 2, 4).extrude(r["latch_depth"]))
    plate = plate.union(catch)
    return plate


def build_body_lid():
    b = body
    L, W, wall, r, t = b["L"], b["W"], b["wall"], b["corner_r"], b["lid_t"]
    lid = rounded_box(L, W, t, r).translate((0, 0, t / 2))
    lip = (rounded_box(L - 2 * wall - 0.4, W - 2 * wall - 0.4, 2.0, max(r - wall, 0.5))
           .translate((0, 0, -1.0)))
    lip = lip.cut(rounded_box(L - 2 * wall - 4.4, W - 2 * wall - 4.4, 3.0, max(r - wall - 2, 0.5)).translate((0, 0, -1.0)))
    lid = lid.union(lip)
    pts = corner_points(L, W, wall + b["boss_d"] / 2)
    lid = lid.cut(cq.Workplane("XY").workplane(offset=-2).pushPoints(pts).circle(b["screw_d"] / 2).extrude(t + 3))
    # top features: trigger, LED, buzzer grille
    tp = top
    lid = lid.cut(cq.Workplane("XY").workplane(offset=-2).center(L / 4, 0).circle(tp["trigger_d"] / 2).extrude(t + 3))
    lid = lid.cut(cq.Workplane("XY").workplane(offset=-2).center(L / 4 + 20, -15).circle(tp["led_d"] / 2).extrude(t + 3))
    grille = cq.Workplane("XY").workplane(offset=-2).center(L / 4 + 20, 15)
    grille = grille.pushPoints([(0, 0)] + [(3.5 * dx, 3.5 * dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx, dy) != (0, 0)])
    lid = lid.cut(grille.circle(1.0).extrude(t + 3))
    return lid


# --------------------------------------------------------------------- head --
def build_head():
    h = head
    L, W, H, wall, r = h["L"], h["W"], h["H"], h["wall"], h["corner_r"]
    part = shell_box(L, W, H, wall, r).translate((0, 0, H / 2))
    part = bosses(part, L, W, H, wall, h["boss_d"], h["screw_d"] - 0.6, z0=wall)

    # coil tails out the front (+X) with a thickened standoff block
    block = (cq.Workplane("YZ").workplane(offset=L / 2 - wall - h["tail_standoff"])
             .center(0, H / 2).rect(h["tail_pitch"] + 16, H - 2 * wall - 2).extrude(h["tail_standoff"]))
    part = part.union(block)
    tails = (cq.Workplane("YZ").workplane(offset=L / 2 - wall - h["tail_standoff"] - 1).center(0, H / 2)
             .pushPoints([(-h["tail_pitch"] / 2, 0), (h["tail_pitch"] / 2, 0)])
             .circle(h["tail_d"] / 2).extrude(h["tail_standoff"] + wall + 2))
    part = part.cut(tails)

    # lead + JST out the back (−X)
    lead = (cq.Workplane("YZ").workplane(offset=-L / 2 - 1).center(-8, H / 2)
            .circle(h["lead_d"] / 2).extrude(wall + 2))
    jst = (cq.Workplane("YZ").workplane(offset=-L / 2 - 1).center(12, H / 2)
           .rect(h["jst_w"], h["jst_h"]).extrude(wall + 2))
    part = part.cut(lead).cut(jst)

    # strain-relief rib for the lead (zip-tie slots in the floor)
    for x in (-L / 2 + 12, -L / 2 + 20):
        slot = cq.Workplane("XY").workplane(offset=-1).center(x, -8).rect(2.5, 6).extrude(wall + 2)
        part = part.cut(slot)
    return part


def build_head_lid():
    h = head
    L, W, wall, r, t = h["L"], h["W"], h["wall"], h["corner_r"], h["lid_t"]
    lid = rounded_box(L, W, t, r).translate((0, 0, t / 2))
    pts = corner_points(L, W, wall + h["boss_d"] / 2)
    lid = lid.cut(cq.Workplane("XY").workplane(offset=-1).pushPoints(pts).circle(h["screw_d"] / 2 + 0.3).extrude(t + 2))
    return lid


# ------------------------------------------------------------------- export --
def export(name, part):
    os.makedirs(OUT, exist_ok=True)
    cq.exporters.export(part, os.path.join(OUT, f"{name}.stl"))
    cq.exporters.export(part, os.path.join(OUT, f"{name}.svg"),
                        opt={"projectionDir": (1, -1.2, 0.8), "width": 600, "height": 450,
                             "showHidden": False, "strokeWidth": 0.6})
    bb = part.val().BoundingBox()
    print(f"{name:10s} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f} mm")


if __name__ == "__main__":
    export("body", build_body())
    export("body_lid", build_body_lid())
    export("head", build_head())
    export("head_lid", build_head_lid())
    export("dock", build_dock())
