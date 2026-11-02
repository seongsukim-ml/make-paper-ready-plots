#!/usr/bin/env python3
"""Optional deterministic molecular/isosurface renderer. See references/rendering-3d.md."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import warnings

import numpy as np
from PIL import Image

BOHR_TO_ANGSTROM = 0.529177210903
COLORS = {1: '#B8C0C8', 6: '#242A30', 7: '#1252A0', 8: '#C0263A', 9: '#3EA64A'}
POSITIVE, NEGATIVE, TOTAL = '#D85140', '#5384EC', '#9CADB7'
FIELDS = ('density', 'alpha', 'beta', 'reference_density', 'prediction_density', 'signed_density')


def load_scene(path: Path) -> dict:
    """NPZ arrays use xyz axis order, point samples, and explicit coordinate units."""
    with np.load(path, allow_pickle=False) as archive:
        data = {key: archive[key] for key in archive.files}
    for key in ('positions', 'atomic_numbers', 'length_unit'):
        if key not in data:
            raise ValueError(f'Missing {key}')
    unit = str(np.asarray(data['length_unit']).item())
    if unit not in ('angstrom', 'bohr'):
        raise ValueError('length_unit must be angstrom or bohr')
    factor = BOHR_TO_ANGSTROM if unit == 'bohr' else 1.0
    positions = np.asarray(data['positions'], dtype=float)
    numbers = np.asarray(data['atomic_numbers'])
    if positions.ndim != 2 or positions.shape[1] != 3 or len(positions) == 0:
        raise ValueError('positions must have shape (N, 3), N > 0')
    if not np.isfinite(positions).all():
        raise ValueError('Non-finite atom coordinates')
    if numbers.shape != (len(positions),) or not np.issubdtype(numbers.dtype, np.integer):
        raise ValueError('atomic_numbers must be an integer vector of length N')
    if np.any((numbers < 1) | (numbers > 118)):
        raise ValueError('Atomic numbers must be in 1..118')
    result = {'positions': positions * factor, 'atomic_numbers': numbers,
              'input_length_unit': unit, 'fields': {}, 'density_unit': None}
    if 'bonds' in data:
        bonds = np.asarray(data['bonds'])
        if bonds.ndim != 2 or bonds.shape[1] != 2 or not np.issubdtype(bonds.dtype, np.integer):
            raise ValueError('bonds must be an integer (M, 2) array, including empty (0, 2)')
        if np.any(bonds < 0) or np.any(bonds >= len(positions)) or np.any(bonds[:, 0] == bonds[:, 1]):
            raise ValueError('Invalid bond indices or self-bonds')
        bonds = np.sort(bonds, axis=1)
        if len(np.unique(bonds, axis=0)) != len(bonds):
            raise ValueError('Duplicate bonds')
        result['bonds'] = bonds
    fields = {key: np.asarray(data[key], dtype=float) for key in FIELDS if key in data}
    if fields:
        for key in ('origin', 'spacing', 'density_unit'):
            if key not in data:
                raise ValueError(f'Fields require {key}')
        origin = np.asarray(data['origin'], dtype=float)
        spacing = np.asarray(data['spacing'], dtype=float)
        if origin.shape != (3,) or spacing.shape != (3,) or not np.isfinite(origin).all() or not np.isfinite(spacing).all() or np.any(spacing <= 0):
            raise ValueError('origin/spacing must be finite length-3 vectors; spacing > 0')
        shapes = {f.shape for f in fields.values()}
        if len(shapes) != 1 or any(f.ndim != 3 or min(f.shape) < 2 or not np.isfinite(f).all() for f in fields.values()):
            raise ValueError('Fields must be finite 3D arrays on one identical grid, all dimensions >= 2')
        for key, field in fields.items():
            if key != 'signed_density' and np.min(field) < 0:
                raise ValueError(f'{key} must be nonnegative; use signed_density for signed fields')
        density_unit = str(np.asarray(data['density_unit']).item())
        if density_unit not in ('e/bohr^3', 'e/angstrom^3', 'arbitrary'):
            raise ValueError('density_unit must be e/bohr^3, e/angstrom^3, or arbitrary')
        if all(k in fields for k in ('density', 'alpha', 'beta')):
            if not np.allclose(fields['density'], fields['alpha'] + fields['beta'], rtol=1e-6, atol=1e-12):
                raise ValueError('density does not match alpha + beta')
        result.update(origin=origin * factor, spacing=spacing * factor,
                      fields=fields, density_unit=density_unit)
    return result


def select_field(scene: dict, mode: str):
    fields = scene['fields']
    if mode == 'structure':
        return None, False, 'structure only'
    if mode == 'total':
        if 'density' in fields:
            return fields['density'], False, 'density'
        return fields['alpha'] + fields['beta'], False, 'alpha + beta'
    if mode == 'spin':
        return fields['alpha'] - fields['beta'], True, 'alpha - beta'
    if mode == 'error':
        return fields['prediction_density'] - fields['reference_density'], True, 'prediction_density - reference_density'
    if mode == 'signed':
        return fields['signed_density'], True, 'signed_density'
    return fields[mode], False, mode


def infer_bonds(scene: dict) -> np.ndarray:
    from ase.data import covalent_radii
    xyz, z = scene['positions'], scene['atomic_numbers']
    result = []
    for i in range(len(xyz)):
        for j in range(i + 1, len(xyz)):
            distance = np.linalg.norm(xyz[j] - xyz[i])
            if .1 < distance <= 1.15 * (covalent_radii[z[i]] + covalent_radii[z[j]]):
                result.append((i, j))
    return np.asarray(result, dtype=int).reshape(-1, 2)


def make_grid(scene, field):
    import pyvista as pv
    grid = pv.ImageData(dimensions=field.shape, spacing=scene['spacing'], origin=scene['origin'])
    grid.point_data['density'] = field.ravel(order='F')
    return grid


def default_camera(scene, width, height):
    xyz = scene['positions']
    low, high = xyz.min(axis=0) - .6, xyz.max(axis=0) + .6
    if scene['fields']:
        shape = next(iter(scene['fields'].values())).shape
        low = np.minimum(low, scene['origin'])
        high = np.maximum(high, scene['origin'] + scene['spacing'] * (np.array(shape) - 1))
    center = (low + high) / 2
    radius = max(float(np.linalg.norm(high - low) / 2), .5)
    az, el = np.deg2rad([-56., 24.])
    direction = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    return {'position': (center + 4 * radius * direction).tolist(), 'focal_point': center.tolist(),
            'view_up': [0., 0., 1.], 'parallel_scale': radius * 1.08 * max(1., height / width),
            'projection': 'parallel', 'aspect_ratio': width / height}


def validate_camera(camera, width, height):
    for key in ('position', 'focal_point', 'view_up'):
        value = np.asarray(camera[key], dtype=float)
        if value.shape != (3,) or not np.isfinite(value).all():
            raise ValueError(f'Invalid camera {key}')
    direction = np.asarray(camera['focal_point']) - np.asarray(camera['position'])
    if np.linalg.norm(np.cross(direction, camera['view_up'])) < 1e-10:
        raise ValueError('Camera direction/view_up are degenerate')
    if camera['projection'] != 'parallel' or not np.isfinite(camera['parallel_scale']) or camera['parallel_scale'] <= 0:
        raise ValueError('Camera must have positive orthographic parallel_scale')
    if not np.isclose(camera['aspect_ratio'], width / height):
        raise ValueError('Reused camera requires the same image aspect ratio')


def reduce_rgba(array, size):
    """Resize in premultiplied alpha; do not bake a white matte into edges."""
    x = np.asarray(array, dtype=np.float32) / 255
    if x.shape[-1] == 3:
        x = np.dstack([x, np.ones(x.shape[:2])])
    alpha = x[..., 3]
    channels = [x[..., k] * alpha for k in range(3)] + [alpha]
    resized = np.stack([np.asarray(Image.fromarray(c, mode='F').resize(size, Image.Resampling.LANCZOS)) for c in channels], axis=-1)
    a = np.clip(resized[..., 3], 0, 1)
    rgb = np.divide(np.clip(resized[..., :3], 0, a[..., None]), a[..., None],
                    out=np.zeros_like(resized[..., :3]), where=a[..., None] > 1e-7)
    result = np.round(np.dstack([rgb, a]) * 255).astype(np.uint8)
    result[result[..., 3] == 0, :3] = 0
    return Image.fromarray(result, 'RGBA')


def render(args):
    import pyvista as pv
    from ase.data import covalent_radii
    from ase.data.colors import jmol_colors
    from scipy.ndimage import gaussian_filter
    scene = load_scene(args.input)
    try:
        field, signed, definition = select_field(scene, args.mode)
    except KeyError as exc:
        raise ValueError(f'Mode {args.mode} requires missing field: {exc}') from exc
    if field is not None and args.level is None:
        raise ValueError('Specify --level in the input density_unit; levels are never inferred')
    if args.level is not None and (not np.isfinite(args.level) or args.level <= 0):
        raise ValueError('--level must be finite and positive')
    if not 0 < args.opacity <= 1 or not np.isfinite(args.smoothing) or args.smoothing < 0:
        raise ValueError('Require 0 < opacity <= 1 and finite smoothing >= 0')
    if not (128 <= args.width <= 4096 and 128 <= args.height <= 4096 and 1 <= args.supersample <= 4):
        raise ValueError('Image dimensions must be 128..4096 and supersample 1..4')
    if args.width * args.height * args.supersample**2 > 40_000_000:
        raise ValueError('Supersampled image exceeds 40 megapixels')
    camera = default_camera(scene, args.width, args.height)
    if args.camera:
        camera = json.loads(args.camera.read_text())['camera']
    validate_camera(camera, args.width, args.height)
    inferred = 'bonds' not in scene
    bonds = infer_bonds(scene) if inferred else scene['bonds']
    plotter = pv.Plotter(off_screen=True, window_size=(args.width*args.supersample, args.height*args.supersample), lighting='three lights')
    plotter.set_background('white')
    plotter.render_window.SetMultiSamples(0)
    peeling_supported = plotter.enable_depth_peeling(number_of_peels=100, occlusion_ratio=0.0)
    records = []
    try:
        xyz, z = scene['positions'], scene['atomic_numbers']
        def color(number):
            return COLORS.get(int(number), jmol_colors[int(number)].tolist() if int(number) < len(jmol_colors) else '#318C7A')
        material = dict(smooth_shading=True, ambient=.25, diffuse=.70, specular=.12, specular_power=18, show_scalar_bar=False)
        for number, point in zip(z, xyz):
            radius = float(np.clip(.44 * covalent_radii[number], .20, .48))
            plotter.add_mesh(pv.Sphere(radius=radius, center=point, theta_resolution=48, phi_resolution=32), color=color(number), **material)
        for i, j in bonds:
            if np.linalg.norm(xyz[i] - xyz[j]) < 1e-8:
                raise ValueError('A bond has coincident endpoints')
            middle = (xyz[i] + xyz[j]) / 2
            for point, number in [(xyz[i], z[i]), (xyz[j], z[j])]:
                segment = middle - point
                plotter.add_mesh(pv.Cylinder(center=(point+middle)/2, direction=segment, radius=.09, height=float(np.linalg.norm(segment)), resolution=24), color=color(number), **material)
        if field is not None:
            displayed = gaussian_filter(field, args.smoothing) if args.smoothing else field
            grid = make_grid(scene, displayed)
            levels = [args.level, -args.level] if signed else [args.level]
            boundary = np.concatenate([displayed[0].ravel(), displayed[-1].ravel(), displayed[:, 0].ravel(), displayed[:, -1].ravel(), displayed[:, :, 0].ravel(), displayed[:, :, -1].ravel()])
            for level in levels:
                mesh = grid.contour([level], scalars='density', method='marching_cubes')
                present = mesh.n_points > 0
                clipped = bool(np.any(boundary >= level) if level > 0 else np.any(boundary <= level))
                records.append({'level': level, 'present': present, 'points': mesh.n_points, 'cells': mesh.n_cells, 'intersects_grid_boundary': clipped})
                if present:
                    mesh = mesh.compute_normals(split_vertices=False, consistent_normals=True)
                    tint = (POSITIVE if level > 0 else NEGATIVE) if signed else {'alpha': '#E5A23B', 'beta': NEGATIVE}.get(args.mode, TOTAL)
                    plotter.add_mesh(mesh, color=tint, opacity=args.opacity, culling='back', **material)
                    if clipped:
                        warnings.warn(f'Isosurface {level:g} reaches the grid boundary; supply a larger grid for a closed shell')
                else:
                    warnings.warn(f'No surface at level {level:g}; no threshold adjustment made')
            if not any(r['present'] for r in records) and not args.allow_empty:
                raise ValueError('No requested isosurface exists. Use --allow-empty only to document this explicitly.')
        plotter.camera_position = [camera['position'], camera['focal_point'], camera['view_up']]
        plotter.enable_parallel_projection()
        plotter.camera.parallel_scale = camera['parallel_scale']
        plotter.reset_camera_clipping_range()
        image = plotter.screenshot(transparent_background=args.transparent, return_img=True)
        peeling_used = bool(plotter.renderer.GetLastRenderingUsedDepthPeeling())
        backend = plotter.render_window.GetClassName()
        final = reduce_rgba(image, (args.width, args.height))
        if not args.transparent:
            white = Image.new('RGBA', final.size, 'white')
            white.alpha_composite(final)
            final = white.convert('RGB')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        final.save(args.output)
        manifest = {'source_file': args.input.name, 'source_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
                    'mode': args.mode, 'field_definition': definition, 'input_length_unit': scene['input_length_unit'],
                    'render_length_unit': 'angstrom', 'density_unit': scene['density_unit'], 'camera': camera,
                    'atom_count': len(z), 'bonds': bonds.tolist(), 'bonds_inferred': inferred,
                    'bond_rule': '1.15 * sum(ASE covalent radii), distance > 0.1 angstrom' if inferred else 'supplied',
                    'smoothing_sigma_voxels': args.smoothing, 'opacity': args.opacity, 'surfaces': records,
                    'field_range': [float(field.min()), float(field.max())] if field is not None else None,
                    'signed_colors': {'positive': POSITIVE, 'negative': NEGATIVE},
                    'transparent': args.transparent, 'supersample': args.supersample, 'size': [args.width, args.height],
                    'alpha_resize': 'premultiplied Lanczos; zero RGB where alpha is zero',
                    'depth_peeling_supported': bool(peeling_supported), 'depth_peeling_used': peeling_used,
                    'backend': backend, 'pyvista': pv.__version__, 'vtk': str(pv.vtk_version_info),
                    'output_sha256': hashlib.sha256(args.output.read_bytes()).hexdigest()}
        args.output.with_suffix('.json').write_text(json.dumps(manifest, indent=2) + '\n')
        print(f'{args.output}: {args.width}x{args.height}; {len(records)} requested surfaces; {backend}')
    finally:
        plotter.close()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--output', type=Path, required=True, help='PNG output; companion JSON is automatic')
    p.add_argument('--mode', choices=['structure', 'total', 'alpha', 'beta', 'spin', 'error', 'signed'], default='structure')
    p.add_argument('--level', type=float)
    p.add_argument('--opacity', type=float, default=.28)
    p.add_argument('--smoothing', type=float, default=0, help='Display-only Gaussian sigma in voxels')
    p.add_argument('--camera', type=Path, help='Reuse camera from a prior renderer JSON manifest')
    p.add_argument('--transparent', action='store_true')
    p.add_argument('--allow-empty', action='store_true')
    p.add_argument('--width', type=int, default=900)
    p.add_argument('--height', type=int, default=650)
    p.add_argument('--supersample', type=int, default=2)
    args = p.parse_args()
    if args.output.suffix.lower() != '.png':
        p.error('--output must end in .png')
    render(args)


if __name__ == '__main__':
    main()
