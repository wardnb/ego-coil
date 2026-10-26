# ego-coil — bill of materials

Prices are rough 2026 single-unit figures from the usual distributors
(Mouser/Digi-Key) unless noted. Verify every rating against the datasheet
before you order; the notes say *why* each rating matters.

## Body — power stage

| Qty | Part | Spec | Why | ~$ |
|---|---|---|---|---|
| 2 (+3 spares) | MOSFET Q1/Q2 | IRFP4332PbF, 250 V, TO-247 | Drains swing to ~π·Vdc ≈ 176 V plus ringing; 200 V parts have no margin | 25 |
| 2 | Choke L1/L2 | ~47 µH, ≥ 20 A sat., 14 AWG (Magnetics 77083 toroid ~30 t, or 47–100 µH / 20 A rod) | Limit inrush, smooth drain current | 12 |
| 2 | Gate pull-up | 100 Ω, 3 W wirewound/metal oxide | Gate rise time vs. Ciss | 1 |
| 2 | Feedback diode | UF4007 (or MUR460) | Fast recovery; what makes the Royer oscillate | 1 |
| 2 | Gate zener | 15 V, 1.3 W (1N5929B / BZX85C15) | Gate-source clamp | 1 |
| 2 | Gate-source resistor | 10 kΩ, 1/4 W | Hold off with gate rail down | — |
| 2 | Bulk cap | 1000 µF, 100 V, low-ESR electrolytic (Nichicon UHE / Panasonic FR) | Buffer the pack | 6 |
| 2 | Film bypass | 1 µF, 100 V, film | HF bypass at the choke feeds | 2 |
| 1 | TVS | SMCJ70A (or 5KP70A) | Clamp ringing; pack full charge ~58 V | 1 |
| 1 | Fuse + holder | 40 A MIDI/ANL + inline holder, **or** 40 A DC breaker | Shorted tank = welder without it | 8 |
| 1 | Heatsink | ≥ 100 × 60 × 25 mm finned, for 2 × TO-247 | Burst duty, but 2 kW stage | 10 |
| 2 | TO-247 insulator kit | Silpad + shoulder washer | Isolate drains from heatsink | 2 |
| 1 | Fan | 40–60 mm, 12 V, ≤ 0.2 A | Heatsink cooling | 5 |
| 1 | Connector (body side) | XT90 female, panel mount | Head connection, 90 A rated | 3 |
| — | Wire | 10 AWG silicone, red/black, 1 m | Lead, internal power | 5 |

## Body — main switch and supervisor

| Qty | Part | Spec | Why | ~$ |
|---|---|---|---|---|
| 1 (or 2 ∥) | Q3 main switch | IRFB4110PbF, 100 V, 4.5 mΩ, TO-220 | Low-side burst switch; 2 in parallel for less heat | 4 |
| 1 | Gate driver | TC4420CPA | 6 A driver, TTL input works at 3.3 V | 2 |
| 1 | Q3 gate resistor | 10 Ω | — | — |
| 1 | Q3 gate pull-down | 10 kΩ | Off at power-up | — |
| 1 | Pre-charge resistor | 100 Ω, 5 W, across Q3 | Charge bulk caps before Q3 closes | 1 |
| 1 | Current sensor | **ACS758LCB-050B** (±50 A, 40 mV/A, 5 V) | Isolated Hall sense in the Q3 return | 8 |
| 2 | Divider | 10 kΩ / 10 kΩ 1 % | ACS758 0–5 V → 0–2.5 V for the ADC | — |
| 2 | Divider | 100 kΩ / 5.6 kΩ 1 % | Pack voltage sense (58 V → 3.07 V) | — |
| 1 | NTC | 10 kΩ, B = 3950, ring-lug or TO-220 style | Heatsink temperature | 2 |
| 1 | 12 V regulator | **RECOM R-78HB12-0.5** (17–72 V in) | Gate rail, driver, fan. LM2596 boards die at 58 V | 12 |
| 1 | 5 V regulator | RECOM R-78E5.0-0.5 (from 12 V) | Pico VSYS + ACS758 | 5 |
| 1 | MCU | Raspberry Pi Pico (W optional) | Supervisor | 5 |
| 1 | Trigger | Momentary, 16 mm, panel mount | — | 2 |
| 1 | Status LED | 5 mm RGB common-cathode, or 3 LEDs | Idle / run / fault | 1 |
| 1 | Buzzer | 3.3 V active piezo | Fault beep | 1 |
| 1 pair | Head-ID connector | JST-XH 3-pin, panel + pigtail | ID0/ID1/GND; straps inside the head select the duty cap | 1 |
| 1 | Proto board | 70 × 90 mm, 2.54 mm | Power stage is hand-wired with heavy copper; supervisor on proto | 3 |

## Body — pack interface

| Qty | Part | Notes |
|---|---|---|
| 1 | EGO 56 V adapter | Buy a bare "EGO 56V battery adapter / dock" (several exist for DIY use: they expose B+ and B− on screw terminals), **or** print one. There are published EGO dock models on Printables/Thingiverse; `cad/body.scad` leaves a parametric pocket for whichever you use. Only B+ and B− are needed; the pack's internal BMS does the protection. |
| 1 | EGO pack | 5.0 Ah or larger. 2.5 Ah packs trip their BMS under this load. 7.5 Ah+ sags least. |

## Head (reference 8-turn nut coil)

| Qty | Part | Spec | Why | ~$ |
|---|---|---|---|---|
| ~1.2 m | Copper tube | 1/4" OD soft refrigeration tube | Work coil | 6 |
| 15 | Resonant caps | 0.1 µF, ≥ 630 V, **pulse / dV/dt-rated film** — Cornell Dubilier 940C6P1K-F, EPCOS B32652A6104, KEMET R76 series | ~10 A RMS *each* at 130 kHz; coupling-grade MKP caps overheat | 25 |
| 2 | Bus bar | Copper, 20 × 2 mm × 80 mm | Low-inductance cap bank + coil clamp | 4 |
| 1 | Connector (head side) | XT90 male, 15 cm pigtail, 10 AWG twisted | ≤ 25 cm total lead | 3 |
| 1 | Head-ID pigtail | JST-XH 3-pin, strap per `firmware/config.py` table | Lets the supervisor cap duty for small coils | 1 |
| — | PTFE sleeve | 6.5 mm ID, or fibreglass | Turn spacing / insulation | 3 |
| 1 | Shell | Print `cad/head.scad` in PC / PA-CF (PETG at a push) | — | — |

## Tools you need on hand

* Oscilloscope, ≥ 50 MHz, with a ×10 probe (drain waveforms are the only way
  to know the stage is healthy)
* LC meter (coil inductance; cheap "transistor tester" LC meters are fine)
* Bench supply, 0–30 V, current-limited, for bring-up
* Clamp meter, DC-capable, for the bus current
* IR thermometer for cap and heatsink temps

## Running total

Roughly **$150–200** for the body and the first head, plus the pack you
already own. Each extra head is ~$40.
