#!/usr/bin/env python3
"""Synthetic example of the DIN Boxed publication style; not research results."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager


BLUE = "#5384EC"
RED = "#D85140"
YELLOW = "#F5B025"
INK = "#202020"
GRID = "#B8BDC5"
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic compact boxed plot")
    parser.add_argument("--output-stem", type=Path, default=Path("din-boxed-example"))
    parser.add_argument("--font", type=Path, help="Optional licensed regular font")
    parser.add_argument("--bold-font", type=Path, help="Optional matching bold font")
    return parser.parse_args()


def register_font(font_path: Path | None, bold_path: Path | None = None) -> str:
    if bold_path is not None and font_path is None:
        raise ValueError("--bold-font requires --font")
    if font_path is None:
        print("Compact boxed font: DejaVu Sans (default; DIN is not bundled)")
        return "DejaVu Sans"
    for path in (font_path, bold_path):
        if path is not None:
            if not path.is_file():
                raise FileNotFoundError(path)
            font_manager.fontManager.addfont(str(path))
    family = font_manager.FontProperties(fname=str(font_path)).get_name()
    print(f"Compact boxed font: {family} ({font_path})")
    return family


def style_axis(ax: plt.Axes) -> None:
    ax.grid(axis="y", color=GRID, linestyle=":", linewidth=0.55, zorder=0)
    ax.tick_params(
        axis="both",
        which="major",
        direction="out",
        top=True,
        right=True,
        length=3.0,
        width=0.75,
        pad=2.0,
    )
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(INK)
        spine.set_linewidth(0.65)


def main() -> None:
    args = parse_args()
    plt.rcParams.update(
        {
            "font.family": register_font(args.font, args.bold_font),
            "font.size": 8.0,
            "axes.labelsize": 9.0,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "text.color": INK,
            "axes.labelcolor": INK,
            "xtick.color": INK,
            "ytick.color": INK,
            "mathtext.fontset": "cm",
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    x = np.array([1, 2, 3, 4])
    series = {
        "Method A": (np.array([4.8, 3.1, 2.4, 2.0]), RED, "o", "-"),
        "Method B": (np.array([5.2, 3.8, 3.0, 2.7]), BLUE, "s", "--"),
        "Baseline": (np.array([6.0, 5.1, 4.7, 4.5]), YELLOW, "D", ":"),
    }

    fig, ax = plt.subplots(figsize=(2.3, 1.45))
    for label, (y, color, marker, linestyle) in series.items():
        ax.plot(
            x,
            y,
            color=color,
            marker=marker,
            linestyle=linestyle,
            linewidth=1.15,
            markersize=4.6,
            markerfacecolor=color,
            markeredgecolor=color,
            markeredgewidth=0.0,
            label=label,
            zorder=3,
        )

    style_axis(ax)
    ax.set_xlabel("Model size", math_fontfamily="cm")
    ax.set_ylabel("Error [a.u.]", math_fontfamily="cm")
    ax.set_xticks(x)
    ax.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=3,
        frameon=False,
        fontsize=7.0,
        handlelength=1.35,
        handletextpad=0.35,
        columnspacing=0.65,
    )

    fig.subplots_adjust(left=0.20, right=0.99, bottom=0.24, top=0.82)
    args.output_stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        args.output_stem.with_suffix(".pdf"),
        bbox_inches="tight",
        pad_inches=0.03,
        metadata={"Title": "Compact boxed plot — synthetic data, DejaVu Sans by default"},
    )
    fig.savefig(
        args.output_stem.with_suffix(".png"),
        dpi=600,
        bbox_inches="tight",
        pad_inches=0.03,
        facecolor="white",
    )
    plt.close(fig)


if __name__ == "__main__":
    main()
