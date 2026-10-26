#!/usr/bin/env python3
"""Render docs/schematic.svg with schemdraw (pip install schemdraw).

Three sheets stacked vertically:
  1. ZVS power stage + main switch + head tank
  2. Gate network detail (one side; the other mirrors it)
  3. Supervisor: supplies, sensing, driver
"""
import os
import schemdraw
import schemdraw.elements as elm

OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "schematic.svg")
schemdraw.use("svg")
FS = 9  # small label font


def sheet_power(d, y0=0.0):
    Y = lambda y: y + y0
    d += elm.Label().label("1. POWER STAGE + MAIN SWITCH + HEAD", fontsize=14, halign="left").at((0, Y(7.5)))

    # bus rail at y=5
    d += elm.Dot(open=True).label("EGO B+\n50–58 V", loc="left", fontsize=FS).at((0, Y(5)))
    d += elm.Fuse().right().length(2.5).label("F1 40 A", fontsize=FS)
    d += elm.Line().right().tox(3.5)
    d += (n_tvs := elm.Dot())
    d += elm.Line().right().tox(6)
    d += (n_bulk := elm.Dot())
    d += elm.Line().right().tox(10)
    d += (n_l1 := elm.Dot())
    d += elm.Line().right().tox(20)
    d += (n_l2 := elm.Dot())

    # TVS + bulk caps down to a local rail at y=2, which drops to the ground rail
    d += elm.Diode().at(n_tvs.start).down().reverse().length(3).label("TVS\nSMCJ70A", loc="bottom", fontsize=FS)
    d += elm.Dot()
    d += elm.Capacitor(polar=True).at(n_bulk.start).down().length(3).label("C1,C2\n2×1000 µF\n100 V", loc="bottom", fontsize=FS)
    d += (n_b2 := elm.Dot())
    d += elm.Line().at((3.5, Y(2))).to((6, Y(2)))
    d += elm.Line().at(n_b2.start).down().toy(Y(-11))
    d += (n_g_left := elm.Dot())

    # chokes down to drains
    d += elm.Inductor2(loops=4).at(n_l1.start).down().length(3).label("L1 47 µH", loc="left", fontsize=FS)
    d += elm.Line().down().toy(Y(0))
    d += (n_d1 := elm.Dot().label("D1", loc="left", fontsize=FS))
    d += elm.Inductor2(loops=4).at(n_l2.start).down().length(3).label("L2 47 µH", loc="right", fontsize=FS)
    d += elm.Line().down().toy(Y(0))
    d += (n_d2 := elm.Dot().label("D2", loc="right", fontsize=FS))

    # MOSFETs pointing down from the drain nodes
    d += (q1 := elm.NFet().theta(0).reverse().at(n_d1.start).anchor("drain").label("Q1\nIRFP4332", loc="bottom", fontsize=FS))
    d += (q2 := elm.NFet().theta(0).at(n_d2.start).anchor("drain").label("Q2\nIRFP4332", loc="bottom", fontsize=FS))
    d += elm.Line().at(q1.gate).left().length(0.8).label("gate net A", loc="left", fontsize=FS)
    d += elm.Line().at(q2.gate).right().length(0.8).label("gate net B", loc="right", fontsize=FS)

    # sources -> ZVS ground rail
    d += elm.Line().at(q1.source).down().toy(Y(-4))
    d += elm.Line().right().tox(20)
    d += elm.Line().at(q2.source).down().toy(Y(-4))
    d += (n_zg := elm.Dot().at((15, Y(-4))).label("ZVS GND", loc="right", fontsize=FS))

    # main switch Q3, precharge, hall sensor
    d += elm.Line().at(n_zg.start).down().length(1.2)
    d += (q3 := elm.NFet().theta(0).reverse().anchor("drain").label("Q3\nIRFB4110", loc="right", fontsize=FS))
    d += elm.Line().at(q3.gate).left().length(0.8).label("TC4420", loc="left", fontsize=FS)
    d += elm.Line().at(q3.drain).right().length(2.2)
    d += elm.Resistor().down().toy(q3.source).label("R_pre\n100 Ω 5 W", loc="right", fontsize=FS)
    d += elm.Line().left().tox(q3.source)
    d += elm.Dot()
    d += elm.Line().at(q3.source).down().length(1.0)
    d += elm.Resistor().down().length(1.6).label("R_sh 2×2 mΩ (1 mΩ)\n(Kelvin → INA180)", loc="left", fontsize=FS)
    d += elm.Line().down().toy(Y(-11))
    d += (n_g_r := elm.Dot())
    d += elm.Line().left().tox(0)
    d += elm.Dot(open=True).label("EGO B−", loc="left", fontsize=FS)

    # lead + head between the drains
    d += elm.Line().at(n_d1.start).right().tox(12)
    d += (xt_a := elm.Dot(open=True).label("XT90", loc="bottom", fontsize=FS))
    d += elm.Line().at(n_d2.start).left().tox(18)
    d += (xt_b := elm.Dot(open=True).label("XT90", loc="bottom", fontsize=FS))
    d += elm.Line().at(xt_a.start).right().tox(12.8)
    d += (h_a := elm.Dot())
    d += elm.Line().at(xt_b.start).left().tox(17.2)
    d += (h_b := elm.Dot())
    d += elm.Inductor2(loops=6).at(h_a.start).right().to(h_b.start).label("work coil 8t × 45 mm, ~1.4 µH", loc="bottom", fontsize=FS)
    d += elm.Line().at(h_a.start).up().length(2.2)
    d += elm.Capacitor().right().to((h_b.start[0], h_a.start[1] + 2.2)).label("C_tank  15 × 0.1 µF  630 V pulse-rated", loc="top", fontsize=FS)
    d += elm.Line().down().toy(h_b.start[1])
    d += elm.Label().label("HEAD", fontsize=12).at((15, Y(3.6)))
    d += elm.Label().label("twisted lead ≤ 25 cm", fontsize=FS).at((15, Y(-1.2)))


def sheet_gate(d, y0):
    Y = lambda y: y + y0
    d += elm.Label().label("2. GATE NETWORK, side A (side B mirrors: Q2 gate, diode to D1)",
                           fontsize=14, halign="left").at((0, Y(2)))
    d += elm.Dot(open=True).label("+12 V", loc="left", fontsize=FS).at((0, Y(0)))
    d += elm.Resistor().right().length(3).label("R_pu 100 Ω 3 W", fontsize=FS)
    d += (ng := elm.Dot().label("gate Q1", loc="top", fontsize=FS))
    d += elm.Line().right().length(1.5)
    d += (n2 := elm.Dot())
    d += elm.Diode().right().length(3).label("UF4007", loc="top", fontsize=FS)
    d += elm.Dot(open=True).label("drain D2", loc="right", fontsize=FS)
    d += elm.Zener().at(ng.start).down().reverse().length(2.5).label("15 V", loc="left", fontsize=FS)
    d += (nz := elm.Dot())
    d += elm.Resistor().at(n2.start).down().length(2.5).label("R_gs 10 k", loc="right", fontsize=FS)
    d += elm.Line().left().to(nz.start)
    d += elm.Line().at(nz.start).down().length(0.6)
    d += elm.Dot(open=True).label("ZVS GND (Q1 source)", loc="bottom", fontsize=FS)


def sheet_supervisor(d, y0):
    Y = lambda y: y + y0
    d += elm.Label().label("3. SUPERVISOR (Raspberry Pi Pico)", fontsize=14, halign="left").at((0, Y(2)))

    # supplies
    d += elm.Dot(open=True).label("fused bus", loc="left", fontsize=FS).at((0, Y(0)))
    d += elm.Line().right().length(1)
    d += elm.RBox().right().length(3.2).label("XL7015 buck\n5–80 V in → 12 V", fontsize=FS)
    d += elm.Line().right().length(1)
    d += elm.Dot().label("+12 V\ngate rail, fan, TC4420", loc="top", fontsize=FS)
    d += elm.Line().right().length(1.5)
    d += elm.RBox().right().length(3.2).label("MP1584 buck\n12 → 5 V", fontsize=FS)
    d += elm.Line().right().length(1)
    d += elm.Dot().label("+5 V\nPico VSYS, INA180", loc="top", fontsize=FS)

    pins = [elm.IcPin(name="ADC0", side="left", pin="GP26"),
            elm.IcPin(name="ADC1", side="left", pin="GP27"),
            elm.IcPin(name="ADC2", side="left", pin="GP28"),
            elm.IcPin(name="ID0", side="left", pin="GP22"),
            elm.IcPin(name="ID1", side="left", pin="GP21"),
            elm.IcPin(name="TRIG", side="left", pin="GP16"),
            elm.IcPin(name="EN", side="right", pin="GP15"),
            elm.IcPin(name="FAN", side="right", pin="GP14"),
            elm.IcPin(name="LED", side="right", pin="GP10-12"),
            elm.IcPin(name="BUZZ", side="right", pin="GP13")]
    d += (pico := elm.Ic(pins=pins, edgepadW=2, edgepadH=0.8, pinspacing=2.6, label="RP2040 Pico")
          .at((8, Y(-11))).anchor("center"))

    def shunt_to_gnd(pin, value):
        d.add(elm.Line().at(pin).left().length(1))
        d.add(elm.Dot())
        d.add(elm.Resistor().down().length(1.6).label(value, loc="right", fontsize=FS))
        d.add(elm.Ground())

    def shunt_to_3v3(pin, value):
        d.add(elm.Line().at(pin).left().length(1))
        d.add(elm.Dot())
        d.add(elm.Resistor().up().length(1.6).label(value, loc="right", fontsize=FS))
        d.add(elm.Vdd().label("3V3", fontsize=FS))

    # ADC0 current: INA180A1 across the shunt, output straight to the ADC
    d += elm.Line().at(pico.ADC0).left().length(1)
    d += elm.RBox().left().length(3.2).label("INA180A2\ngain 50", fontsize=FS)
    d += elm.Dot(open=True).label("R_sh Kelvin\n50 mV/A → 2.0 V @ 40 A", loc="left", fontsize=FS)
    # ADC1 pack voltage
    shunt_to_gnd(pico.ADC1, "5.6 k")
    d += elm.Line().at(pico.ADC1).left().length(1)
    d += elm.Resistor().left().length(2.5).label("100 k", fontsize=FS)
    d += elm.Dot(open=True).label("fused bus\n(V_pack)", loc="left", fontsize=FS)
    # ADC2 temperature
    shunt_to_3v3(pico.ADC2, "10 k")
    d += elm.Line().at(pico.ADC2).left().length(1)
    d += elm.Thermistor().left().length(2.5).label("NTC 10 k\non heatsink", fontsize=FS)
    d += elm.Ground()
    # head ID (digital, internal pull-ups; strap inside the head)
    for pin in (pico.ID0, pico.ID1):
        d += elm.Line().at(pin).left().length(1)
        d += elm.Switch().left().length(2.5).label("strap in head", fontsize=FS)
        d += elm.Ground()
    # trigger
    d += elm.Line().at(pico.TRIG).left().length(1)
    d += elm.Switch().left().length(2.5).label("trigger\n(internal pull-up)", fontsize=FS)
    d += elm.Ground()

    # outputs
    d += elm.Line().at(pico.EN).right().length(1)
    d += elm.RBox().right().length(2.4).label("TC4420", fontsize=FS)
    d += elm.Resistor().right().length(2).label("10 Ω", fontsize=FS)
    d += elm.Dot(open=True).label("Q3 gate", loc="right", fontsize=FS)

    d += elm.Line().at(pico.FAN).right().length(1)
    d += elm.Resistor().right().length(2).label("1 k", fontsize=FS)
    d += elm.Line().right().length(0.8)
    d += (qf := elm.NFet().theta(0).reverse().anchor("gate").label("2N7002", loc="right", fontsize=FS))
    d += elm.Line().at(qf.drain).up().length(0.5)
    d += elm.Dot(open=True).label("fan −  (fan + → 12 V)", loc="right", fontsize=FS)
    d += elm.Line().at(qf.source).down().length(0.3)
    d += elm.Ground()

    d += elm.Line().at(pico.LED).right().length(1)
    d += elm.Dot(open=True).label("RGB LED, 330 Ω each", loc="right", fontsize=FS)
    d += elm.Line().at(pico.BUZZ).right().length(1)
    d += elm.Dot(open=True).label("piezo buzzer", loc="right", fontsize=FS)


def main():
    with schemdraw.Drawing(file=OUT, show=False) as d:
        d.config(unit=2.5, fontsize=11)
        sheet_power(d, 0)
        sheet_gate(d, y0=-18)
        sheet_supervisor(d, y0=-26)
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
