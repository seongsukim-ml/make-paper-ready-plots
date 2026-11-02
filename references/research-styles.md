# Research figure styles

Use these recipes to adapt supplied data to the research gallery's visual language.
The archived figures preserve their original typography. New figures should use
licensed DIN 2014 when supplied, with Computer Modern math; otherwise DejaVu Sans.
The public package includes styling recipes and a new molecular renderer, not the
original private manuscript plotting pipeline or experimental data.

## Choose a recipe

| Requested figure | Recipe and starting point |
|---|---|
| Model/data scaling, Hamiltonian/orbital/force/energy errors | [DIN Boxed](din-boxed.md), `assets/matplotlib-din-boxed.py`; QHFlow2 gallery for layout |
| Occupation spectrum and spectral deviation | Occupation recipe below; Matplotlib `GridSpec` and shared axes |
| OV-weight or architecture ablation | Ablation recipe below; `examples/generate_gallery.py` for axis/legend conventions |
| Molecular geometry, total/spin density, signed prediction error | [3D workflow](rendering-3d.md), `scripts/render_molecular.py` |
| Multiple molecules/methods or inverted geometry | Molecular comparison recipe below, followed by Matplotlib composition |

## Occupation spectrum

- Order eigenvalues according to the stated scientific convention and label the
  orbital/eigenvalue index. Preserve the supplied occupancy convention (0–1 or
  0–2); do not silently rescale it.
- Use a shared x-axis for occupation and deviation panels. Define the deviation
  explicitly, such as prediction minus reference or its absolute value.
- Where values cluster near opposite ends of the physical interval, an optional
  broken y-axis may separate them. Implement two axes with shared x coordinates,
  draw diagonal break marks, disclose the omitted interval, and retain readable
  ticks on both portions. Never make a disconnected interval look continuous.
- Show the reference unobtrusively and keep raw/corrected methods in consistent
  colors, markers, and line styles. Lines through sorted spectra are appropriate;
  do not connect independently unordered configurations.
- Use a log deviation axis only for strictly positive magnitudes. Show zeros
  explicitly or choose a linear/symlog representation with a stated threshold;
  do not add an arbitrary epsilon to make data log-compatible.

## Weight sweep / ablation

- Use two aligned panels for quantities with different units (for example density
  error and energy error). Avoid a double y-axis by default.
- Keep true weight coordinates if the x-axis represents numeric distance. If
  weights are categorical settings, use equal spacing and label the axis as
  configurations. Do not imply linear spacing for irregular numeric settings.
- Put a baseline at its measured value. For relative errors, disclose the exact
  denominator and handle a zero baseline explicitly.
- Keep panel sizes and legend order identical; use a single compact shared legend
  when panels remain together, or matching legends if they may be separated.
- Use zero-based bars. For line/point plots, choose limits that preserve differences
  without hiding important observations. Add uncertainty only when supplied.

## Molecular comparisons

- Use rows for molecules and columns for reference/prediction/error or methods.
  Put column headings once above the grid and molecule identifiers at the left.
- Within a molecule, reuse the same geometry, camera, orthographic scale, image
  aspect ratio, lighting, atom sizes, density units, opacity, and contour levels.
  Keep the same error levels across methods; do not normalize each field by its
  own maximum. If levels differ between molecule rows, label them per row.
- Use a quiet neutral total-density shell. For signed fields use red for positive,
  blue for negative, and a visible sign legend: error = prediction − reference;
  spin = alpha − beta. Numeric error metrics belong in text or adjacent plots,
  not inferred from the visible surface area.
- For inversion tests, state whether the transform applies to coordinates, the
  field, or both. Preserve atom correspondence and grid registration. A camera
  rotation alone is not a molecular inversion. Prepare transformed inputs before
  invoking this renderer; it does not infer transformations.
- Render all panels with one saved camera and compose them without per-panel
  automatic cropping. Inspect the union of all visible surfaces to set the
  common framing; avoid clipping lobes just to fill the panel.
- Use short titles and generous inter-panel space. Keep rendered molecules large
  enough to read at final paper size. Export a high-resolution PNG and a PDF
  composition; the molecular panels in that PDF remain raster images.

For a runnable example, see `examples/generate_molecular_gallery.py`. It uses a
small synthetic methanol-like geometry and analytic Gaussian fields, not DFT
calculations or research predictions. The original manuscript gallery is a
composition reference, not a claim of exact regeneration by this demo.
