# Matplotlib paper-plot style guide

## Composition

- Prefer 1-by-N small multiples for the same metric across related outputs.
- Share x and y scales when panels are directly comparable.
- Start around `3.4 in` width per panel and `2.6 in` height for a compact horizontal figure.
- Use panel titles above axes with normal weight and a small pad.
- Avoid redundant figure titles, subcaptions, cards, shadows, and colored backgrounds.

## Typography

- Use one font family across titles, labels, ticks, and legends.
- Recommend DIN 2014 when the user has a licensed copy. Otherwise use DejaVu Sans or an explicitly supplied project font. Korean labels require a supplied font with Korean glyphs, such as Noto Sans CJK KR.
- Good starting sizes for a 1-by-3 figure: body `8.0`, panel title `9.4`, axis label `8.8`, x tick `7.2`, y tick `7.4`, legend `6.8` points.
- Keep axis-label and panel-title weight normal unless emphasis is explicitly requested.
- Embed TrueType fonts with `pdf.fonttype = 42` and `ps.fonttype = 42`.

## Axes and ticks

- Use `#202020` spines at about `0.8 pt`.
- Keep all four spines visible for the compact boxed style used in this project.
- Use major ticks around `3 pt` long and suppress minor tick labels and lengths when they add noise.
- On parameter axes, position ticks at the real numeric values and format labels as rounded `28M`, `112M`, and so on.
- On log y-axes, use `FixedLocator` and `FuncFormatter` to show full values such as `100`, `300`, `1000`, `3000`, `10000`.
- Choose limits from all observations and requested overlays. Leave enough room for extrapolated curves without excessive blank space.
- Label quantities and units directly, for example `Parameters [M]` and `Matrix MAE ↓ [1e-6]`.

## Grid and background

- Use a white background.
- Draw horizontal major grids only: `#B8BDC5`, dotted, about `0.65 pt`, behind data.
- Avoid vertical grids unless x-alignment is the main analytical task.

## Series styling

- Primary: sky blue `#62B5F4`, solid line, circle marker.
- Secondary metric: deep blue `#426FF5`, dashed line, triangle marker.
- Comparator family: light green `#94C973`, solid line, diamond marker.
- Statistical/reference overlay: light neutral gray `#A3A8AE`, thin dash-dot line.
- Use peer line widths around `1.35–1.45` and marker sizes around `5.0`.
- Use white marker edges around `0.55 pt` for all filled peer markers.
- Use an open marker only to convey a real state, such as a point excluded from fitting.

## Legends

- Use a white legend box with a thin dark border, no transparency, and compact spacing.
- Place it in the upper right when that region is data-free.
- Repeat it in each panel when requested or when panels may be reused independently.
- Prefer a shared legend only when repeated legends materially reduce plotting space.
- Remove series before shrinking legend text below a readable size.

## Clutter decisions

- Keep the reader's main comparison to two or three visual layers per panel.
- If a comparator overlaps the main metric while RMSE occupies a much larger range, make a separate MAE-only figure.
- Do not overlay a power-law line on a clean architecture-comparison figure unless the fit is part of the question.
- Avoid adding x ticks for closely spaced comparator parameters when labels would collide; keep exact x placement and explain values in text or a table.

## Export and QA

- Save PDF with tight bounding box and small padding around `0.03 in`.
- Save PNG at 300 dpi with a white face color.
- Close the figure after saving.
- Inspect the actual PNG for clipped labels, collisions, detached legends, weak series contrast, and excessive whitespace.
- Verify the PDF is one page and contains the intended embedded font.
