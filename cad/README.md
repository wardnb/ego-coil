# cad/

`build_cad.py` is a parametric CadQuery model. Edit the dictionaries at the
top, run it, print the STLs from `cad/out/`.

```bash
pip install cadquery
python cad/build_cad.py
```

| Part | What | Print notes |
|---|---|---|
| `body.stl` | 160 × 95 × 75 mm box. Floor: 4 nut bosses + cable hole for the EGO dock underneath (rear recess kept for the fallback plate). Four 10 mm standoffs for the 100 × 80 main PCB (`powerboard` dict); the Pico is socketed on that board. Left: 40 mm fan. Right: exhaust slots. Front: XT90 panel mount + JST-XH head-ID. Floor: standoffs for a 60 × 40 power board and a Pico. | PETG or ASA, 4 walls, 30 % infill. Open side up, no supports. |
| `body_lid.stl` | Lid with locating lip, trigger (16 mm), LED (5 mm) and buzzer grille. | Same material. |
| `head.stl` | 70 × 48 × 34 mm shell for the cap bank. Coil tails exit the front through a thickened standoff block; lead and JST exit the back; zip-tie slots for strain relief. | **PC, PA-CF or ASA** — the coil tails get hot by conduction from the bolt. PETG is marginal. |
| `head_lid.stl` | Plain lid. | Same material as the head. |
| `ego56v_dock.stl` (in `cad/`, not generated) | Complete EGO tool-side interface, mounts under the body. Add four M3 holes in the slicer — see `docs/dock-measurement.md`. | PETG/ASA, tower up, 5 walls, 40 % infill. |
| `dock.stl` | Fallback parametric rail-plate dock for the rear recess; needs ten caliper readings (`rail` dict). | PETG, rails up. |

## What is deliberately not modelled


* **The heatsink.** It sits in the rear-left bay under the fan; set
  `body["H"]` so your heatsink plus the TO-247 packages clear the lid. 75 mm
  fits a 25 mm-fin heatsink laid flat with the MOSFETs on top.
* **A grip.** The first build is a box with a lanyard; once the weight and
  balance are known, add a pistol grip under the front half.

## Head geometry

The reference head holds 15 caps between two 20 × 2 mm copper bars running
along X, with the coil tails clamped at the front end of the bars. The
standoff block around the tails is 10 mm thick so the hot copper has an air
gap to the printed wall; slip ceramic beads or silicone sleeve on the tails
where they pass through.

Coil tails are on `tail_pitch = 14 mm` centres. Match that when you wind the
coil, or change the parameter.
