# Optional molecular 3D rendering

Use the deterministic PyVista/VTK renderer for ball-and-stick molecules and
isosurfaces from supplied scalar grids. These are scientific geometry renders,
not AI-generated images. The optional dependencies are separate from Matplotlib.

## Install and run

From the repository root, in a Python 3.10+ environment:

```bash
python -m pip install -r requirements-3d.txt
python examples/generate_molecular_gallery.py --font /path/to/DIN2014-Regular.ttf
```

Omit `--font` for DejaVu Sans. Font binaries are not bundled. The demo creates
synthetic NPZ input, six transparent renders and JSON manifests, and DIN-labeled
PNG/PDF compositions in `examples/molecular-3d/`. It does not regenerate the
archived manuscript figures.

```bash
python scripts/render_molecular.py scene.npz --mode structure --output out/structure.png
python scripts/render_molecular.py scene.npz --mode total --level 0.02 \
  --camera out/structure.json --transparent --output out/total.png
python scripts/render_molecular.py scene.npz --mode error --level 0.001 \
  --camera out/structure.json --transparent --output out/error.png
```

The example contour values above are placeholders in the supplied density units,
not universal physical recommendations. Choose them from the scientific question
and field range, and fix them across comparisons. No surface is an error unless
`--allow-empty` explicitly requests a documented empty result.

## Input contract

Use `numpy.savez_compressed` with numeric arrays and scalar strings; object arrays
and pickle are not accepted. All coordinates share one Cartesian frame.

| Key | Shape / values | Meaning |
|---|---|---|
| `positions` | `(N, 3)`, finite | Atom coordinates |
| `atomic_numbers` | `(N,)`, integers 1–118 | Chemical elements |
| `length_unit` | scalar `angstrom` or `bohr` | Unit of positions, origin, spacing |
| `bonds` | optional integer `(M, 2)` | Zero-based atom pairs; empty `(0, 2)` disables bonds |
| `origin` | `(3,)` | Position of field sample `[0,0,0]` |
| `spacing` | positive `(3,)` | Axis-aligned x/y/z grid increments |
| `density_unit` | `e/bohr^3`, `e/angstrom^3`, or `arbitrary` | Unit of every scalar field and contour level |
| Scalar fields | identical finite `(nx, ny, nz)`, each dimension ≥2 | Point samples in x/y/z axis order |

Structure-only inputs need the first three keys; bonds are optional. Scalar grids
also require origin, spacing and density_unit. Sample `[i,j,k]` is located at
`origin + spacing * [i,j,k]`. The renderer uses Fortran flattening when assigning
NumPy xyz samples to VTK point data; do not pre-transpose the input array.

| Mode | Required fields | Definition |
|---|---|---|
| `structure` | none | Atoms and bonds only |
| `total` | `density`, or both `alpha` and `beta` | density, or alpha + beta |
| `alpha` / `beta` | corresponding field | Nonnegative spin-channel density |
| `spin` | `alpha`, `beta` | alpha − beta |
| `error` | `prediction_density`, `reference_density` | prediction − reference |
| `signed` | `signed_density` | Supplied signed scalar field |

All fields except `signed_density` must be nonnegative. If density, alpha and beta
are all provided, density must agree with their sum. Predictions/references must
already be aligned on the same grid. This renderer does not evaluate a density
matrix in an AO basis, run quantum chemistry, interpolate mismatched grids, parse
cube files, handle periodic cells, or support skewed grids. Prepare those inputs
with the research project's scientific pipeline; never invent missing fields.

Bohr coordinates are converted to angstrom for geometry only. Density numbers
and their units are retained unchanged: changing coordinate units must not silently
change the threshold. Any physical density-unit conversion belongs in input
preparation and must be applied to both values and thresholds consistently.

If bonds are absent, a simple distance rule uses 1.15 times the sum of ASE covalent
radii (and distance >0.1 Å). It does not infer bond order or aromaticity. Supply
explicit bonds for ambiguous structures. Atom sizes are illustrative, not
space-filling van der Waals radii.

## Style controls

- Smooth ball-and-stick geometry; carbon charcoal, oxygen dark red, nitrogen
  dark blue, hydrogen muted gray, and bonds colored by their endpoint elements.
- Total density uses a neutral shell; alpha amber, beta blue. Signed fields have
  red positive and blue negative surfaces at exactly `+level` and `-level`.
  Add sign labels in the final composition.
- `--opacity` defaults to 0.28. Keep it fixed across corresponding panels; the
  synthetic demo uses 0.38 for ordinary shells and 0.52 for signed shells.
- `--smoothing` defaults to zero. A nonzero Gaussian sigma is in voxels and changes
  only the displayed field. Disclose it; compute reported metrics from raw input.
- `--transparent` outputs RGBA; otherwise the background is white. Supersampling
  defaults to 2, with premultiplied-alpha Lanczos reduction to avoid edge halos.
- `--width` and `--height` are final pixels. Increase these for print; resolution
  limits prevent excessive framebuffer allocation. Raw 3D output is PNG only.

## Camera and comparison consistency

The default orthographic camera conservatively fits the entire input grid and
geometry. Empty grid margins may produce excess whitespace. Save one camera
and adjust its `camera.parallel_scale` (half the vertical span in angstrom) and
`focal_point` together with `position` for a tighter shared framing. Keep every
surface in view. Pass that same JSON through `--camera` to all comparison panels;
the image aspect ratio must match. `examples/generate_molecular_gallery.py`
provides a known, fixed camera for its synthetic scene.

Do not independently fit or crop each method. The source NPZ SHA-256, field
definition, camera, threshold, units, opacity, smoothing, bonds, engine versions,
transparency backend, and output SHA-256 are recorded in the companion JSON.
Missing positive/negative surfaces and intersections with the grid boundary are
reported separately. A boundary intersection may indicate an incomplete shell;
extend the input grid rather than hiding the cut.

## Validation and delivery

1. Verify coordinates and grid registration, units, field definitions and signs.
2. Render structure plus requested fields. Check that both signed contours exist
   when expected and that shells do not intersect the grid boundary.
3. Compare camera JSON across panels, and inspect actual output at final size.
4. Inspect transparent images on both white and black backgrounds; check atom
   edges, surface overlap, clipping, sign-color visibility and empty margins.
5. Compose labels and legends in Matplotlib using DIN where available. The demo
   writes PNG/PDF compositions; PDF labels are vector text but the 3D panels are
   embedded raster images. Increase render resolution when enlarging them.
6. Deliver input-preparation code, renderer command, PNG and JSON, plus the
   composition script/PDF when requested. Include scientific provenance separately
   from renderer metadata.

Tests of grid orientation, units, sign arithmetic, camera reuse and transparent
resizing are in `tests/test_molecular.py` (`python -m pytest tests/test_molecular.py`).
They require the optional dependencies and pytest. They do not replace inspection
of the actual research figure.

## Rendering environment

PyVista 0.46 and VTK 9.5 are the supported version families. Offscreen rendering
still requires a working OpenGL backend. See the [PyVista installation guide](https://docs.pyvista.org/getting-started/installation.html)
for EGL/OSMesa and platform-specific setup. A headless environment may need system
OpenGL libraries; a Python requirements file cannot bundle system graphics drivers.
The release was tested with both offscreen X and a display-free EGL backend
(`VTK_DEFAULT_OPENGL_WINDOW=vtkEGLRenderWindow` with `DISPLAY` unset). This does
not establish compatibility with every driver or platform. The companion manifest records the backend and whether depth peeling was actually
used, because translucent surfaces can differ between environments.

Implementation references: [ImageData grids](https://tutorial.pyvista.org/tutorial/02_mesh/solutions/c_create-uniform-grid.html),
[depth peeling](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.renderer.enable_depth_peeling),
and [transparent screenshots](https://docs.pyvista.org/api/plotting/_autosummary/pyvista.plotter.screenshot).
