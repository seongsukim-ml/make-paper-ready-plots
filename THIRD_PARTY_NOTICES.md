# Third-party notices

DIN 2014 is not distributed with this repository. A private predecessor used
user-supplied DIN files; those files and any permission to redistribute them are
not part of this public release. To use DIN, supply your own licensed font paths
and verify the license permits your intended use and embedding.

The synthetic demo gallery is rendered with user-supplied DIN 2014 fonts.
Font metadata identifies ParaType as the copyright holder and has OS/2
`fsType=0` (no embedding restriction set in that field). This metadata is not a
replacement for the applicable font license. PNGs contain rendered glyphs;
PDFs contain font subsets embedded by Matplotlib. Original font files are not
included.

Without an explicit font path, scripts use DejaVu Sans from Matplotlib.
Matplotlib distributes DejaVu under its own font license in
`matplotlib/mpl-data/fonts/ttf/LICENSE_DEJAVU`.

Python dependencies retain their respective licenses. The repository's MIT
license covers its original instructions, scripts, and synthetic examples; it
does not replace third-party dependency or font licenses.

## QHFlow2 figures

`examples/qhflow2/*.png` are extracted without pixel changes from stored
notebook outputs in [seongsukim-ml/QHFlow2](https://github.com/seongsukim-ml/QHFlow2) at
commit `67af4bfe499459039cd2a9b4b3cd7ff3dbc04bd5`.
Copyright (c) 2026 Seongsu Kim. The source `REUSE.toml` assigns these files
the MIT license; the license text is included in this repository's `LICENSE`.
See `examples/qhflow2/sources.json` for per-file provenance and checksums.
These archived figures retain their original fonts and scientific labels.

## Density matrix learning manuscript figures

Selected source PDFs and their rendered PNG previews in
`examples/density-matrix/` are included at the repository owner's request.
The source repository is private and supplies no general reuse license.
These assets are excluded from the MIT license for the original skill and
synthetic examples. See `examples/density-matrix/NOTICE.md` and `sources.json`
in that directory for rights, source locations, and checksums.
