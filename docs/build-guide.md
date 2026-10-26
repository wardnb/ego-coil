# Build guide

Start to finish, in the order that keeps the expensive parts alive. Budget a
weekend for the build and an evening for bring-up. Don't skip bring-up.

## 0. Before you order anything

- Read `design.md` §6 (safety). Decide now whether you're happy with the
  field strength near your own body; if anyone in your household has an
  implanted device, this isn't the project for your garage.
- Check you have, or can borrow: an oscilloscope (≥ 50 MHz, ×10 probe), a
  bench supply with current limit, an LC meter, a DC clamp meter, an IR
  thermometer. Bring-up without a scope is guesswork that costs MOSFETs.
- Measure your EGO pack against `dock-measurement.md` to confirm the supplied
  dock STL matches your pack generation (the blade slots and rail spacing are
  the tell).

## 1. Order

1. **PCB.** Follow `pcb/README.md`: import the netlist into KiCad, place per
   the plan, route, DRC, export Gerbers. Order 5 boards at JLCPCB, 2 oz copper,
   with economic assembly for the parts marked SMT in `pcb/bom.csv`. Fill the
   LCSC column first. ~2 weeks.
2. **Through-hole and heavy parts** from `bom.md`. Buy the IRFP4332s from
   Mouser or Digi-Key, not a marketplace; buy four.
3. **Resonant caps** for the head: 5 × 0.33 µF 1200 V CBB81, or pull the
   0.27–0.3 µF 1200 V caps out of a scrapped induction cooktop.
4. **Copper tube**, 1/4" soft refrigeration, 1.5 m.
5. Filament: PETG for the body and dock, PC / PA-CF / ASA for the head.

## 2. Print

While the boards ship: `python cad/build_cad.py`, then print from `cad/out/`
plus `cad/ego56v_dock.stl`. Settings are in `cad/README.md`. Add the four
countersunk holes to the dock in the slicer (`dock-measurement.md` §1).

## 3. Wind the coil and build the head

1. Wind 8 turns of 1/4" tube on a 38 mm mandrel (a socket works) so the mean
   diameter lands near 45 mm. Leave two 40 mm straight tails on 14 mm centres.
   Slip PTFE or fibreglass sleeve over the tube first so the turns can't touch.
2. **Measure the inductance.** Expect ~1.4 µH empty. Write it down.
3. Run the calculator with your number:
   `python tools/zvs_tank.py --turns 8 --diameter 45 --pitch 9 --caps 1.5`
   and adjust `--caps` until the empty frequency is 100–130 kHz. That's your
   cap bank.
4. Solder the caps between two 20 × 2 mm copper bars, as short as the caps
   allow. Clamp the coil tails to the bar ends with M4 bolts (or solder with a
   big iron). Wire a 15 cm twisted 10 AWG pigtail to an XT90 male; add the
   JST-XH head-ID pigtail with the strap for this head type
   (`firmware/config.py`).
5. Fit it all in the printed head shell with the coil tails through the
   standoff block. Nothing conductive may touch the shell except through an
   air gap or a ceramic/silicone sleeve.

## 4. Populate the board

Order of soldering: lowest profile first.

1. Check the JLC-assembled side under magnification: INA180 orientation, no
   bridges on the 2512 shunts.
2. Pico sockets, JST headers, buck-module headers, TC4420 in a DIP socket.
3. Gate network through-hole parts (R1/R2, D7/D8, ZD1/ZD2). Check diode
   direction twice: D7 is gate-Q1 → drain-Q2, D8 is gate-Q2 → drain-Q1.
4. Electrolytics C1/C2/C8, R3 pre-charge resistor.
5. Chokes L1/L2: 30 turns of 14 AWG on the toroid, leads short.
6. Q3 with its small heatsink. Q1/Q2 **last**, after the board is mounted so
   their tabs sit flat on the main heatsink with silpads and shoulder washers.
   Check with a meter that neither tab is shorted to the heatsink.
7. Solder 1.5 mm copper wire along the heavy traces (B+ → caps → chokes,
   drains → J3/J4, sources → Q3 → shunt → B−).
8. M4 ring terminals on 10 AWG for J1–J4.

## 5. Bring-up — the part that matters

Do this with the **bench supply, not the battery**, head connected, Pico
*not* fitted (so Q3 is off). Temporarily bridge Q3 drain-source with a wire
for steps 1–3.

1. **24 V, current limit 3 A, no bolt in the coil.** Scope Q1 drain, ×10
   probe, ground on ZVS_GND. You want a clean half-sine, ~75 V peak (π × 24),
   at ~110 kHz, with the other drain showing the same thing interleaved. The
   supply should draw 1–2 A.
   - Draws the limit and flat waveforms: both FETs on. Power off *now*; check
     gate network wiring and diode direction.
   - Oscillates but with a spike at the zero crossing: lead too long or
     untwisted, or gate pull-up too weak. Shorten the lead; try 68 Ω.
   - No oscillation: gate rail present? (12 V at R1/R2.) Zeners backwards?
2. **Bolt in the coil.** Frequency rises 10–20 %; current rises a lot. Set
   the supply limit to 5 A and watch the drain peak stays below 100 V. Heat
   for 10 s, then IR-thermometer the caps: under 50 °C is fine.
3. **36 V if your supply does it**, same checks. Drain peaks ~115 V.
4. Remove the Q3 bridge, fit the Pico with the firmware, connect trigger and
   LED. At 24 V: short press cycles levels (beeps), hold runs, release stops.
   Temporarily set `CURRENT_TRIP_A = 2.0` in `config.py` and confirm it trips
   and latches with a bolt in; put it back to 38.
5. Check the NTC reads room temperature (REPL: `read_temp_c()`) and `VSENSE`
   matches the supply voltage.

## 6. First battery run

Outdoors or on a concrete floor, nothing flammable within arm's reach, fire
extinguisher in sight.

1. Dock a pack that's at least half charged. The LED should breathe. If it
   blinks amber, the pack reads below 48 V.
2. Hold the trigger with the coil empty for 2 s. Listen: a faint whine at
   ~110 kHz is normal. Release.
3. Put a 1/2" bolt in the coil, hold for 5 s. It should glow dull red by the
   end. Clamp-meter the B+ lead: expect 15–30 A depending on the bolt.
4. Full 20 s run on the same bolt, then check heatsink temp (fan should be
   on) and cap temp in the head.
5. If the pack cuts out mid-run (everything dies, LED off), its BMS tripped
   before the firmware did: lower `CURRENT_TRIP_A` by 4 A and try again.

## 7. Using it

- Short press: cycle power level (1/2/3 beeps). Level 3 is full duty; level 1
  is for small fasteners and the pencil head.
- Hold: run. Release: stop. Max 20 s, then a 10 s cooldown.
- Red LED + beeps = fault, count the beeps (1 overcurrent, 2 overtemp, 3 run
  limit, 4 pack low, 5 pack high). Release the trigger to clear.
- Let the fan run after use; don't dock the body with a hot heatsink in a
  closed toolbox.

## 8. Write down what you measured

Coil inductance, empty and loaded frequency, pack current on a known bolt,
cap temperature after 20 s. Those four numbers are what turn this from a
design into a tested one; open an issue with them.
