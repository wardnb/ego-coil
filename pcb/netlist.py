#!/usr/bin/env python3
"""ego-coil main board — circuit as code (SKiDL) → KiCad netlist.

    pip install skidl
    python pcb/netlist.py          # writes pcb/ego-coil.net + pcb/bom.csv

Open KiCad 8/9 → new project → PCB editor → File ▸ Import ▸ Netlist → pick
ego-coil.net. Footprints reference the standard KiCad libraries; a few are
flagged "ADJUST" below because they depend on the exact module/choke you buy.
Placement rules are in pcb/README.md.

Parts are defined inline (no KiCad symbol libs needed to run this). Each
part carries fields the JLCPCB BOM plugin reads: `JLC` = "SMT" for parts
JLCPCB assembles, "THT" for hand-soldered, and `LCSC` left for you to fill
from the JLC parts search (numbers change; verify at order time).
"""
import os
from skidl import (ERC, KICAD8, Net, Part, Pin, SKIDL, generate_netlist, set_default_tool)

set_default_tool(SKIDL)
HERE = os.path.dirname(os.path.abspath(__file__))


# ----------------------------------------------------------- part factory --
def P(ref, value, footprint, pins, jlc="THT", desc="", lcsc=""):
    """Inline part. pins: list of (number, name, func) with func in
    'in','out','pwr','pas','bidir'."""
    T = Pin.types
    fmap = {"in": T.INPUT, "out": T.OUTPUT, "pwr": T.PWRIN, "pas": T.PASSIVE, "bidir": T.BIDIR}
    p = Part(name=value, tool=SKIDL, value=value, footprint=footprint)
    for num, name, func in pins:
        p.add_pins(Pin(num=str(num), name=name, func=fmap[func]))
    p.ref = ref
    p.fields["JLC"] = jlc
    p.fields["LCSC"] = lcsc
    p.fields["Desc"] = desc
    return p


def R(ref, value, fp="Resistor_SMD:R_0805_2012Metric", jlc="SMT", desc=""):
    return P(ref, value, fp, [(1, "1", "pas"), (2, "2", "pas")], jlc, desc or f"{value} resistor")


def C(ref, value, fp="Capacitor_SMD:C_0603_1608Metric", jlc="SMT", desc=""):
    return P(ref, value, fp, [(1, "1", "pas"), (2, "2", "pas")], jlc, desc or f"{value} capacitor")


def D(ref, value, fp, jlc="THT", desc=""):
    return P(ref, value, fp, [(1, "K", "pas"), (2, "A", "pas")], jlc, desc)


def NFET(ref, value, fp, jlc="THT", desc=""):
    return P(ref, value, fp, [(1, "G", "in"), (2, "D", "pas"), (3, "S", "pas")], jlc, desc)


def HDR(ref, n, desc, fp=None, jlc="THT"):
    fp = fp or f"Connector_PinHeader_2.54mm:PinHeader_1x{n:02d}_P2.54mm_Vertical"
    return P(ref, f"HDR{n}", fp, [(i, str(i), "pas") for i in range(1, n + 1)], jlc, desc)


def M4PAD(ref, desc):
    return P(ref, "M4", "MountingHole:MountingHole_4.3mm_M4_Pad", [(1, "1", "pas")], "THT", desc)


# ------------------------------------------------------------------- nets --
gnd = Net("GND")            # pack negative / supervisor ground
vpack = Net("VPACK")        # after the off-board fuse
d1, d2 = Net("D1"), Net("D2")
zgnd = Net("ZVS_GND")       # MOSFET sources
q3s = Net("SHUNT_HI")       # Q3 source / shunt high side
v12, v5, v33 = Net("+12V"), Net("+5V"), Net("+3V3")
gate_a, gate_b = Net("GATE_A"), Net("GATE_B")
ks_hi, ks_lo = Net("KELVIN_HI"), Net("KELVIN_LO")
isense = Net("ISENSE")
vsense = Net("VSENSE")
tsense = Net("TSENSE")
en, q3g = Net("EN"), Net("Q3_GATE")
fan_n = Net("FAN_N")
id0, id1 = Net("HEAD_ID0"), Net("HEAD_ID1")
trig = Net("TRIG")
ledr, ledg, ledb, buzz = Net("LED_R"), Net("LED_G"), Net("LED_B"), Net("BUZZ")
fan_g = Net("FAN_GATE")
fan_en = Net("FAN_EN")
led_rp, led_gp, led_bp = Net("LED_R_P"), Net("LED_G_P"), Net("LED_B_P")
for n in (gnd, vpack, d1, d2, zgnd, q3s, v12, v5, v33):
    n.drive = 5  # treat as driven so ERC doesn't complain about passives-only nets

# -------------------------------------------------------- heavy I/O pads --
j_bplus = M4PAD("J1", "Pack B+ (from inline 40 A fuse), ring terminal, 10 AWG")
j_bminus = M4PAD("J2", "Pack B−, ring terminal, 10 AWG")
j_d1 = M4PAD("J3", "Lead to XT90 pin 1 (D1), 10 AWG")
j_d2 = M4PAD("J4", "Lead to XT90 pin 2 (D2), 10 AWG")
j_bplus[1] += vpack
j_bminus[1] += gnd
j_d1[1] += d1
j_d2[1] += d2

# ------------------------------------------------------ input protection --
tvs = D("D5", "SMCJ70A", "Diode_SMD:D_SMC", "SMT", "TVS 70 V standoff, SMC")
tvs["K"] += vpack
tvs["A"] += gnd
c1 = C("C1", "1000uF/100V", "Capacitor_THT:CP_Radial_D18.0mm_P7.50mm", "THT", "Bulk electrolytic, low ESR")
c2 = C("C2", "1000uF/100V", "Capacitor_THT:CP_Radial_D18.0mm_P7.50mm", "THT", "Bulk electrolytic, low ESR")
c3 = C("C3", "1uF/100V", "Capacitor_SMD:C_1210_3225Metric", "SMT", "X7R 100 V bypass at choke feed")
c4 = C("C4", "1uF/100V", "Capacitor_SMD:C_1210_3225Metric", "SMT", "X7R 100 V bypass at choke feed")
for c in (c1, c2, c3, c4):
    c[1] += vpack
    c[2] += gnd

# ------------------------------------------------------------ ZVS stage --
# chokes: toroid footprint is a placeholder — ADJUST to the core you wind
l1 = P("L1", "47uH/20A", "Inductor_THT:L_Toroid_Horizontal_D28.0mm_P30.00mm_Fastron_DSP",
       [(1, "1", "pas"), (2, "2", "pas")], "THT", "Choke, 30 t 14 AWG on sendust toroid (ADJUST footprint)")
l2 = P("L2", "47uH/20A", "Inductor_THT:L_Toroid_Horizontal_D28.0mm_P30.00mm_Fastron_DSP",
       [(1, "1", "pas"), (2, "2", "pas")], "THT", "Choke, 30 t 14 AWG on sendust toroid (ADJUST footprint)")
l1[1] += vpack
l1[2] += d1
l2[1] += vpack
l2[2] += d2

q1 = NFET("Q1", "IRFP4332", "Package_TO_SOT_THT:TO-247-3_Vertical", desc="250 V 57 A, heatsink, Mouser only")
q2 = NFET("Q2", "IRFP4332", "Package_TO_SOT_THT:TO-247-3_Vertical", desc="250 V 57 A, heatsink, Mouser only")
q1["D"] += d1
q1["S"] += zgnd
q1["G"] += gate_a
q2["D"] += d2
q2["S"] += zgnd
q2["G"] += gate_b

# gate networks (A drives Q1, feedback diode to D2; B mirrors)
for side, gate, other_drain, rp, df, zd_, rg in (("A", gate_a, d2, "R1", "D7", "ZD1", "R17"),
                                                  ("B", gate_b, d1, "R2", "D8", "ZD2", "R18")):
    rpu = R(rp, "100R/3W", "Resistor_THT:R_Axial_DIN0918_L18.0mm_D6.0mm_P22.86mm_Horizontal", "THT",
            "Gate pull-up from +12 V, wirewound 3 W")
    rpu[1] += v12
    rpu[2] += gate
    dfb = D(df, "UF4007", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", "THT", "Gate→opposite drain feedback")
    dfb["A"] += gate
    dfb["K"] += other_drain
    zd = D(zd_, "15V/1.3W", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", "THT", "Gate zener clamp")
    zd["K"] += gate
    zd["A"] += zgnd
    rgs = R(rg, "10k", desc="Gate-source hold-off")
    rgs[1] += gate
    rgs[2] += zgnd

# ------------------------------------------------- main switch + sensing --
q3 = NFET("Q3", "IRFB4110", "Package_TO_SOT_THT:TO-220-3_Vertical", desc="100 V 4.5 mΩ burst switch, small heatsink")
q3["D"] += zgnd
q3["S"] += q3s
q3["G"] += q3g
rpre = R("R3", "100R/5W", "Resistor_THT:R_Axial_Power_L20.0mm_W6.4mm_P25.40mm", "THT", "Bulk-cap pre-charge across Q3")
rpre[1] += zgnd
rpre[2] += q3s
rg3 = R("R4", "10R", desc="Q3 gate resistor")
rg3[1] += q3g
rpd3 = R("R5", "10k", desc="Q3 gate pull-down")
rpd3[1] += q3g
rpd3[2] += gnd

# shunt: 2 × 2 mΩ 2512 in parallel = 1 mΩ 6 W; Kelvin taps from the pads
rsh1 = R("R6", "2mR/3W", "Resistor_SMD:R_2512_6332Metric", "SMT", "Shunt, metal strip 2512 3 W")
rsh2 = R("R7", "2mR/3W", "Resistor_SMD:R_2512_6332Metric", "SMT", "Shunt, metal strip 2512 3 W")
for r in (rsh1, rsh2):
    r[1] += q3s
    r[2] += gnd
# Kelvin nets are routed as separate thin traces from the shunt pads; in the
# netlist they are the same copper, so tie them here and keep the rule in
# the layout (see README).
ks_hi += q3s
ks_lo += gnd

u2 = P("U2", "INA180A2", "Package_TO_SOT_SMD:SOT-23-5",
       [(1, "OUT", "out"), (2, "GND", "pwr"), (3, "IN+", "in"), (4, "IN-", "in"), (5, "V+", "pwr")],
       "SMT", "Current-sense amp, gain 50 → 50 mV/A with 1 mΩ")
u2["IN+"] += ks_hi
u2["IN-"] += ks_lo
u2["GND"] += gnd
u2["V+"] += v5
u2["OUT"] += isense
c5 = C("C5", "100nF", desc="INA180 decoupling")
c5[1] += v5
c5[2] += gnd
c6 = C("C6", "10nF", desc="ISENSE filter (with trace R≈1k) ~16 kHz")
r8 = R("R8", "1k", desc="ISENSE series / filter")
r8[1] += isense
isense_f = Net("ISENSE_F")
r8[2] += isense_f
c6[1] += isense_f
c6[2] += gnd

# pack voltage divider
r9 = R("R9", "100k", desc="V_pack divider top, 1 %")
r10 = R("R10", "5.6k", desc="V_pack divider bottom, 1 %")
r9[1] += vpack
r9[2] += vsense
r10[1] += vsense
r10[2] += gnd
c7 = C("C7", "100nF", desc="VSENSE filter")
c7[1] += vsense
c7[2] += gnd

# NTC on a header, 10 k pull-up
j_ntc = HDR("J5", 2, "NTC 10 k B3950 on heatsink, JST-XH 2p",
            "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical")
r11 = R("R11", "10k", desc="NTC pull-up to 3V3, 1 %")
r11[1] += v33
r11[2] += tsense
j_ntc[1] += tsense
j_ntc[2] += gnd

# ------------------------------------------------------------- supplies --
# 12 V and 5 V are bought modules on 4-pin headers: IN+, IN-, OUT+, OUT-  (ADJUST pitch to module)
u3 = HDR("U3", 4, "XL7015 buck module 5–80 V → 12 V (IN+ IN- OUT+ OUT-)")
u3[1] += vpack
u3[2] += gnd
u3[3] += v12
u3[4] += gnd
u4 = HDR("U4", 4, "MP1584 buck module 12 → 5 V (IN+ IN- OUT+ OUT-)")
u4[1] += v12
u4[2] += gnd
u4[3] += v5
u4[4] += gnd
c8 = C("C8", "100uF/25V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", "THT", "+12 V rail bulk")
c8[1] += v12
c8[2] += gnd
c9 = C("C9", "10uF", "Capacitor_SMD:C_0805_2012Metric", desc="+5 V bulk")
c9[1] += v5
c9[2] += gnd

# ------------------------------------------------------------ Q3 driver --
u1 = P("U1", "TC4420CPA", "Package_DIP:DIP-8_W7.62mm",
       [(1, "NC", "pas"), (2, "IN", "in"), (3, "NC2", "pas"), (4, "GND", "pwr"),
        (5, "GND2", "pwr"), (6, "OUT", "out"), (7, "OUT2", "pas"), (8, "VDD", "pwr")],
       "THT", "6 A MOSFET driver, TTL input")
u1["IN"] += en
u1["GND"] += gnd
u1["GND2"] += gnd
u1["OUT"] += rg3[2]
u1["OUT2"] += rg3[2]
u1["VDD"] += v12
c10 = C("C10", "1uF", "Capacitor_SMD:C_0805_2012Metric", desc="TC4420 decoupling, close to pin 8")
c10[1] += v12
c10[2] += gnd
r12 = R("R12", "10k", desc="EN pull-down: stage off while Pico boots")
r12[1] += en
r12[2] += gnd

# --------------------------------------------------------------- fan sw --
q4 = P("Q4", "2N7002", "Package_TO_SOT_SMD:SOT-23", [(1, "G", "in"), (2, "S", "pas"), (3, "D", "pas")],
       "SMT", "Fan low-side switch")
r13 = R("R13", "1k", desc="Fan gate")
r13[1] += fan_en
r13[2] += fan_g
q4["G"] += fan_g
q4["S"] += gnd
q4["D"] += fan_n
j_fan = HDR("J6", 2, "Fan 12 V, JST-XH 2p (+12 V, FAN_N)", "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical")
j_fan[1] += v12
j_fan[2] += fan_n
d6 = D("D6", "1N4148W", "Diode_SMD:D_SOD-123", "SMT", "Fan flyback")
d6["A"] += fan_n
d6["K"] += v12

# ------------------------------------------------------------- UI I/O ---
j_trig = HDR("J7", 2, "Trigger, JST-XH 2p", "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical")
j_trig[1] += trig
j_trig[2] += gnd
j_id = HDR("J8", 3, "Head ID, JST-XH 3p (ID0, ID1, GND) → panel", "Connector_JST:JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical")
j_id[1] += id0
j_id[2] += id1
j_id[3] += gnd
j_led = HDR("J9", 4, "RGB LED common cathode (R, G, B, GND), JST-XH 4p",
            "Connector_JST:JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical")
for i, (net, ref) in enumerate(((led_rp, "R14"), (led_gp, "R15"), (led_bp, "R16")), start=1):
    r = R(ref, "330R", desc="LED series")
    r[1] += net
    r[2] += j_led[i]
j_led[4] += gnd
j_buz = HDR("J10", 2, "Piezo buzzer, JST-XH 2p", "Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical")
j_buz[1] += buzz
j_buz[2] += gnd

# ------------------------------------------------------------------ Pico --
# Two 1x20 sockets. Pin numbers are the Pico's physical pins.
pico_l = HDR("A1", 20, "Pico socket, pins 1–20", "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical")
pico_r = HDR("A2", 20, "Pico socket, pins 21–40", "Connector_PinSocket_2.54mm:PinSocket_1x20_P2.54mm_Vertical")


def pico(pin):
    return pico_l[pin] if pin <= 20 else pico_r[pin - 20]


for g in (3, 8, 13, 18, 23, 28, 33, 38):
    gnd += pico(g)
v5 += pico(39)          # VSYS
v33 += pico(36)         # 3V3(OUT)
led_rp += pico(14)   # GP10
led_gp += pico(15)   # GP11
led_bp += pico(16)   # GP12
buzz += pico(17)             # GP13
fan_en += pico(19)    # GP14
en += pico(20)               # GP15
trig += pico(21)             # GP16
id1 += pico(27)              # GP21
id0 += pico(29)              # GP22
isense_f += pico(31)         # GP26 / ADC0
vsense += pico(32)           # GP27 / ADC1
tsense += pico(34)           # GP28 / ADC2

# --------------------------------------------------------- mounting holes --
for i in range(1, 5):
    P(f"H{i}", "M3", "MountingHole:MountingHole_3.2mm_M3", [], "THT", "M3 standoff")


# ----------------------------------------------------------------- output --
def write_bom(path):
    rows = []
    for p in default_circuit.parts:  # noqa: F821  (SKiDL builtin)
        rows.append((p.ref, p.value, p.footprint, p.fields.get("JLC", ""), p.fields.get("LCSC", ""),
                     p.fields.get("Desc", "")))
    rows.sort(key=lambda r: (r[3], r[0]))
    with open(path, "w") as f:
        f.write("Ref,Value,Footprint,Assembly,LCSC,Description\n")
        for r in rows:
            f.write(",".join('"%s"' % str(x).replace('"', "'") for x in r) + "\n")
    return len(rows)


if __name__ == "__main__":
    ERC()
    out = os.path.join(HERE, "ego-coil.net")
    generate_netlist(file_=out, tool=KICAD8)
    n = write_bom(os.path.join(HERE, "bom.csv"))
    print(f"wrote {out} and bom.csv ({n} parts)")
