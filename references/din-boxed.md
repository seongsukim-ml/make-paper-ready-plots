# DIN Boxed style

Use this profile for compact parameter-scaling and convergence figures. Preserve the analytical structure of the requested chart; this profile controls presentation, not what should be plotted.

## Typography

- Recommend DIN 2014 for this profile and for matching the public gallery. Provide a licensed regular font using `--font` and optionally its bold face with `--bold-font`. No DIN font files are included.
- Register both regular and bold faces. Use Computer Modern mathtext (`mathtext.fontset = "cm"`) for LaTeX-style equations, Greek letters, and mathematical symbols. Set `axes.unicode_minus = False` when ASCII hyphens are preferred for ordinary tick labels.
- When passing a file-backed `FontProperties`, set its size directly; otherwise it can override a separate `fontsize` argument with its default size.
- Do not pass a file-backed DIN `FontProperties` to a mixed text-and-math string such as `r"Occ. number, $\lambda_i$"`; it can make the math inherit the text face. Set DIN globally through `rcParams`, use ordinary `fontsize` and `fontweight` arguments, and set `math_fontfamily="cm"` on the text artist.
- Keep numeric ticks outside math delimiters so they remain DIN. If log ticks must look like `10` with a raised exponent, draw the base and exponent as separate ordinary DIN text artists instead of using `$10^{-4}$`.
- Report the font actually used. Without an explicit font, use DejaVu Sans consistently across machines.
- Keep `pdf.fonttype = 42` and `ps.fonttype = 42`.
- For a compact single-column figure, start with labels at `9 pt`, annotations and legend at `8 pt`, and ticks at `8 pt`.
- Keep labels regular unless a short title or direct data annotation genuinely needs emphasis.
- The repository license does not grant rights to third-party fonts. Check embedding permissions for any font supplied locally.

## Layout and axes

- Start near `2.3 in x 1.45 in` for a small single panel, then expand only as required by the content.
- Use a white background and all four spines in near-black at about `0.65 pt`.
- Point major ticks outward and show them on the top and right. Start with `3 pt` tick length.
- Prefer hand-selected major ticks and plain numeric labels, especially on log axes.
- Draw quiet dotted horizontal major grids only: `#B8BDC5`, `0.5--0.65 pt`. Omit vertical grids unless exact x alignment is central to the comparison.
- Keep outer whitespace tight without clipping labels. Export with about `0.03 in` padding.

## Lines, markers, and color

Use the compact boxed palette when it fits the semantics:

- blue `#5384EC`
- red `#D85140`
- yellow `#F5B025`
- neutral gray `#757575`
- optional orange `#C45C1C`

Use filled markers around `4.5--5.0 pt` and lines around `1.0--1.3 pt`. Do not add a white marker border by default. Retain marker shape or line-style distinctions so color is not the only encoding. Use a thin gray dashed line for a reference or previous-best level.

## Legend and export

- Prefer one compact horizontal legend above the axes or in an unused corner.
- Set `frameon=False` unless the legend overlaps data and needs separation.
- Render PDF and PNG. Use `600 dpi` for very small figures and `300 dpi` otherwise.
- Inspect the PNG at intended paper size and validate both files with `scripts/validate_static_plot.py`.
