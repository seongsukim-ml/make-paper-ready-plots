# Make Paper-Ready Plots

A reusable AI-agent skill for clean, reproducible **Matplotlib figures for
scientific papers**. Includes style guides, runnable templates, PDF/PNG export,
and a small output validator.

**논문용 그래프 제작 스킬입니다.** 실험 결과 비교, parameter scaling, ablation,
작은 패널 여러 개를 일관된 스타일로 만들 수 있습니다. 아래 그림은 모두 합성
데이터로 만든 예시입니다. **DIN 2014 폰트를 권장하며 아래 샘플도 DIN 2014로
제작했습니다.** 폰트 파일 자체는 포함하지 않습니다.

## Gallery

Every example below uses **synthetic demonstration data**, not experimental
results. Public previews use **DIN 2014 (recommended)**, supplied locally.
Without a font path, the scripts use DejaVu Sans. The scripts reproduce the data,
layout, and styling; binary output can vary with dependency versions.

### Small multiples

Aligned log–log comparisons, explicit numeric ticks, quiet horizontal grids,
and consistent per-panel legends.

![Three-panel synthetic comparison](examples/gallery/small-multiples.png)

[PDF](examples/gallery/small-multiples.pdf) · [Template](assets/matplotlib-small-multiples.py)

### Compact boxed

The recommended DIN 2014 typography with thin boxed axes, outward ticks, filled
markers, and a compact horizontal legend. Supply your own licensed DIN font
to match the gallery; DejaVu Sans is available as a fallback.

<img src="examples/gallery/compact-boxed.png" alt="Compact boxed synthetic comparison using DIN 2014" width="440">

[PDF](examples/gallery/compact-boxed.pdf) · [Template](assets/matplotlib-din-boxed.py)

### Architecture ablation

Zero-based bars with direct value labels and a hatch to distinguish the full
model independently of color. Values are illustrative, with no claimed
statistical uncertainty.

<img src="examples/gallery/ablation.png" alt="Synthetic architecture ablation" width="600">

[PDF](examples/gallery/ablation.pdf) · [Source](examples/generate_gallery.py)

### Descriptive scaling fit

An optional power-law fit on exactly four synthetic observations. The open
marker is excluded from fitting. This example demonstrates presentation and
fit selection, not evidence for a real scaling law.

<img src="examples/gallery/scaling-fit.png" alt="Synthetic scaling fit with an excluded comparison point" width="600">

[PDF](examples/gallery/scaling-fit.pdf) · [Source](examples/generate_gallery.py)

## Use the skill

Clone the repository and ask your coding agent to read
[`SKILL.md`](SKILL.md). The instructions and supporting assets are self-contained.

```bash
git clone https://github.com/seongsukim-ml/make-paper-ready-plots.git
```

Example prompt:

> Follow make-paper-ready-plots/SKILL.md. Plot the MAE results from results.csv
> as three comparable panels with shared scales. Preserve the supplied values,
> use the default style, and deliver the Python script, PDF, and PNG.

For a compact plot:

> Follow make-paper-ready-plots/SKILL.md and references/din-boxed.md. Use the
> compact boxed profile with my licensed DIN 2014 font. Keep the legend above the axes.
> Export a PDF and a 600-dpi PNG and inspect the rendered output.

For personal Codex skill discovery, clone directly into an unused skill folder:

```bash
git clone https://github.com/seongsukim-ml/make-paper-ready-plots.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/make-paper-ready-plots"
```

If that directory already exists, use a separate checkout and compare it with
your existing skill before replacing anything. Once your agent discovers the
skill, refer to it as `$make-paper-ready-plots`.

## Run the examples

Python 3.10 or later is required. No LaTeX installation or image-generation API
is needed.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python examples/generate_gallery.py
```

The command above uses the DejaVu Sans fallback. To match the committed DIN
2014 gallery, regenerate with your own licensed fonts:

```bash
python examples/generate_gallery.py \
  --font /path/to/DIN2014-Regular.ttf --bold-font /path/to/DIN2014-Bold.ttf
```

The generator creates all four PNG/PDF pairs and validates their image dimensions,
PDF signature, page count, and expected font name. The validator is a basic
file check, not a substitute for inspecting layout at the intended paper size.

Run a template separately:

```bash
python assets/matplotlib-small-multiples.py --output-stem output/comparison
python assets/matplotlib-din-boxed.py --output-stem output/compact
python scripts/validate_static_plot.py output/compact.png output/compact.pdf
```

**Recommended font: DIN 2014.** It gives these compact plots the narrow, clean
letterforms shown in the gallery. Font files are not bundled; provide your own
licensed copies. For an individual figure:

```bash
python assets/matplotlib-din-boxed.py --output-stem output/compact-din \
  --font /path/to/DIN2014-Regular.ttf --bold-font /path/to/DIN2014-Bold.ttf
```

## Design choices

- Two profiles: a default small-multiples style and a compact DIN Boxed layout.
- Thin boxed axes, restrained typography, and dotted horizontal grids.
- Marker and line-style distinctions alongside color.
- Real numeric coordinates and preserved input precision.
- Optional power-law fitting only when requested; fitted points are explicit.
- Editable source scripts plus vector PDF and raster PNG outputs.

## Files

| Path | Purpose |
|---|---|
| [SKILL.md](SKILL.md) | Agent entry point and workflow |
| [references/style-guide.md](references/style-guide.md) | Default plotting style |
| [references/din-boxed.md](references/din-boxed.md) | Compact boxed profile and font handling |
| [references/power-law.md](references/power-law.md) | Optional descriptive scaling fits |
| `assets/` | Two standalone Matplotlib templates |
| `examples/` | Gallery generator and committed PNG/PDF examples |
| `scripts/validate_static_plot.py` | Basic PNG/PDF checks |

## License

[MIT](LICENSE) for the original skill, code, and synthetic examples. See
[third-party notices](THIRD_PARTY_NOTICES.md) for fonts and dependencies.
