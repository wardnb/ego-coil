# ego-coil — electrical design

A handheld induction bolt heater: EGO 56 V pack → power stage in the body →
short flexible lead → swappable coil head that carries its own resonant caps.

## 1. Architecture

```
 ┌───────────────────────────── BODY ─────────────────────────────┐
 │  EGO pack ──fuse──TVS──┬── bulk caps ──┬── L1 ──┐              │
 │                        │               └── L2 ──┤   drains     │   lead (≤25 cm,
 │                        │          ┌──────────────┴──────────┐   │   twisted 10 AWG)
 │                        │          │  Q1  Q2  ZVS core        ├──XT90══════╗
 │                        │          │  gate net on 12 V rail   │   │        ║
 │                        │          └──────────┬──────────────┘   │        ║
 │                        │              ZVS ground node            │   ┌────╨────┐
 │                        │                     │                   │   │  HEAD   │
 │                        │              Q3 main switch (low side)  │   │ C-bank  │
 │                        │                     │  ┌─ Hall sensor   │   │ + coil  │
 │                        └── pack negative ────┴──┘                │   └─────────┘
 │                                                                   │
 │  12 V buck (XL7015, 80 V in) → gate pull-ups, fan, Q3 driver      │
 │  5 V  mini buck → RP2040 supervisor, INA180                       │
 └───────────────────────────────────────────────────────────────────┘
```

Three blocks:

| Block | Lives in | Job |
|---|---|---|
| ZVS power stage | body | Self-oscillating push-pull (Mazzilli) driving the tank |
| Resonant tank | head | Work coil + parallel cap bank, pre-tuned per head |
| Supervisor | body | Enable/disable the stage, trip on overcurrent / overtemp / timeout, burst-mode power levels |

### Why the caps go in the head

The coil and the caps exchange the circulating tank current (150–250 A peak).
If the caps sit in the body, that current runs down the lead: the lead gets
hot, stiff and lossy, and its inductance detunes the tank. With the caps at
the coil, the lead carries only the drain current (~20–40 A RMS), so it can be
a short twisted pair of ordinary 10 AWG silicone wire. Each head is a
self-contained tuned tank, and because a ZVS oscillator tracks resonance on
its own, heads with different coils can be swapped without touching the body.

### Why the lead must stay short

The lead sits between the MOSFET drains and the tank, so its inductance adds
to the tank *in series with the drains*, not in parallel with the coil. A long
or untwisted lead stores energy that shows up as ringing and voltage spikes on
the drains. Rules: ≤25 cm, tightly twisted, both conductors the same length.
Scope the drains on the first build; if the waveform is a clean half-sine with
no spike at the zero crossing, the lead is fine.

## 2. Tank numbers (from `tools/zvs_tank.py`)

Reference head: 8 turns of 1/4" (6.35 mm) copper tube, 45 mm mean diameter,
9 mm pitch.

```
python tools/zvs_tank.py --turns 8 --diameter 45 --pitch 9 --vdc 56 --caps 1.5 --n-caps 15
```

| Quantity | Value | Confidence |
|---|---|---|
| Coil inductance (empty) | ~1.4 µH | ±10 % (Wheeler) — measure it |
| Coil inductance (bolt in coil) | ~1.0 µH | assumed ×0.7 — measure it |
| Cap bank | 1.5 µF | chosen |
| Frequency | ~110 kHz empty, ~130 kHz loaded | solid |
| Drain peak voltage | ~176 V ideal, spikes higher | solid |
| Tank current | ~220 A pk / ~155 A RMS loaded | solid |
| Circulating VA | ~19 kVA | solid |
| Real power | 1–3 kW depending on loaded Q | **estimate** |
| Pack current | 20–50 A | **estimate** — the supervisor trips at 38 A |

Loaded Q (how hard the bolt loads the tank) can only be measured. A rusted
3/4" nut in a snug coil is a heavy load (Q≈5–8, high power); a small bolt in a
loose coil is a light one (Q≈15–20, low power). Design the heads so the coil
sits close to the work.

### Why 1.5 µF and ~120 kHz

Lower frequency = easier gate drive and lower switching loss, but higher
circulating current (more cap ripple). Higher frequency = the reverse. 100–150
kHz is the sweet spot for IRFP-class MOSFETs with a passive gate network. If
you build a smaller pencil coil (fewer turns, lower L) you need *more*
capacitance to stay in that band — run the calculator for each head.

## 3. Power stage

### MOSFETs Q1, Q2
A ZVS tank swings the drains to π·Vdc ≈ 176 V at 56 V, plus ringing. 200 V
parts have no margin. Use 250 V:

* **IRFP4332PbF** — 250 V, 57 A, 33 mΩ, TO-247. First choice.
* IRFP4229PbF — 250 V, 44 A, 46 mΩ. Fine.
* IRFP264 — 250 V, 38 A, 75 mΩ. Older, hotter, works.

Mount both on one heatsink (isolated with silpads *or* use the drain tabs and
isolate the heatsink from everything). Heatsink: ≥ 100 × 60 × 25 mm finned
aluminium with a 40–60 mm 12 V fan. 10–15 s bursts with cooldown between them
is the intended duty cycle; this is a bolt heater, not a forge.

### Chokes L1, L2
Two independent chokes, ~47 µH each, 14 AWG, on sendust / Kool-Mµ toroids
(Magnetics 77083 or similar, ~30 turns) or a pair of 47–100 µH / 20 A rod
inductors. They set the inrush and smooth the drain current. Bigger L = softer
start on the BMS, slightly slower response. Do not use a single center-tapped
choke unless you understand the consequences; two independent chokes is the
robust choice.

### Gate network (per MOSFET)
Fed from the **12 V rail**, not from the 56 V bus — pull-ups straight from
56 V would dissipate several watts each.

| Part | Value | Notes |
|---|---|---|
| R pull-up | 100 Ω, 3 W | 12 V → gate. Sets gate rise time. Ciss of IRFP4332 ≈ 6.7 nF → τ ≈ 0.7 µs, OK to ~150 kHz. Use 220 Ω if the stage runs < 80 kHz. |
| D feedback | UF4007 or MUR460 | gate → *opposite* drain, cathode at drain. This is what makes it oscillate. |
| Z clamp | 15 V, 1.3 W | gate → source, cathode at gate. Protects the gate. |
| R g-s | 10 kΩ | gate → source. Holds the FET off when the 12 V rail is down. |

### Bulk caps
2 × 1000 µF / 100 V low-ESR electrolytic across the DC input after the fuse,
plus 2 × 1 µF 100 V film close to the choke feeds.

### Input protection
* 40 A ANL/MIDI fuse or a 40 A DC breaker, as close to the pack contacts as
  the dock allows.
* TVS **SMCJ70A** (or 5KP70A for more headroom) across the input after the
  fuse. Pack full-charge is ~58 V; 70 V standoff leaves room for ringing.
* Reverse polarity: the EGO dock is keyed, so rely on the key, but orient the
  TVS so a reverse connection blows the fuse rather than the electronics.

## 4. Main switch Q3 and the supervisor

The ZVS oscillator **must be started by applying the full bus voltage fast**.
Ramping the supply slowly is the classic way to make a ZVS fail to oscillate,
latch with both MOSFETs on, and blow them. So "soft start" here means:

1. Bulk caps are **pre-charged** through a 100 Ω / 5 W resistor across Q3
   whenever the pack is docked (takes ~0.5 s).
2. Inrush into the tank is limited by L1/L2.
3. Q3 closes hard. Power *level* is set by **burst mode** (switching Q3 on/off
   at ~20 Hz with a duty cycle), never by lowering the voltage.

### Q3
Low-side N-channel on the ZVS return: **IRFB4110** (100 V, 180 A, 4.5 mΩ,
TO-220) or two in parallel. Driven by a **TC4420** from the 12 V rail; TC4420's
TTL-level input is driven straight from an RP2040 GPIO at 3.3 V. 10 Ω gate
resistor, 10 kΩ gate pull-down.

When Q3 is open the ZVS ground node floats. The gate zeners forward-bias and
let it settle at roughly 12 V above pack negative, with microamps flowing.
That is harmless. Do **not** add a bleed resistor from the ZVS ground node to
pack negative — with the gate rail live it would let both MOSFETs conduct and
drag the node to the bus voltage.

### Sensing

| Signal | Sensor | To RP2040 |
|---|---|---|
| Bus current | 2 × 2 mΩ 2512 shunts in parallel (1 mΩ, 6 W) in the Q3 return path, read by an **INA180A2** (gain 50, 5 V supply) with Kelvin traces | ADC0. 40 A → 40 mV × 50 = 2.0 V. (Alternative: ACS758LCB-050B Hall sensor through a 10 k/10 k divider; select in `config.py`.) |
| Pack voltage | 100 kΩ / 5.6 kΩ divider from the fused bus | ADC1. 58 V → 3.07 V. |
| Heatsink temp | 10 kΩ NTC (B=3950) on the MOSFET heatsink, 10 kΩ to 3.3 V | ADC2. |
| Trigger | momentary switch to GND, internal pull-up | GP16 |
| Head ID | two lines (GP22, GP21) with internal pull-ups, strapped to GND or open inside the head | 4 codes |

### Supplies
* **12 V**: an **XL7015**-based buck module (5–80 V in, ~0.8 A; sold as
  "DC-DC 80 V step-down"). Powers the gate pull-ups (~0.15 A), the TC4420,
  and the fan. Check the module's input cap is rated ≥ 80 V; some clones fit
  63 V caps. Do **not** use LM2596 boards: 40 V max, and a fresh pack is 58 V.
  (Drop-in upgrade if you want a name-brand part: RECOM R-78HB12-0.5, 72 V in.)
* **5 V**: any small 12 V → 5 V buck (MP1584 module) or a 7805 on a tab of
  heatsink — the Pico and the INA180 draw < 100 mA.
* RP2040: a Pico or Pico W. Everything is 3.3 V logic from there.

### Firmware behaviour (`firmware/main.py`)
* Idle: fan off, status LED breathing. Pack voltage and heatsink temp sampled.
* Trigger pressed and no fault → Q3 on (burst-mode duty for the selected
  level) → LED solid.
* Trip conditions, all latched until the trigger is released:
  * bus current > 38 A for > 20 ms (BMS protection is typically 40–60 A; we
    trip first so the pack never shuts down mid-heat)
  * heatsink > 70 °C
  * run time > 20 s continuous
  * pack < 46 V under load (empty pack sag)
* Three power levels cycled by a short press when idle: 40 % / 70 % / 100 %
  burst duty at 20 Hz.
* Fan on whenever heatsink > 40 °C or the stage has run in the last 60 s.

## 5. The head

* **Coil**: 1/4" soft copper refrigeration tube. Wind it on a mandrel, keep
  ~2.5 mm gap between turns (slip on PTFE or fibreglass sleeve to guarantee
  it). Two straight tails ~40 mm long that pass through the head shell to the
  cap bank.
* **Cap bank**: ~1.5 µF of **pulse / resonant-rated polypropylene at
  ≥ 630 V**. Cheapest good option: 5 × 0.33 µF 1200 V CBB81 (the ones sold
  for ZVS heaters, ~$1.50 each) or, free, the 0.27–0.3 µF 1200 V resonant caps
  out of a scrapped induction cooktop — that is exactly this duty. The
  reference-grade choice is 15 × 0.1 µF Cornell Dubilier 940C / EPCOS B32652.
  The bank carries ~155 A RMS total, so ~30 A per cap with 5 caps: check the
  datasheet's dV/dt or I_RMS figure. Generic 0.1 µF MKP coupling caps are
  rated 1–3 A and *will* fail hot. Solder them between two copper
  bus bars (20 × 2 mm) that also clamp the coil tails.
* **Cooling**: for 10–15 s bursts the copper mass is enough. A 1/4" tube
  coil is also a water channel: if you want continuous duty, run coolant
  through it from a small pump in the body (the lead gets two silicone hoses
  alongside it).
* **Shell**: printed in a high-temp material (PC, PA-CF, or at least PETG
  with an air gap); the coil gets hot by conduction from the bolt. The shell
  holds the bus bars, caps and the XT90 pigtail. See `cad/head.scad`.

Head variants (each is just a coil + cap bank, re-run the calculator):

| Head | Coil | Approx L | Caps for ~120 kHz |
|---|---|---|---|
| Nut (reference) | 8 t × 45 mm | 1.4 µH | 1.5 µF |
| Pencil (tight spaces) | 5 t × 25 mm | 0.35 µH | 5 µF — or accept ~200 kHz with 2 µF |
| Pancake (flat surfaces) | 6 t spiral, 60 mm OD | ~1 µH | 2 µF |

Low-inductance pencil coils push the frequency up fast. The pragmatic answer
is to give the pencil head ~2 µF, accept ~200 kHz, and limit it to lower
burst duty in firmware. A 3-pin JST-XH beside the XT90 carries two ID lines
and GND; straps inside each head give four codes, so the supervisor knows
which head is attached and caps its duty — see `firmware/config.py`.

## 6. Safety

* **Pacemakers / implants**: the field near the coil is strong. Keep anyone
  with an implanted device well away.
* **Rings and watches off.** Any metal on your hands heats.
* **Fuel / brake lines**: never within a few inches of the coil.
* **Burns**: the bolt is red-hot and the coil is hot. Gloves.
* **Lithium pack**: the 40 A fuse is non-negotiable. A shorted tank with no
  fuse turns the pack into a welder.
* **Drain voltage**: the tank node is 170–250 V peak at ~120 kHz. Insulated
  shell, no exposed metal on the head except the coil itself.
* **Printed shells and hot copper**: an air gap or a ceramic / silicone
  standoff between the coil tails and the plastic.

## 7. Build and bring-up order

1. Build the power stage on a bench supply (24 V, current-limited to 5 A) with
   a 1 Ω / 50 W dummy "coil" of a few turns. Scope the drains: two
   interleaved half-sines, no spikes, no flat-topping. Fix that first.
2. Build the reference head. Measure the coil with an LC meter and adjust the
   cap bank to land in 100–150 kHz.
3. Run at 24 V with the real head, heat a bolt, watch the drain waveform with
   the bolt in and out. Check cap temperature after a 15 s run.
4. Bring up the supervisor with Q3 in the loop, still at 24 V. Verify trips
   by lowering the current threshold temporarily.
5. Move to 36 V, then the EGO pack. Set the current trip from measured data.
6. Only then close up the enclosure.

Expect to lose a MOSFET or two during step 1. Buy five.
