#!/usr/bin/env python3
"""Rebuild the public gallery using deterministic synthetic data only."""
from pathlib import Path
import argparse
import subprocess
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BLUE, GREEN, GRAY = "#62B5F4", "#94C973", "#A3A8AE"


def style(ax):
    ax.grid(axis="y", which="major", color="#B8BDC5", linestyle=":", linewidth=.65)
    ax.set_axisbelow(True)
    ax.tick_params(which="major", length=3, width=.75)
    for spine in ax.spines.values():
        spine.set_color("#202020")
        spine.set_linewidth(.8)


def save(fig, out, name):
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight", pad_inches=.03,
                metadata={"Title": name, "Subject": "Synthetic demonstration, not research results"})
    fig.savefig(out / f"{name}.png", dpi=300, bbox_inches="tight", pad_inches=.03, facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "examples" / "gallery")
    parser.add_argument("--font", type=Path, help="Recommended: licensed DIN 2014 regular font")
    parser.add_argument("--bold-font", type=Path, help="Optional matching bold font")
    args = parser.parse_args()
    if args.bold_font and not args.font:
        parser.error("--bold-font requires --font")
    family = "DejaVu Sans"
    pdf_font_name = "DejaVuSans"
    for font_path in (args.font, args.bold_font):
        if font_path:
            font_manager.fontManager.addfont(str(font_path))
    if args.font:
        family = font_manager.FontProperties(fname=str(args.font)).get_name()
        pdf_font_name = font_manager.get_font(str(args.font)).postscript_name
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    for script, name in [("matplotlib-small-multiples.py", "small-multiples"),
                         ("matplotlib-din-boxed.py", "compact-boxed")]:
        command = [sys.executable, str(ROOT / "assets" / script),
                   "--output-stem", str(out / name)]
        if args.font:
            command += ["--font", str(args.font.resolve())]
        if args.bold_font:
            command += ["--bold-font", str(args.bold_font.resolve())]
        subprocess.run(command, check=True)

    with plt.rc_context({"font.family": family, "font.size": 9,
                         "axes.labelsize": 9, "axes.titlesize": 10,
                         "legend.fontsize": 8, "mathtext.fontset": "cm",
                         "pdf.fonttype": 42, "ps.fonttype": 42}):
        # Fixed illustrative scores: neither measured results nor uncertainty estimates.
        categories = ["Full model", "Without gate", "Shared head", "Linear head"]
        values = np.array([1.42, 1.88, 1.71, 2.36])
        fig, ax = plt.subplots(figsize=(4.8, 2.8), layout="constrained")
        bars = ax.bar(np.arange(4), values, width=.58,
                      color=[BLUE, GREEN, GREEN, GREEN], edgecolor="white", linewidth=.6)
        bars[0].set_hatch("///")
        bars[0].set_edgecolor("#426FF5")
        ax.bar_label(bars, fmt="%.2f", padding=4, fontsize=8)
        ax.set_xticks(np.arange(4), categories)
        ax.set_ylim(0, 2.85)
        ax.set_ylabel("MAE [a.u.]")
        ax.set_title("Architecture ablation · synthetic data", loc="left", pad=10)
        style(ax)
        save(fig, out, "ablation")

        # Descriptive OLS fit on exactly the first four synthetic points.
        x = np.array([30., 100., 300., 700., 1800.])
        y = np.array([950., 450., 225., 140., 120.])
        b, log_a = np.polyfit(np.log(x[:4]), np.log(y[:4]), 1)
        a = np.exp(log_a)
        curve_x = np.geomspace(x.min(), x.max(), 150)
        fig, ax = plt.subplots(figsize=(4.8, 2.8), layout="constrained")
        ax.plot(curve_x, a * curve_x**b, color=GRAY, linestyle="-.", linewidth=1.2,
                label="Fit on first 4 points", zorder=2)
        ax.plot(x[:4], y[:4], "o", color=BLUE, markersize=6, markeredgecolor="white",
                markeredgewidth=.55, label="Fitted observations", zorder=3)
        ax.plot(x[4:], y[4:], "o", color=BLUE, markerfacecolor="white", markersize=6,
                label="Excluded comparison point", zorder=3)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(23, 2400)
        ax.set_ylim(65, 1500)
        ax.set_xticks(x, ["30M", "100M", "300M", "700M", "1800M"])
        ax.set_yticks([100, 300, 1000], ["100", "300", "1000"])
        ax.minorticks_off()
        ax.set_xlabel("Parameters")
        ax.set_ylabel("MAE [a.u.]")
        ax.set_title("Parameter scaling · synthetic data", loc="left", pad=10)
        style(ax)
        legend = ax.legend(loc="upper right", framealpha=1, edgecolor="#303030")
        legend.get_frame().set_linewidth(.65)
        save(fig, out, "scaling-fit")
        log_y = np.log(y[:4])
        residual = log_y - (log_a + b * np.log(x[:4]))
        r2 = 1 - np.sum(residual**2) / np.sum((log_y - log_y.mean())**2)
        print(f"Synthetic scaling: exponent={b:.4f}, log-space R²={r2:.4f}; "
              f"last point excluded. Extrapolation is illustrative only.")

    for png in sorted(out.glob("*.png")):
        subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_static_plot.py"),
                        str(png), str(png.with_suffix(".pdf")),
                        "--font-substring", pdf_font_name], check=True)


if __name__ == "__main__":
    main()
