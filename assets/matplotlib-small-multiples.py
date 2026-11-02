import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter


def parse_args():
    parser = argparse.ArgumentParser(description="Synthetic small-multiples example")
    parser.add_argument("--output-stem", type=Path, required=True)
    parser.add_argument("--font", type=Path)
    parser.add_argument("--bold-font", type=Path)
    return parser.parse_args()


X = np.array([30.0, 100.0, 300.0, 700.0, 1800.0])
X_LABELS = ["30M", "100M", "300M", "700M", "1800M"]
PANELS = {
    "Panel A": {
        "Primary": np.array([950.0, 320.0, 180.0, 130.0, 115.0]),
        "Comparator": np.array([205.0, 160.0, 122.0]),
    },
    "Panel B": {
        "Primary": np.array([960.0, 325.0, 185.0, 132.0, 117.0]),
        "Comparator": np.array([208.0, 162.0, 124.0]),
    },
    "Panel C": {
        "Primary": np.array([1850.0, 590.0, 330.0, 220.0, 190.0]),
        "Comparator": np.array([350.0, 270.0, 205.0]),
    },
}
COMPARATOR_X = np.array([130.0, 510.0, 1340.0])

COLORS = {"Primary": "#62B5F4", "Comparator": "#94C973"}
STYLES = {
    "Primary": dict(marker="o", linestyle="-"),
    "Comparator": dict(marker="D", linestyle="-"),
}


def resolve_font(path):
    if path is not None:
        font_manager.fontManager.addfont(str(path))
        return font_manager.FontProperties(fname=str(path)).get_name()
    return "DejaVu Sans"


def format_x_tick(value, _position):
    for x_value, label in zip(X, X_LABELS):
        if np.isclose(value, x_value):
            return label
    return ""


def format_y_tick(value, _position):
    labels = {100: "100", 300: "300", 1000: "1000", 3000: "3000"}
    return labels.get(round(value), "")


def main():
    args = parse_args()
    args.output_stem.parent.mkdir(parents=True, exist_ok=True)
    if args.bold_font is not None:
        if args.font is None:
            raise ValueError("--bold-font requires --font")
        font_manager.fontManager.addfont(str(args.bold_font))
    font_family = resolve_font(args.font)
    plt.rcParams.update(
        {
            "font.family": font_family,
            "font.size": 8.0,
            "axes.titlesize": 9.4,
            "axes.titleweight": "normal",
            "axes.labelsize": 8.8,
            "axes.labelweight": "normal",
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 7.4,
            "axes.edgecolor": "#202020",
            "axes.linewidth": 0.8,
            "text.color": "#171717",
            "axes.labelcolor": "#171717",
            "xtick.color": "#171717",
            "ytick.color": "#171717",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    fig, axes = plt.subplots(1, len(PANELS), figsize=(3.4 * len(PANELS), 2.60), sharex=True, sharey=True)
    axes = np.atleast_1d(axes)

    for ax, (title, series) in zip(axes, PANELS.items()):
        for name, y in series.items():
            x = X if name == "Primary" else COMPARATOR_X
            ax.plot(
                x,
                y,
                color=COLORS[name],
                linewidth=1.35,
                markersize=5.0,
                markerfacecolor=COLORS[name],
                markeredgecolor="white",
                markeredgewidth=0.55,
                label=name,
                zorder=3,
                **STYLES[name],
            )

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(23, 2250)
        ax.set_ylim(80, 3000)
        ax.xaxis.set_major_locator(FixedLocator(X))
        ax.xaxis.set_major_formatter(FuncFormatter(format_x_tick))
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.yaxis.set_major_locator(FixedLocator([100, 300, 1000, 3000]))
        ax.yaxis.set_major_formatter(FuncFormatter(format_y_tick))
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.grid(axis="y", which="major", color="#B8BDC5", linestyle=":", linewidth=0.65, zorder=0)
        ax.tick_params(which="minor", length=0)
        ax.tick_params(axis="x", which="major", length=3.0, width=0.75, pad=3)
        ax.tick_params(axis="y", which="major", length=3.0, width=0.75, pad=2)
        ax.tick_params(labelleft=True)

        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color("#202020")
            spine.set_linewidth(0.8)

        ax.set_title(title, pad=5, fontweight="normal")
        ax.set_xlabel("Parameters", labelpad=5, fontweight="normal")
        ax.set_ylabel("Error [a.u.]", labelpad=5, fontweight="normal")

        legend = ax.legend(
            loc="upper right",
            fontsize=6.8,
            frameon=True,
            framealpha=1.0,
            facecolor="white",
            edgecolor="#303030",
            borderpad=0.35,
            handlelength=2.1,
            handletextpad=0.45,
            labelspacing=0.25,
        )
        legend.get_frame().set_linewidth(0.65)

    fig.subplots_adjust(left=0.07, right=0.99, bottom=0.22, top=0.91, wspace=0.31)
    stem = args.output_stem
    metadata = {
        "Title": "Paper-ready small-multiple comparison",
        "Subject": "Reusable Matplotlib publication figure template",
        "Author": "Synthetic demonstration data",
    }
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", pad_inches=0.03, metadata=metadata)
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight", pad_inches=0.03, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
