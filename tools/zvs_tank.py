#!/usr/bin/env python3
"""ZVS induction heater tank calculator (current-fed Royer / ZVS).

Single-layer helical work coil (Wheeler's formula) + resonant capacitor bank.

Solid numbers : coil inductance (~+/-10%), resonant frequency, drain voltage
                (~pi x Vdc), circulating tank current and circulating VA.
Assumed number: real power draw. It depends on the LOADED Q of the tank (how
                much circulating energy the bolt soaks up per cycle). You can
                only measure that, so use --q and treat power as a range.

Examples:
  python zvs_tank.py --turns 8 --diameter 45 --pitch 9 --vdc 56 --caps 1.0 --n-caps 10
  python zvs_tank.py --turns 8 --diameter 45 --pitch 9 --vdc 56 --sweep
  python zvs_tank.py --turns 8 --diameter 45 --pitch 9 --freq 120
"""
import argparse
import math

MM_PER_IN = 25.4
SQ2 = math.sqrt(2)


def wheeler_uH(turns, mean_dia_mm, length_mm):
    """Wheeler's approximation, single-layer air-core solenoid.
    L(uH) = N^2 r^2 / (9r + 10l), r and l in inches."""
    r = (mean_dia_mm / 2) / MM_PER_IN
    l = length_mm / MM_PER_IN
    return (turns**2 * r**2) / (9 * r + 10 * l)


def resonant_freq(L_h, C_f):
    return 1 / (2 * math.pi * math.sqrt(L_h * C_f))


def cap_for_freq(L_h, f_hz):
    return 1 / ((2 * math.pi * f_hz) ** 2 * L_h)


def state(L_h, C_f, vdc):
    """Frequency, peak tank current and circulating VA for the ideal tank."""
    f = resonant_freq(L_h, C_f)
    xl = 2 * math.pi * f * L_h
    v_pk = math.pi * vdc          # ZVS drain swing
    i_pk = v_pk / xl              # circulating tank current
    va = v_pk * i_pk / 2          # circulating reactive power (RMS x RMS)
    return f, i_pk, va


def report(L_uH, C_uF, vdc, q, n_caps, loaded_factor):
    L = L_uH * 1e-6
    C = C_uF * 1e-6
    v_pk = math.pi * vdc
    print(f"Coil inductance   : {L_uH:.2f} uH empty, ~{L_uH*loaded_factor:.2f} uH with a bolt in it "
          f"(assumed x{loaded_factor})")
    print(f"Tank capacitance  : {C_uF:.3f} uF")
    print(f"Drain peak voltage: ~{v_pk:.0f} V ideal (real spikes run higher; keep 250 V parts)\n")

    rows = {}
    for label, Lx in (("empty", L), ("loaded", L * loaded_factor)):
        f, i_pk, va = state(Lx, C, vdc)
        rows[label] = (f, i_pk, va)
        print(f"{label:>7}: {f/1e3:6.1f} kHz | tank {i_pk:4.0f} A pk ({i_pk/SQ2:3.0f} A rms) "
              f"| circulating {va/1e3:5.1f} kVA")

    f_l, i_l, va_l = rows["loaded"]
    print(f"\nEstimated draw with a bolt in the coil (power = circulating VA / loaded Q):")
    for qq in sorted({5, q, 20}):
        p = va_l / qq
        print(f"  Q={qq:>4g}: ~{p:5.0f} W  ->  ~{p/vdc:4.0f} A from the pack")

    warns = []
    if v_pk > 200:
        warns.append(f"drain swing ~{v_pk:.0f} V leaves little margin on 250 V MOSFETs; use <=56 V.")
    if rows["empty"][0] > 200e3 or f_l < 40e3:
        warns.append("frequency outside ~40-200 kHz; MOSFET/gate-drive losses climb at the "
                     "high end. Add capacitance or coil turns.")
    if va_l / q / vdc > 40:
        warns.append(f"at Q={q:g} the pack current is over ~40 A; BMS will likely trip. "
                     "Raise Q/lower voltage/limit duty.")
    if n_caps:
        per = (i_l / SQ2) / n_caps
        print(f"\nPer-cap ripple: ~{per:.0f} A rms across {n_caps} caps (check the MKP datasheet).")
        if per > 15:
            warns.append("per-cap ripple above ~15 A rms; add more caps in parallel.")
    for w in warns:
        print(f"WARNING: {w}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--turns", type=float, required=True)
    ap.add_argument("--diameter", type=float, required=True,
                    help="coil MEAN diameter in mm (tube center to tube center)")
    ap.add_argument("--pitch", type=float, required=True,
                    help="turn-to-turn spacing in mm (1/4in tube is 6.35 mm, so >= ~7)")
    ap.add_argument("--vdc", type=float, default=56.0, help="supply voltage (EGO ~56-60 V)")
    ap.add_argument("--caps", type=float, help="total tank capacitance in uF")
    ap.add_argument("--freq", type=float, help="OR target (empty) frequency in kHz; solves for C")
    ap.add_argument("--n-caps", type=int, help="number of parallel caps (ripple estimate)")
    ap.add_argument("--q", type=float, default=10.0,
                    help="assumed LOADED tank Q (default 10; lower = more power into the bolt)")
    ap.add_argument("--loaded-factor", type=float, default=0.7,
                    help="L with steel in coil / L empty (default 0.7, measure it)")
    ap.add_argument("--sweep", action="store_true",
                    help="table of capacitance vs frequency / current / estimated power")
    a = ap.parse_args()

    length = a.turns * a.pitch
    L_uH = wheeler_uH(a.turns, a.diameter, length)

    if a.sweep:
        Ll = L_uH * 1e-6 * a.loaded_factor
        print(f"Coil: {a.turns:g} turns, {a.diameter:g} mm dia, {a.pitch:g} mm pitch "
              f"-> {L_uH:.2f} uH empty, ~{L_uH*a.loaded_factor:.2f} uH loaded")
        print(f"All columns are for the LOADED coil at {a.vdc:g} V, assumed Q={a.q:g}\n")
        print(f"{'C uF':>6} {'f kHz':>7} {'Itank pk':>9} {'kVA':>6} {'P est W':>8} {'Idc A':>6}")
        for c in (0.33, 0.47, 0.68, 1.0, 1.5, 2.0):
            f, i, va = state(Ll, c * 1e-6, a.vdc)
            p = va / a.q
            print(f"{c:6.2f} {f/1e3:7.1f} {i:9.0f} {va/1e3:6.1f} {p:8.0f} {p/a.vdc:6.1f}")
        return

    if a.freq:
        C_uF = cap_for_freq(L_uH * 1e-6, a.freq * 1e3) * 1e6
        print(f"For {a.freq:g} kHz (empty) you need ~{C_uF:.3f} uF total.\n")
    elif a.caps:
        C_uF = a.caps
    else:
        ap.error("give --caps or --freq (or --sweep)")
    report(L_uH, C_uF, a.vdc, a.q, a.n_caps, a.loaded_factor)


if __name__ == "__main__":
    main()
