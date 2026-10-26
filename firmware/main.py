"""ego-coil supervisor — MicroPython for Raspberry Pi Pico (RP2040).

Responsibilities
  * gate the ZVS stage on/off through Q3 (burst mode for power levels)
  * trip on overcurrent, overtemperature, run-time limit, pack under/over-voltage
  * fan control, status LED, fault beeps
  * short press while idle: cycle power level; hold: run

Behaviour summary
  idle      LED breathes green (level 1), blue (2), white (3)
  running   LED solid, buzzer silent
  fault     LED red, N beeps = fault code, latched until trigger released
  low pack  LED amber blink, refuses to start

Copy config.py and main.py to the Pico. main.py runs at boot.
"""
import math
import time
from machine import ADC, PWM, Pin, Timer

import config as C

# ----------------------------------------------------------------- hardware --
trigger = Pin(C.PIN_TRIGGER, Pin.IN, Pin.PULL_UP)
en = Pin(C.PIN_EN, Pin.OUT, value=0)
fan = Pin(C.PIN_FAN, Pin.OUT, value=0)
buzzer = Pin(C.PIN_BUZZER, Pin.OUT, value=0)
led = {k: PWM(Pin(p)) for k, p in (("r", C.PIN_LED_R), ("g", C.PIN_LED_G), ("b", C.PIN_LED_B))}
for pwm in led.values():
    pwm.freq(1000)
    pwm.duty_u16(0)

adc_cur = ADC(C.ADC_CURRENT)
adc_vp = ADC(C.ADC_VPACK)
adc_t = ADC(C.ADC_TEMP)

FAULT_NONE, FAULT_OVERCURRENT, FAULT_OVERTEMP, FAULT_TIMEOUT, FAULT_PACK_LOW, FAULT_PACK_HIGH = range(6)
FAULT_NAMES = ("ok", "overcurrent", "overtemp", "run limit", "pack low", "pack high")


# ------------------------------------------------------------------ sensing --
def _adc_v(adc, n=8):
    acc = 0
    for _ in range(n):
        acc += adc.read_u16()
    return (acc / n) * C.ADC_VREF / C.ADC_MAX


def read_current_a():
    if C.CURRENT_SENSOR == "shunt":
        return _adc_v(adc_cur) / (C.SHUNT_OHMS * C.INA_GAIN)
    v = _adc_v(adc_cur) * C.CUR_DIVIDER
    return (v - C.CUR_ZERO_V) / C.CUR_SENS_V_PER_A


def read_vpack():
    return _adc_v(adc_vp) * C.VPACK_DIVIDER


def read_temp_c():
    v = _adc_v(adc_t)
    if v <= 0.01 or v >= C.ADC_VREF - 0.01:
        return 25.0  # open or shorted NTC: do not trip on a wiring fault, but log it
    r = C.NTC_R_PULLUP * v / (C.ADC_VREF - v)
    inv_t = 1.0 / 298.15 + math.log(r / C.NTC_R25) / C.NTC_BETA
    return 1.0 / inv_t - 273.15


_id0 = Pin(C.PIN_HEAD_ID0, Pin.IN, Pin.PULL_UP)
_id1 = Pin(C.PIN_HEAD_ID1, Pin.IN, Pin.PULL_UP)


def detect_head():
    code = (_id1.value(), _id0.value())
    for name, h in C.HEADS.items():
        if h["code"] == code:
            return name
    return C.HEAD_DEFAULT


# ------------------------------------------------------------------ outputs --
def set_led(r, g, b):
    led["r"].duty_u16(int(r * 65535))
    led["g"].duty_u16(int(g * 65535))
    led["b"].duty_u16(int(b * 65535))


LEVEL_COLOURS = ((0, 1, 0), (0, 0.4, 1), (1, 1, 1))


def beep(n, on_ms=80, off_ms=120):
    for i in range(n):
        buzzer.value(1)
        time.sleep_ms(on_ms)
        buzzer.value(0)
        if i < n - 1:
            time.sleep_ms(off_ms)


# -------------------------------------------------------------- burst timer --
class Burst:
    """Toggles EN at BURST_HZ with a duty cycle. duty=1.0 holds EN high."""

    def __init__(self):
        self.timer = Timer()
        self.duty = 1.0
        self.active = False
        self.period_ms = int(1000 / C.BURST_HZ)

    def start(self, duty):
        self.duty = duty
        self.active = True
        if duty >= 0.999:
            en.value(1)
            return
        self._phase_on()

    def _phase_on(self, _t=None):
        if not self.active:
            return
        en.value(1)
        self.timer.init(mode=Timer.ONE_SHOT, period=max(1, int(self.period_ms * self.duty)),
                        callback=self._phase_off)

    def _phase_off(self, _t=None):
        en.value(0)
        if not self.active:
            return
        self.timer.init(mode=Timer.ONE_SHOT, period=max(1, int(self.period_ms * (1 - self.duty))),
                        callback=self._phase_on)

    def stop(self):
        self.active = False
        self.timer.deinit()
        en.value(0)


burst = Burst()


# ------------------------------------------------------------------- state --
class Supervisor:
    def __init__(self):
        self.level_idx = C.POWER_DEFAULT_IDX
        self.head = detect_head()
        self.fault = FAULT_NONE
        self.running = False
        self.run_started = 0
        self.run_stopped = -100000
        self.last_run_len_s = 0.0
        self.over_since = None
        self.press_started = None
        self.breath = 0.0
        print("head:", self.head, C.HEADS[self.head]["note"])

    # ---- helpers ----
    def duty(self):
        return min(C.POWER_LEVELS[self.level_idx], C.HEADS[self.head]["max_duty"])

    def trip(self, code):
        self.stop()
        self.fault = code
        print("TRIP:", FAULT_NAMES[code])
        set_led(1, 0, 0)
        beep(code)

    def start(self):
        self.running = True
        self.run_started = time.ticks_ms()
        self.over_since = None
        fan.value(1)
        set_led(*LEVEL_COLOURS[self.level_idx])
        burst.start(self.duty())
        print("RUN level", self.level_idx + 1, "duty", self.duty())

    def stop(self):
        if self.running:
            self.last_run_len_s = time.ticks_diff(time.ticks_ms(), self.run_started) / 1000
            print("STOP after %.1f s" % self.last_run_len_s)
        burst.stop()
        self.running = False
        self.run_stopped = time.ticks_ms()

    # ---- checks while running ----
    def check_running(self, now, i, v, t):
        if i > C.CURRENT_HARD_A:
            return self.trip(FAULT_OVERCURRENT)
        if i > C.CURRENT_TRIP_A:
            if self.over_since is None:
                self.over_since = now
            elif time.ticks_diff(now, self.over_since) > C.CURRENT_TRIP_MS:
                return self.trip(FAULT_OVERCURRENT)
        else:
            self.over_since = None
        if t > C.TEMP_TRIP_C:
            return self.trip(FAULT_OVERTEMP)
        if v < C.VPACK_MIN_LOAD:
            return self.trip(FAULT_PACK_LOW)
        if v > C.VPACK_MAX:
            return self.trip(FAULT_PACK_HIGH)
        if time.ticks_diff(now, self.run_started) > C.RUN_MAX_S * 1000:
            return self.trip(FAULT_TIMEOUT)

    def can_start(self, now, v, t):
        if self.fault != FAULT_NONE:
            return False
        if t > C.TEMP_RESUME_C:
            return False
        if v < C.VPACK_MIN_IDLE or v > C.VPACK_MAX:
            return False
        if self.last_run_len_s >= C.RUN_MAX_S * 0.9 and \
                time.ticks_diff(now, self.run_stopped) < C.COOLDOWN_S * 1000:
            return False
        return True

    # ---- idle UI ----
    def idle_ui(self, now, v, t):
        since_run = time.ticks_diff(now, self.run_stopped) / 1000
        fan.value(1 if (t > C.TEMP_FAN_ON_C or since_run < C.FAN_HOLD_S) else 0)
        if self.fault != FAULT_NONE:
            set_led(1, 0, 0)
            return
        if v < C.VPACK_MIN_IDLE:
            k = 1 if (now // 250) % 2 else 0
            set_led(k, 0.4 * k, 0)
            return
        self.breath = (self.breath + 0.02) % (2 * math.pi)
        a = 0.15 + 0.35 * (1 + math.sin(self.breath)) / 2
        r, g, b = LEVEL_COLOURS[self.level_idx]
        set_led(r * a, g * a, b * a)

    # ---- main loop ----
    def loop(self):
        while True:
            now = time.ticks_ms()
            pressed = trigger.value() == 0
            i, v, t = read_current_a(), read_vpack(), read_temp_c()

            if self.running:
                if not pressed:
                    self.stop()
                else:
                    self.check_running(now, i, v, t)
            else:
                if pressed:
                    if self.press_started is None:
                        self.press_started = now
                    held = time.ticks_diff(now, self.press_started)
                    if self.fault == FAULT_NONE and held > C.DEBOUNCE_MS and self.can_start(now, v, t) \
                            and held > C.LONG_PRESS_MS:
                        self.start()
                else:
                    if self.press_started is not None:
                        held = time.ticks_diff(now, self.press_started)
                        self.press_started = None
                        if self.fault != FAULT_NONE:
                            self.fault = FAULT_NONE       # release clears the latch
                            beep(1, 40, 0)
                        elif C.DEBOUNCE_MS < held < C.LONG_PRESS_MS:
                            self.level_idx = (self.level_idx + 1) % len(C.POWER_LEVELS)
                            beep(self.level_idx + 1, 40, 60)
                            print("level", self.level_idx + 1)
                    self.idle_ui(now, v, t)

            time.sleep_ms(C.LOOP_MS)


try:
    Supervisor().loop()
finally:
    burst.stop()
    en.value(0)
