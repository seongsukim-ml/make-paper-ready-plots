#!/usr/bin/env python3
"""Synthetic molecule/volume demo; not DFT data or model predictions."""
from pathlib import Path
import argparse
import json
import subprocess
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Patch
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def make_demo(path):
    positions = np.array([[0,0,0], [1.43,0,0], [-.36,1.02,0],
                          [-.36,-.51,.88], [-.36,-.51,-.88], [1.78,.90,0.]])
    numbers = np.array([6,8,1,1,1,1])
    origin = np.array([-2.5,-2.2,-2.0])
    spacing = np.array([.08,.08,.08])
    shape = (73,58,53)
    xyz = np.stack(np.meshgrid(*(origin[k]+spacing[k]*np.arange(shape[k]) for k in range(3)), indexing='ij'), axis=-1)
    density = np.zeros(shape)
    for z, point in zip(numbers, positions):
        sigma, weight = (.44, .8) if z > 1 else (.30, .18)
        density += weight * np.exp(-np.sum((xyz-point)**2, axis=-1)/(2*sigma**2))
    polarization = .12 * density * np.tanh(3 * xyz[...,2])
    alpha, beta = density/2+polarization, density/2-polarization
    prediction = density + .15*density*np.tanh(xyz[...,0])*np.tanh(3*xyz[...,2])
    np.savez_compressed(path, positions=positions, atomic_numbers=numbers,
                        bonds=np.array([[0,1],[0,2],[0,3],[0,4],[1,5]]),
                        origin=origin, spacing=spacing, length_unit='angstrom', density_unit='arbitrary',
                        density=density, alpha=alpha, beta=beta,
                        reference_density=density, prediction_density=prediction)


def compose(out, names, filename):
    fig, axes = plt.subplots(1, len(names), figsize=(3.2*len(names),2.7), layout='constrained')
    axes = np.atleast_1d(axes)
    for ax, (name, label) in zip(axes, names):
        ax.imshow(Image.open(out/f'{name}.png'), interpolation='bilinear')
        ax.axis('off')
        ax.set_title(label, fontsize=10, fontweight='normal')
    fig.legend(handles=[Patch(color='#D85140', label='Positive (+)'),
                        Patch(color='#5384EC', label='Negative (−)')],
               loc='outside lower center', ncol=2, frameon=False, fontsize=9)
    fig.suptitle('Synthetic geometry and Gaussian fields · arbitrary density units', fontsize=10)
    fig.savefig(out/f'{filename}.png', dpi=300, bbox_inches='tight', pad_inches=.04)
    # Molecular panels are raster images embedded in a PDF, not vector geometry.
    fig.savefig(out/f'{filename}.pdf', bbox_inches='tight', pad_inches=.04,
                metadata={'Title':'Synthetic molecular rendering example','Subject':'Raster 3D panels; not DFT results'})
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', type=Path, help='Optional licensed DIN regular font')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'examples/molecular-3d')
    args=parser.parse_args()
    if args.font:
        font_manager.fontManager.addfont(str(args.font))
        plt.rcParams['font.family'] = font_manager.FontProperties(fname=args.font).get_name()
    plt.rcParams.update({'pdf.fonttype': 42, 'mathtext.fontset': 'cm'})
    out=args.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=True)
    source=out/'synthetic-fields.npz'
    make_demo(source)
    # One hand-framed camera for every panel, including every field's outer shell.
    # The renderer default conservatively frames the entire grid; this demo has
    # a known compact molecule. Never independently zoom comparison panels.
    az, el = np.deg2rad([-56., 24.])
    center = np.array([.55, .12, 0.])
    direction = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    camera = {'position': (center+15*direction).tolist(), 'focal_point': center.tolist(),
              'view_up': [0.,0.,1.], 'parallel_scale': 1.8,
              'projection': 'parallel', 'aspect_ratio': 900/650}
    (out/'camera.json').write_text(json.dumps({'camera': camera}, indent=2)+'\n')
    definitions=[('structure',None),('alpha',.04),('beta',.04),('total',.08),('spin',.012),('error',.008)]
    for mode,level in definitions:
        cmd=[sys.executable,str(ROOT/'scripts/render_molecular.py'),str(source),
             '--mode',mode,'--output',str(out/f'{mode}.png'),'--width','900','--height','650',
             '--supersample','3','--transparent', '--camera',str(out/'camera.json'),
             '--opacity', '.52' if mode in ('spin','error') else '.38']
        if level is not None:
            cmd+=['--level',str(level)]
        subprocess.run(cmd,check=True)
    compose(out,[('structure','Structure'),('total','Total density · level 0.08'),
                 ('error','Signed error · ±0.008')],'overview')
    compose(out,[('structure','Structure'),('alpha','Alpha · 0.04'),('beta','Beta · 0.04'),
                 ('total','Total · 0.08'),('spin','Spin · ±0.012')],'channels')
    for name in ('total','error'):
        rgba=Image.open(out/f'{name}.png').convert('RGBA')
        for color in ('white','black'):
            bg=Image.new('RGBA',rgba.size,color)
            bg.alpha_composite(rgba)
            bg.convert('RGB').save(out/f'{name}-on-{color}.png')
    cameras=[json.loads((out/f'{mode}.json').read_text())['camera'] for mode,_ in definitions]
    assert all(camera==cameras[0] for camera in cameras), 'Comparison camera drift'
    (out/'typography.json').write_text(json.dumps({'font_family': plt.rcParams['font.family'], 'font_binaries_included': False}, indent=2)+'\n')
    print('Six modes rendered with an identical camera and physical scale.')


if __name__=='__main__':
    main()
