#!/usr/bin/env python3
"""Assembled-unit mock-ups → docs/images/mockup-*.png

Builds the body, lid, dock, a simplified EGO pack, the lead, the head and
its coil (with a bolt in it) as CadQuery solids, tessellates them, and
renders with a tiny numpy z-buffer rasterizer so it runs anywhere
(no OpenGL needed).  python cad/render_mockup.py
"""
import math
import os
import sys

import numpy as np
import cadquery as cq
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_cad as B  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "images")

# ------------------------------------------------------------- colours ---
C_BODY = (0.18, 0.20, 0.23)
C_LID = (0.22, 0.24, 0.27)
C_ACCENT = (0.95, 0.55, 0.10)     # trigger / LED ring
C_PACK = (0.56, 0.78, 0.20)       # EGO green
C_PACK_DARK = (0.20, 0.22, 0.20)
C_DOCK = (0.30, 0.30, 0.32)
C_HEAD = (0.18, 0.20, 0.23)
C_COPPER = (0.80, 0.45, 0.25)
C_LEAD = (0.12, 0.12, 0.13)
C_STEEL = (0.55, 0.56, 0.58)
C_HOT = (0.95, 0.30, 0.10)
C_HEATSINK = (0.62, 0.64, 0.66)


def tube_along(points, r):
    path = cq.Workplane("XY").spline(points)
    p0 = points[0]
    p1 = points[1]
    d = np.array(p1) - np.array(p0)
    d = d / np.linalg.norm(d)
    plane = cq.Plane(origin=p0, normal=tuple(d))
    return cq.Workplane(plane).circle(r).sweep(path, isFrenet=True)


def helix_tube(radius, pitch, turns, r_tube):
    h = pitch * turns
    helix = cq.Wire.makeHelix(pitch=pitch, height=h, radius=radius)
    start = helix.startPoint()
    tangent = helix.tangentAt(0)
    plane = cq.Plane(origin=start.toTuple(), normal=tangent.toTuple())
    return cq.Workplane(plane).circle(r_tube).sweep(cq.Workplane().add(helix), isFrenet=True)


def build_scene():
    b = B.body
    L, W, H = b["L"], b["W"], b["H"]
    parts = []  # (solid, colour)

    # ---- body + lid (body is at z 0..H, x = front-back, y = width)
    body = B.build_body()
    lid = B.build_body_lid().translate((0, 0, H))
    parts += [(body, C_BODY), (lid, C_LID)]
    # trigger button + LED on the lid
    trig = cq.Workplane("XY").workplane(offset=H + b["lid_t"]).center(L / 4, 0).circle(7.5).extrude(4)
    parts.append((trig, C_ACCENT))
    led = cq.Workplane("XY").workplane(offset=H + b["lid_t"]).center(L / 4 + 20, -15).circle(2.4).extrude(1.5)
    parts.append((led, C_ACCENT))
    # heatsink fins visible through the right-side slots: a block inside
    hs = cq.Workplane("XY").box(60, 26, 50).translate((-L / 4, W / 2 - 16, 28))
    parts.append((hs, C_HEATSINK))

    # ---- dock under the floor (simplified EGO interface: wings + tower), pack slides along X
    dz = 0  # dock top face mates with the body floor at z=0
    wings = cq.Workplane("XY").box(93, 93.5, 15).translate((0, 0, dz - 7.5))
    tower = cq.Workplane("XY").box(66, 36, 28.5).translate((-15 + 15, 0, dz - 14.25))
    dock = wings.union(tower).edges("|Z").fillet(2)
    parts.append((dock, C_DOCK))

    # ---- EGO pack: 140 x 80 x 105 with a cap on top that the dock sits in
    pack_top = dz - 28.5
    pack = (cq.Workplane("XY").box(140, 82, 100).edges("|Z").fillet(8).edges(">Z or <Z").fillet(3)
            .translate((0, 0, pack_top - 50 - 6)))
    collar = cq.Workplane("XY").box(100, 95, 14).edges("|Z").fillet(4).translate((0, 0, pack_top - 1))
    collar = collar.cut(cq.Workplane("XY").box(94, 94, 16).translate((0, 0, pack_top)))
    parts += [(pack, C_PACK), (collar, C_PACK_DARK)]
    # release button on the pack front
    btn = cq.Workplane("YZ").workplane(offset=70).center(0, pack_top - 20).rect(26, 10).extrude(3)
    parts.append((btn, C_PACK_DARK))

    # ---- lead from the XT90 (front face, y=-12, z=H/2) to the head
    x0 = L / 2 + 4
    ang = -35.0                      # head yaw (deg) about Z; head +X points this way
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    head_back = (x0 + 175, -70, 40)  # world position of the head's back-face centre
    # last control point approaches the back face along the head axis
    xz = H - b["wall"] - 12          # XT90 height on the front face (matches build_cad)
    lead_pts = [(x0, -12, xz), (x0 + 60, -16, xz + 2), (x0 + 120, -40, 46),
                (head_back[0] - 20 * ca, head_back[1] - 20 * sa, head_back[2]), head_back]
    parts.append((tube_along(lead_pts, 4.5), C_LEAD))
    xt = cq.Workplane("YZ").workplane(offset=L / 2).center(-12, xz).rect(22, 13).extrude(6)
    parts.append((xt, C_LEAD))

    # ---- head: shell + lid, rotated so its +X (coil side) points along the lead direction
    hd = B.head
    shell = B.build_head()
    hlid = B.build_head_lid().translate((0, 0, hd["H"]))
    head = shell.union(hlid)
    # orient: head local X -> world direction (cos a, sin a, 0); local back-face centre
    # (-L/2, 0, H/2) must land on head_back
    hx = head_back[0] + (hd["L"] / 2) * ca
    hy = head_back[1] + (hd["L"] / 2) * sa
    hz = head_back[2] - hd["H"] / 2

    def place(solid):
        return solid.rotate((0, 0, 0), (0, 0, 1), ang).translate((hx, hy, hz))
    parts.append((place(head), C_HEAD))

    # coil: axis along head +X, starting at the front face
    coil = helix_tube(radius=22.5, pitch=9, turns=8, r_tube=3.2)
    # helix is built along Z; rotate so its axis is +X, then move to the head front
    coil = coil.rotate((0, 0, 0), (0, 1, 0), 90)  # Z -> X
    coil = coil.translate((hd["L"] / 2 + 6, 0, hd["H"] / 2))
    tails = (cq.Workplane("YZ").workplane(offset=hd["L"] / 2 - 10).center(0, hd["H"] / 2)
             .pushPoints([(-7, 0), (7, 0)]).circle(3.2).extrude(18))
    parts.append((place(coil.union(tails)), C_COPPER))

    # bolt in the coil (hot)
    bolt_shank = (cq.Workplane("YZ").workplane(offset=hd["L"] / 2 + 10).center(0, hd["H"] / 2)
                  .circle(6).extrude(90))
    nut = (cq.Workplane("YZ").workplane(offset=hd["L"] / 2 + 36).center(0, hd["H"] / 2)
           .polygon(6, 24).extrude(12))
    parts.append((place(bolt_shank), C_STEEL))
    parts.append((place(nut), C_HOT))

    return parts


# ------------------------------------------------------- rasteriser ------
def tessellate(parts, tol=0.4):
    tris, cols = [], []
    for solid, colour in parts:
        for s in solid.vals() if hasattr(solid, "vals") else [solid]:
            v, f = s.tessellate(tol, 0.3)
            v = np.array([p.toTuple() for p in v])
            f = np.array(f)
            tris.append(v[f])
            cols.append(np.tile(colour, (len(f), 1)))
    return np.concatenate(tris), np.concatenate(cols)


def render(tris, cols, azim, elev, size=(1600, 1100), fov_scale=1.0, light=(0.4, -0.6, 0.7), bg=(1, 1, 1)):
    """Orthographic render. azim/elev in degrees. Returns PIL image."""
    a, e = math.radians(azim), math.radians(elev)
    # camera basis
    fwd = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])  # from scene to camera
    right = np.cross([0, 0, 1], fwd); right /= np.linalg.norm(right)
    up = np.cross(fwd, right)
    P = np.stack([right, up, fwd])  # rows
    v = tris.reshape(-1, 3) @ P.T
    v = v.reshape(-1, 3, 3)
    # normals + shading
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nl = np.linalg.norm(n, axis=1, keepdims=True); nl[nl == 0] = 1
    n = n / nl
    lt = np.array(light) / np.linalg.norm(light)
    shade = 0.35 + 0.65 * np.clip(n @ lt, 0, 1)
    # occasional rim light so dark plastic isn't flat
    shade += 0.12 * np.clip(n @ fwd, 0, 1) ** 4
    rgb = np.clip(cols * shade[:, None], 0, 1)
    # fit to image
    Wd, Hd = size
    xy = v[:, :, :2].reshape(-1, 2)
    mn, mx = xy.min(0), xy.max(0)
    scale = 0.92 * min(Wd / (mx[0] - mn[0]), Hd / (mx[1] - mn[1])) * fov_scale
    off = np.array([Wd, Hd]) / 2 - (mn + mx) / 2 * scale
    sx = v[:, :, 0] * scale + off[0]
    sy = Hd - (v[:, :, 1] * scale + off[1])
    sz = v[:, :, 2]
    img = np.ones((Hd, Wd, 3)) * np.array(bg)
    zbuf = np.full((Hd, Wd), -np.inf)
    # painter-ish order: far to near, with z-test per pixel
    order = np.argsort(sz.mean(1))
    for i in order:
        x, y, z = sx[i], sy[i], sz[i]
        x0, x1 = int(max(0, x.min())), int(min(Wd - 1, x.max()) + 1)
        y0, y1 = int(max(0, y.min())), int(min(Hd - 1, y.max()) + 1)
        if x1 <= x0 or y1 <= y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        d = (x[1] - x[0]) * (y[2] - y[0]) - (x[2] - x[0]) * (y[1] - y[0])
        if abs(d) < 1e-9:
            continue
        w0 = ((x[1] - gx) * (y[2] - gy) - (x[2] - gx) * (y[1] - gy)) / d
        w1 = ((x[2] - gx) * (y[0] - gy) - (x[0] - gx) * (y[2] - gy)) / d
        w2 = 1 - w0 - w1
        inside = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        if not inside.any():
            continue
        zz = w0 * z[0] + w1 * z[1] + w2 * z[2]
        sub = zbuf[y0:y1, x0:x1]
        upd = inside & (zz > sub)
        sub[upd] = zz[upd]
        img[y0:y1, x0:x1][upd] = rgb[i]
    # light ground shadow: darken bg under the model's footprint a little
    return Image.fromarray((img * 255).astype(np.uint8))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    parts = build_scene()
    tris, cols = tessellate(parts)
    print("triangles:", len(tris))
    views = {
        "mockup-hero": dict(azim=-150, elev=28),
        "mockup-front": dict(azim=-95, elev=12),
        "mockup-top": dict(azim=-120, elev=70),
    }
    for name, v in views.items():
        im = render(tris, cols, **v)
        im.save(os.path.join(OUT, name + ".png"))
        print("wrote", name)
    # head close-up: head, coil, bolt only (last five parts of the scene)
    tris_h, cols_h = tessellate(parts[-4:], tol=0.2)
    render(tris_h, cols_h, azim=-50, elev=22, size=(1400, 900)).save(os.path.join(OUT, "mockup-head.png"))
    print("wrote mockup-head")
