---
name: make-paper-ready-plots
description: Create, revise, and validate clean publication-ready Python and Matplotlib figures, including the compact DIN Boxed style. Use when Codex needs to make experiment-result plots, parameter-scaling curves, MAE/RMSE comparisons, log or log-log small multiples, optional power-law fits, paper figures inspired by a reference image, or polished PDF and PNG exports with restrained typography, ticks, grids, legends, colors, and markers.
---

# Make Paper-Ready Plots

Build reproducible static figures that are visually quiet, analytically honest, and ready to place in a paper.

## Workflow

1. Inspect the supplied data, plot script, reference image, and requested output paths. Preserve raw numeric precision.
2. State a compact chart contract internally: comparison, panel layout, axes and units, series, palette, non-color distinctions, optional statistical overlays, and final file formats.
3. Read [references/style-guide.md](references/style-guide.md) before editing or writing plot code.
4. Select the requested style:
   - Use the default guide and [assets/matplotlib-small-multiples.py](assets/matplotlib-small-multiples.py) for ordinary 1-by-N experiment plots.
   - For **DIN Boxed**, compact boxed, or DIN figures, also read [references/din-boxed.md](references/din-boxed.md) and start from [assets/matplotlib-din-boxed.py](assets/matplotlib-din-boxed.py).
   - Otherwise adapt the closest existing project script rather than rebuilding its visual language.
   - For additional manuscript examples, see [density-matrix figures](examples/density-matrix/README.md). Their molecular renderings are visual references, not a molecular-rendering workflow.
   - For QHFlow2 visual references, see [the original figure gallery](examples/qhflow2/README.md). Use its layout as a reference; use the user’s supplied data for new figures.
5. Read [references/power-law.md](references/power-law.md) only when the user requests scaling or power-law fitting.
6. Prefer fonts already present in the project. For DIN Boxed figures, use a user-supplied licensed DIN font when available; otherwise use DejaVu Sans. This public package does not include DIN font files. Register regular and bold faces when supplied and use Computer Modern mathtext (`mathtext.fontset = "cm"`) for LaTeX-style equations and symbols. For mixed labels such as `r"Occ. number, $\lambda_i$"`, set `math_fontfamily="cm"` on the text artist and avoid a file-backed `FontProperties` on the entire string. Use a user-supplied Noto Sans CJK KR font when appropriate for Korean text; otherwise use one consistent readable family.
   Keep numeric tick labels in the surrounding text font rather than wrapping them in `$...$`. For DIN scientific-notation ticks that need raised exponents, compose the base and exponent from separate ordinary DIN text artists.
7. Render both PDF and 300-dpi PNG unless the user requests another format. Keep the plotting script beside the outputs.
8. Inspect the final PNG at its delivered size. Revise collisions, clipping, excessive whitespace, weak contrast, crowded legends, and misleading scales.
9. Run:

   ```bash
   python scripts/validate_static_plot.py figure.png figure.pdf
   ```

10. Return links to the PDF, PNG, and plotting script.

The default and DIN Boxed styles are separate profiles; DIN Boxed specifics override the default marker, tick, and legend settings. Example arrays are synthetic, not research results.

## Default Decisions

- Use top panel titles rather than bottom subcaptions unless explicitly requested.
- Keep x/y titles regular weight; do not bold them by default.
- Show complete numeric y ticks such as `1000` and `3000`; do not abbreviate them as `1k` or `3k` unless requested.
- Use thin boxed axes, short ticks, and quiet dotted horizontal major grids.
- Use solid circles for the primary series, dashed triangles for a secondary metric, and solid diamonds for a comparator family.
- Give every marker a thin white edge for a clean printed appearance.
- Use a light sky blue, deeper blue, light green, and neutral gray as the default two-series-plus-reference palette.
- Keep line widths and marker sizes consistent across peer series. Distinguish series with shape and line style as well as color.
- When exact overlap hides discrete observations, keep lines at the true coordinates and apply a small horizontal dodge to markers only. Preserve every y value and disclose the visual offset in the caption.
- Put the same compact legend in each panel when the user asks for per-panel legends or when panels may be separated in a paper.
- Split a comparison into a focused MAE-only or metric-only figure when extra series compress the relevant range or create crossing-line clutter.
- Add a statistical fit only when requested. Keep it lighter than observations and identify exactly which points were fitted.

## Guardrails

- Do not infer a power-law fit, regression, trend line, or uncertainty band without a request or clear analytical need.
- Do not connect unrelated configurations merely because they share an x-axis.
- Do not mix RMSE with an MAE-focused architectural comparison when RMSE dominates the y-range.
- Do not rely on color alone; retain marker and line-style distinctions.
- Do not use library-default categorical colors in a shipped figure.
- Do not deliver without inspecting the rendered output.
- Verify that every substring inside `$...$`, including math embedded in an otherwise DIN label, renders in Computer Modern rather than inheriting the surrounding text face.
- DIN font files are not distributed. Use only fonts the user is entitled to use and embed; see `THIRD_PARTY_NOTICES.md`. Public examples use DIN 2014 supplied locally; DejaVu Sans is the fallback when DIN is unavailable.
