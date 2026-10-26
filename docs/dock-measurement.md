# Measuring your EGO pack for the printed dock

`cad/build_cad.py` has a `rail` dictionary whose values marked **MEASURE** are
placeholders. Ten caliper readings on the pack you own turn them into a dock
that fits. Do this once; it takes ten minutes.

Orientation: look at the bottom of the pack, the face that slides onto a tool.
The pack slides on in one direction; call that the **slide axis**. The two
grooves that run along the slide axis are what the dock's rails engage.

| # | Measure | Put in |
|---|---|---|
| 1 | Centre-to-centre distance between the two grooves | `rail_spacing` |
| 2 | Groove width at the opening (where the rail enters) | `rail_w_top` |
| 3 | Groove width at the neck, the narrowest point | `rail_w_root` |
| 4 | Groove depth, opening to floor | `rail_h` |
| 5 | Width of the latch tongue (the spring-loaded tab the release button moves) | `latch_w` |
| 6 | How far the tongue drops below the groove floor when released | `latch_depth` |
| 7 | Distance from the pack's leading face (the end that hits the tool's stop) to the latch tongue's catching face | `latch_from_end` |
| 8 | Centre spacing of the two **power** blades (the big ones; ignore the small signal pins) | `term_pitch` |
| 9 | Distance from the leading face to the centre of the power blades | `term_from_end` |
| 10 | Blade width and thickness | `term_w`, `term_t` |

Then:

```bash
python cad/build_cad.py        # writes cad/out/dock.stl
```

## First print

Print `dock.stl` alone in PETG, rails up, no supports, 5 walls, 40 % infill.
If the pack is tight, raise `clearance` by 0.1; if it rattles, lower it.
Check that the latch clicks and holds before you trust it with 2 kW.

## Terminals

Female 6.3 mm spade terminals (crimped to 10 AWG, insulated) drop into the two
slots in the end stop; the wire runs down through the hole behind each slot
and into the body through the cable hole. Use the two **power** blades only.
EGO packs also carry small signal contacts for the tool; this design does not
connect to them, the pack's internal BMS does the protection.

If your pack's blades are not 6.3 mm, measure (#10) and swap the terminals
for the matching size; the slot width follows `term_w`.

## Mounting

The plate screws to the body's rear recess on the 64 × 44 mm pattern with four
M3 × 12 and nuts inside the body. The pack's weight hangs on these, so use
nyloc nuts.
