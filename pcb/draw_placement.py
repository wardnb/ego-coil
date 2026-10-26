#!/usr/bin/env python3
"""Draw the board placement plan (pcb/placement.svg) to scale, 100 x 80 mm."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch

W, H = 100, 80
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(-2, W + 2); ax.set_ylim(-2, H + 2); ax.set_aspect("equal"); ax.axis("off")
ax.add_patch(Rectangle((0, 0), W, H, fill=False, lw=2))


def box(x, y, w, h, label, color="#dddddd", fs=8):
    ax.add_patch(Rectangle((x, y), w, h, fc=color, ec="k", lw=0.8))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs)


def pad(x, y, label):
    ax.add_patch(Circle((x, y), 3.5, fc="#f5c542", ec="k")); ax.text(x, y - 6, label, ha="center", fontsize=7)


# mounting holes
for x, y in ((4, 4), (W - 4, 4), (4, H - 4), (W - 4, H - 4)):
    ax.add_patch(Circle((x, y), 1.6, fc="w", ec="k"))

# --- heavy side (left 55 mm) ---
ax.add_patch(Rectangle((0, 0), 55, H, fc="#fff3e0", ec="none", zorder=0))
ax.text(27, H - 3, "POWER STAGE — 2 oz, 6 mm+ traces, copper wire reinforced", ha="center", fontsize=8, weight="bold")
pad(8, 66, "J1 B+")
pad(8, 54, "J2 B−")
box(16, 48, 10, 24, "C1\nC2\n1000µ", "#ffe0b2")
box(28, 62, 8, 8, "D5\nTVS", "#c8e6c9")
box(13, 32, 12, 14, "L1", "#ffe0b2")
box(27, 32, 12, 14, "L2", "#ffe0b2")
box(2, 6, 16, 22, "Q1\nTO-247", "#bbdefb")
box(20, 6, 16, 22, "Q2\nTO-247", "#bbdefb")
ax.text(19, 2, "Q1/Q2 tabs flush with board edge → bolt flat to heatsink", ha="center", fontsize=7)
pad(46, 20, "J3 D1")
pad(46, 10, "J4 D2")
box(40, 48, 12, 6, "R1 100Ω", "#e0e0e0", 6); box(40, 56, 12, 6, "R2 100Ω", "#e0e0e0", 6)
box(42, 32, 8, 4, "D7", "#e0e0e0", 6); box(42, 38, 8, 4, "D8", "#e0e0e0", 6)
box(42, 44, 8, 4, "ZD1/2", "#e0e0e0", 6)
ax.text(19, 30, "gate net: ≤15 mm loops, over the ZVS_GND pour", ha="center", fontsize=6.5, style="italic")

# --- main switch + shunt (middle) ---
box(56, 6, 12, 20, "Q3\nTO-220", "#bbdefb")
box(70, 6, 6, 10, "R6\nR7\n2512", "#c8e6c9", 6)
ax.text(73, 18, "Kelvin\n→ U2", ha="center", fontsize=6)
box(56, 28, 12, 5, "R3 100Ω 5W", "#e0e0e0", 6)
box(78, 8, 8, 6, "U2\nINA180", "#c8e6c9", 6)
box(78, 16, 8, 6, "U1\nTC4420", "#e0e0e0", 6)
ax.text(70, 36, "ZVS_GND pour under Q1/Q2/Q3; GND pour under everything else", ha="center", fontsize=6.5, style="italic")

# --- supplies ---
box(58, 42, 14, 10, "U3\nXL7015 12V", "#e1bee7", 7)
box(74, 42, 12, 10, "U4\nMP1584 5V", "#e1bee7", 7)
box(88, 42, 6, 10, "C8", "#e1bee7", 6)

# --- Pico + I/O (right) ---
ax.add_patch(Rectangle((56, 54), 42, 24, fc="#e3f2fd", ec="none", zorder=0))
box(60, 56, 21, 20, "Pico (socketed)\nA1 / A2", "#bbdefb", 8)
for i, lbl in enumerate(("J5 NTC", "J6 FAN", "J7 TRIG", "J8 ID", "J9 LED", "J10 BZ")):
    box(84, 56 + i * 3.4, 12, 3, lbl, "#fff9c4", 6)
ax.text(78, H - 3, "SUPERVISOR — JLC-assembled SMD here", ha="center", fontsize=8, weight="bold")

# current loop arrow
ax.add_patch(FancyArrowPatch((10, 72), (10, 28), arrowstyle="->", mutation_scale=12, color="red", lw=1.2))
ax.text(12, 44, "40 A loop:\nB+ → C1/C2 → L1/L2\n→ Q1/Q2 → ZVS_GND\n→ Q3 → shunt → B−\nkeep it short & wide",
        fontsize=6.5, color="red", va="center")

plt.tight_layout()
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "placement.svg")
plt.savefig(out, bbox_inches="tight"); print("wrote", out)
