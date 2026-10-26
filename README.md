# ego-coil

A handheld induction bolt heater that runs on an EGO 56 V tool battery.
Open hardware: ZVS power stage in the body, swappable coil heads that carry
their own resonant caps, and a small RP2040 supervisor that keeps the
battery's BMS happy and the MOSFETs alive.

```
EGO pack ─┤ body: fuse → bulk caps → ZVS stage → main switch → supervisor ├══ lead ══╡ head: coil + cap bank ╞
```

**Status: design stage.** Nothing here has been built yet. The numbers are
engineering estimates from first principles; the bring-up order in
`docs/design.md` §7 is written so that the estimates get replaced by
measurements before anything runs on the battery.

## What's in the repo

| Path | What |
|---|---|
| `docs/design.md` | The electrical design, with the reasoning for every choice, plus safety and bring-up order |
| `docs/bom.md` | Parts list with ratings and why each rating matters |
| `docs/schematic.svg` | Schematic of the body (power stage, main switch, supervisor) and a head |
| `tools/zvs_tank.py` | Coil / cap / frequency / current calculator — run it for every new head |
| `firmware/` | MicroPython supervisor for a Raspberry Pi Pico |
| `cad/` | OpenSCAD: parametric body enclosure and head shell |

## Design in one paragraph

A ZVS (Mazzilli) push-pull oscillator is the cheapest reliable way to drive an
induction tank, and 56 V is a good voltage for it. At 56 V the MOSFET drains
swing to ~180 V, so the stage uses 250 V parts. The resonant capacitors sit
in the **head** next to the coil, not in the body, so the 150–250 A
circulating current never travels down the lead; the lead only carries the
~30 A drain current and can be a short twisted pair. Each head is a tuned
tank on its own; the ZVS stage locks to whatever head is plugged in. A Pico
watches bus current, heatsink temperature and run time, switches the stage
on and off in burst mode for power levels, and trips before the pack's BMS
does.

## Quick start

```bash
# what does a given coil want for caps and what will it draw?
python tools/zvs_tank.py --turns 8 --diameter 45 --pitch 9 --vdc 56 --caps 1.5 --n-caps 15
python tools/zvs_tank.py --turns 5 --diameter 25 --pitch 8 --sweep        # pencil coil
python tools/zvs_tank.py --turns 8 --diameter 45 --pitch 9 --freq 120     # solve for C
```

Firmware: copy `firmware/*.py` to the Pico with Thonny or `mpremote cp
firmware/*.py :`. Pin assignments and trip thresholds are in
`firmware/config.py`.

CAD: open `cad/body.scad` or `cad/head.scad` in OpenSCAD, adjust the
parameters at the top of each file, export STL.

## Safety

Read `docs/design.md` §6 before building. Short version: strong magnetic
field (implants), red-hot metal, 200 V at 100 kHz in the head, and a lithium
pack that will deliver hundreds of amps into a fault. The 40 A fuse at the
pack is not optional.

## License

CERN-OHL-P v2 for hardware, MIT for firmware and tools. Pick what suits
when you publish; both are permissive.
