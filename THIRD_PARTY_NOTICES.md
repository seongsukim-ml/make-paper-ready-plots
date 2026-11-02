# Third-party notices

DIN 2014 is not distributed with this repository. A private predecessor used
user-supplied DIN files; those files and any permission to redistribute them are
not part of this public release. To use DIN, supply your own licensed font paths
and verify the license permits your intended use and embedding.

The committed public gallery is rendered with user-supplied DIN 2014 fonts.
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
