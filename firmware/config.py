"""ego-coil supervisor configuration. Edit here, not in main.py."""

# ---- pins (Raspberry Pi Pico GP numbers) ----
PIN_TRIGGER = 16      # momentary to GND, internal pull-up
PIN_EN = 15           # -> TC4420 input -> Q3 gate (HIGH = stage on)
PIN_FAN = 14          # -> 1k -> 2N7002 gate (HIGH = fan on)
PIN_BUZZER = 13       # active piezo
PIN_LED_R = 10
PIN_LED_G = 11
PIN_LED_B = 12
ADC_CURRENT = 0       # GP26  current sense (see CURRENT_SENSOR)
ADC_VPACK = 1         # GP27  bus via 100k/5.6k
ADC_TEMP = 2          # GP28  10k NTC to GND, 10k pull-up to 3V3
# Head ID: a 3-pin JST-XH beside the XT90 carries ID0, ID1 and GND. Inside
# each head, each ID pin is either left open or strapped to GND -> 4 codes.
# The Pico has only three ADC inputs and they are all used, so the ID is
# digital. Pins use internal pull-ups.
PIN_HEAD_ID0 = 22
PIN_HEAD_ID1 = 21
HEAD_DEFAULT = "nut"

# ---- sensing scale factors ----
ADC_VREF = 3.3
ADC_MAX = 65535                      # read_u16()
# "shunt": 2 mOhm shunt + INA180A1 (gain 20) -> 0.040 V/A, zero at 0 V, no divider
# "hall":  ACS758LCB-050B via 10k/10k divider -> 2.5 V zero, 0.040 V/A at the sensor
CURRENT_SENSOR = "shunt"
SHUNT_OHMS = 0.002
INA_GAIN = 20.0
CUR_DIVIDER = 2.0                    # hall only: 10k/10k
CUR_ZERO_V = 2.5                     # hall only: ACS758 zero-current output
CUR_SENS_V_PER_A = 0.040             # hall only: ACS758LCB-050B
VPACK_DIVIDER = (100e3 + 5.6e3) / 5.6e3
NTC_R_PULLUP = 10000.0
NTC_R25 = 10000.0
NTC_BETA = 3950.0

# ---- trip thresholds ----
CURRENT_TRIP_A = 38.0        # pack BMS is typically 40-60 A; trip first
CURRENT_TRIP_MS = 20         # sustained above threshold before tripping
CURRENT_HARD_A = 48.0        # instantaneous trip, no filtering
TEMP_FAN_ON_C = 40.0
TEMP_TRIP_C = 70.0
TEMP_RESUME_C = 55.0
VPACK_MIN_IDLE = 48.0        # refuse to start below this (empty pack)
VPACK_MIN_LOAD = 46.0        # stop if it sags below this under load
VPACK_MAX = 60.0             # something is wrong above this
RUN_MAX_S = 20.0             # continuous run limit
COOLDOWN_S = 10.0            # minimum rest after a max-length run
FAN_HOLD_S = 60.0            # keep fan on after a run

# ---- burst-mode power levels ----
BURST_HZ = 20
# duty per level; the ZVS restarts on every burst, so a floor of ~30 % keeps
# each burst long enough (15 ms) for the oscillator to settle
POWER_LEVELS = (0.40, 0.70, 1.00)
POWER_DEFAULT_IDX = 2

# ---- heads ----
# code: (ID1, ID0) as read with pull-ups, 1 = open, 0 = strapped to GND.
# (1, 1) = nothing strapped = no ID connector fitted = default head.
# max_duty: cap on burst duty for coils that run hot or at high frequency
HEADS = {
    "nut":     {"code": (1, 1), "max_duty": 1.00, "note": "8t x 45 mm, 1.5 uF"},
    "pencil":  {"code": (1, 0), "max_duty": 0.70, "note": "5t x 25 mm, 2 uF, ~200 kHz"},
    "pancake": {"code": (0, 1), "max_duty": 1.00, "note": "6t spiral 60 mm, 2 uF"},
    "spare":   {"code": (0, 0), "max_duty": 0.70, "note": "unassigned"},
}

# ---- misc ----
LOOP_MS = 5
DEBOUNCE_MS = 30
LONG_PRESS_MS = 600
