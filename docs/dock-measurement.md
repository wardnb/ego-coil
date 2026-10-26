# EGO dock

## Use the supplied interface: `cad/ego56v_dock.stl`

`cad/ego56v_dock.stl` is a complete EGO 56 V tool-side interface (93.5 × 93 ×
28.5 mm): the central tower with the wire ramp inside, the two 15 mm wings
the pack's grooves ride on, and a 5 mm tail plate with two blade slots on
28 mm centres for the power terminals. It mounts **under the body**, so the
pack hangs below the electronics like a cordless drill's.

Frame convention: the STL loads with z up, the tower running along y
(y −61 … +31) and the wings at ±x. The pack slides along y.

### 1. Add four screw holes in the slicer

The mesh is not manifold, so holes are added at slice time rather than in
CAD. In Orca / Bambu / PrusaSlicer, add a **negative part** (cylinder, 3.4 mm
diameter, through) at each of these positions in the STL's own coordinates,
plus a 6.5 mm × 90° countersink on the top (wing) face so the heads sit below
the surface the pack slides over:

| x | y |
|---|---|
| +34 | −10 |
| +34 | +20 |
| −34 | −10 |
| −34 | +20 |

These land in the solid wings, 15 mm deep. `cad/build_cad.py` puts the
matching 3.2 mm holes and M3 nut bosses in the body floor
(`DOCK_STL_HOLES`); change both together if you move them.

### 2. Terminals

Two **male 6.3 mm blade terminals** (flag/PCB-tab style, 0.8 mm thick, crimped
or soldered to 10 AWG) stand in the tail-plate slots at x = ±14 and run up
the ramp inside the tower. The pack's female contacts pick them up as it
slides on. Confirm the blade thickness against the slot (≈1 mm) before you
glue anything: too thin and the blade can tilt, too thick and it won't seat.
Use the two **power** contacts only; the pack's small signal pins are not
connected, the pack's own BMS does the protection.

Route the two 10 AWG leads through the body's floor cable hole (14 mm) to
the fuse holder immediately inside.

### 3. Print

PETG or ASA, tower up, 5 walls, 40 % infill, no supports needed for the
original geometry. Check the mesh in the slicer's repair tool first; it
reports non-manifold edges on this file but slices cleanly.

### 4. Assembly

M3 × 20 countersunk from the dock side, through the body floor, nyloc nuts on
the bosses inside. The pack's weight and every yank on the lead go through
these four screws; don't skip the nylocs.

## Fallback: parametric dock

If the supplied STL turns out not to match your pack generation,
`build_dock()` in `cad/build_cad.py` is a parametric rail-plate dock whose
`rail` values you fill in from ten caliper readings on your pack:

| # | Measure | Put in |
|---|---|---|
| 1 | Centre-to-centre distance between the pack's two grooves | `rail_spacing` |
| 2 | Groove width at the opening | `rail_w_top` |
| 3 | Groove width at the neck | `rail_w_root` |
| 4 | Groove depth | `rail_h` |
| 5 | Latch tongue width | `latch_w` |
| 6 | Latch tongue drop | `latch_depth` |
| 7 | Leading face → latch catch face | `latch_from_end` |
| 8 | Power-blade centre spacing | `term_pitch` |
| 9 | Leading face → blade centres | `term_from_end` |
| 10 | Blade width and thickness | `term_w`, `term_t` |

It mounts on the body's rear recess instead of underneath.
