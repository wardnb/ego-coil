# ego-coil — bill of materials

Two columns: **Budget** is the sub-$100 build this repo targets; **Reference**
is the name-brand part if you'd rather not gamble on a marketplace listing.
The circuit is the same either way. Prices are rough 2026 single-unit
figures; "AE" = AliExpress/eBay/Amazon marketplace, "Mouser" = Mouser/Digi-Key.
Verify every rating against the datasheet before you order.

The four things that blew the first budget, and what replaced them:

| Was | Now | Saves |
|---|---|---|
| 15 × CDE 940C resonant caps ($25) | 5 × 0.33 µF 1200 V CBB81 pulse caps, or free ones from a scrapped induction cooktop | ~$17 |
| RECOM R-78HB12 + R-78E5.0 ($17) | XL7015 80 V buck module + MP1584 mini buck | ~$13 |
| ACS758 Hall sensor ($8) | 2 mΩ shunt + INA180A1 | ~$5 |
| ANL fuse + holder ($8), new heatsink + fan ($15) | MAXI blade fuse + holder; CPU cooler from a scrap PC | ~$15 |

And one that isn't on the list but matters most: **print the EGO dock**
instead of buying an adapter ($15–25). Published models exist (search
"EGO 56V battery adapter" on Printables/Thingiverse).

## Body — power stage

| Qty | Part | Budget | $ | Reference | $ |
|---|---|---|---|---|---|
| 4 | MOSFET Q1/Q2 + 2 spares, **250 V** TO-247 | IRFP4332PbF, Mouser (don't buy these on AE — fakes are common and a fake here costs you the pack) | 18 | same | 18 |
| 2 | Choke L1/L2, ~47 µH, ≥ 20 A | wind 30 t of 14 AWG on a sendust/Kool-Mµ toroid salvaged from a PC PSU output filter, or AE "47 µH 20 A toroidal" | 4 | Magnetics 77083 cores + wire | 12 |
| 2 | Gate pull-up 100 Ω 3 W | AE wirewound | 1 | Vishay | 1 |
| 2 | Feedback diode | UF4007 | 0.5 | MUR460 | 1 |
| 2 | Gate zener 15 V 1.3 W | 1N5929B | 0.5 | same | 0.5 |
| 2 | Gate-source 10 kΩ | — | — | — | — |
| 2 | Bulk cap 1000 µF 100 V | AE / scrap (ATX PSU primary caps are 200 V 470 µF — also fine) | 3 | Nichicon UHE | 6 |
| 2 | Film bypass 1 µF 100 V | — | 1 | — | 2 |
| 1 | TVS SMCJ70A | — | 1 | — | 1 |
| 1 | Fuse 40 A + holder | MAXI blade fuse + inline holder (auto parts) | 3 | ANL + holder | 8 |
| 1 | Heatsink for 2 × TO-247 | CPU cooler from a scrap PC (comes with a fan) | 0 | 100 × 60 × 25 mm finned | 10 |
| 2 | TO-247 insulator kit | silpad + shoulder washer | 1 | — | 2 |
| 1 | Fan 12 V 40–60 mm | from the CPU cooler | 0 | — | 5 |
| 1 | XT90 panel-mount female | AE pair | 2 | — | 3 |
| 1 m | 10 AWG silicone wire, red/black | — | 4 | — | 5 |
| 1 | Proto board + copper strip for the heavy nets | — | 2 | — | 3 |

## Body — main switch and supervisor

| Qty | Part | Budget | $ | Reference | $ |
|---|---|---|---|---|---|
| 1 | Q3 IRFB4110PbF (100 V, 4.5 mΩ) | Mouser | 2 | same | 2 |
| 1 | Gate driver TC4420CPA | Mouser | 1.5 | same | 1.5 |
| 1 | Q3 gate 10 Ω, pull-down 10 kΩ | — | — | — | — |
| 1 | Pre-charge 100 Ω 5 W across Q3 | — | 1 | — | 1 |
| 1 | Current shunt 2 mΩ 5 W | metal-strip, Kelvin leads | 1 | — | 1 |
| 1 | INA180A1 (gain 20) on a breakout | SOT-23 + adapter, or AE module | 1.5 | — | 1.5 |
| — | *(alternative)* ACS758LCB-050B Hall + 10 k/10 k | — | — | — | 8 |
| 2 | Pack-voltage divider 100 k / 5.6 k 1 % | — | — | — | — |
| 1 | NTC 10 k B3950, ring-lug | — | 1 | — | 2 |
| 1 | 12 V buck, **≥ 80 V input** | XL7015 module ("DC-DC 80 V to 12 V"); confirm its input cap is ≥ 80 V | 3 | RECOM R-78HB12-0.5 | 12 |
| 1 | 5 V from 12 V | MP1584 mini buck module | 1 | RECOM R-78E5.0-0.5 | 5 |
| 1 | Raspberry Pi Pico | — | 4 | — | 5 |
| 1 | Trigger, 16 mm momentary | — | 2 | — | 2 |
| 1 | RGB LED + 3 × 330 Ω, piezo | — | 1 | — | 1 |
| 1 | JST-XH 3-pin pair (head ID) | — | 1 | — | 1 |
| 1 | 2N7002 + 1 k (fan switch) | — | 0.5 | — | 0.5 |

## Body — pack interface

| Qty | Part | Budget | $ | Reference | $ |
|---|---|---|---|---|---|
| 1 | EGO 56 V dock | **print** a published EGO adapter model; add two M4 bolts + ring terminals for B+/B− | 2 | bought DIY adapter with screw terminals | 20 |
| 1 | EGO pack 5 Ah+ | already own | 0 | — | — |

## Head (reference 8-turn nut coil)

| Qty | Part | Budget | $ | Reference | $ |
|---|---|---|---|---|---|
| ~1.2 m | 1/4" soft copper refrigeration tube | hardware store | 6 | — | 6 |
| ~1.5 µF | Resonant caps, ≥ 630 V, pulse-rated PP | 5 × 0.33 µF 1200 V CBB81 (sold for ZVS heaters), **or free** 0.27–0.3 µF 1200 V caps from a scrapped induction cooktop | 8 | 15 × CDE 940C6P1K-F | 25 |
| 2 | Copper bus bar 20 × 2 × 80 mm | cut from 1/2" copper pipe flattened, or AE strip | 2 | — | 4 |
| 1 | XT90 male + 15 cm 10 AWG twisted pigtail | — | 1 | — | 3 |
| 1 | JST-XH 3-pin pigtail + strap | — | 0.5 | — | 1 |
| — | PTFE / fibreglass sleeve for turn spacing | — | 2 | — | 3 |
| 1 | Shell, printed in PC / PA-CF / ASA | filament | 2 | — | 2 |

## Totals

| | Budget | Reference |
|---|---|---|
| Body — power stage | ~$41 | ~$78 |
| Body — switch + supervisor | ~$21 | ~$42 |
| Dock | ~$2 | ~$20 |
| Head | ~$22 | ~$44 |
| **Total** | **~$86** | ~$185 |

The budget total assumes a scrap CPU cooler and a printed dock. With a new
heatsink and fan it is ~$100; with a bought dock ~$115. Each extra head is
~$20 on the budget column.

Where **not** to save: the two IRFP4332s (fakes), the resonant caps (must be
pulse-rated), and the fuse. Everything else on the budget column is a
commodity.

## Tools you need on hand

* Oscilloscope ≥ 50 MHz with a ×10 probe — drain waveforms are the only way to
  know the stage is healthy. A $40 used analogue scope is fine for this.
* LC meter (cheap "transistor tester" units read µH well enough)
* Bench supply, 0–30 V, current-limited, for bring-up
* DC clamp meter
* IR thermometer
