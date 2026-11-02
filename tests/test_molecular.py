"""Scientific coordinate and transparency invariants; rendering is checked by the demo."""
import importlib.util
from pathlib import Path
import numpy as np
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/render_molecular.py'
spec = importlib.util.spec_from_file_location('render_molecular', SCRIPT)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def save(tmp_path, **changes):
    data = dict(positions=np.array([[0.,0.,0.],[1.,0.,0.]]), atomic_numbers=np.array([1,1]),
                length_unit='angstrom', origin=np.array([0.,0.,0.]), spacing=np.array([.2,.3,.4]),
                density_unit='e/bohr^3', alpha=np.ones((3,4,5))*.6, beta=np.ones((3,4,5))*.4)
    data.update(changes)
    path = tmp_path/'scene.npz'
    np.savez(path, **data)
    return path


def test_bohr_conversion_preserves_density_units_and_values(tmp_path):
    scene = r.load_scene(save(tmp_path, length_unit='bohr'))
    np.testing.assert_allclose(scene['positions'][1], [r.BOHR_TO_ANGSTROM,0,0])
    np.testing.assert_allclose(scene['spacing'],np.array([.2,.3,.4])*r.BOHR_TO_ANGSTROM)
    assert scene['density_unit']=='e/bohr^3'
    np.testing.assert_array_equal(scene['fields']['alpha'],np.ones((3,4,5))*.6)


def test_channels_and_error_sign(tmp_path):
    scene=r.load_scene(save(tmp_path, reference_density=np.ones((3,4,5))*.9,
                           prediction_density=np.ones((3,4,5))*.8))
    np.testing.assert_allclose(r.select_field(scene,'total')[0],1.)
    np.testing.assert_allclose(r.select_field(scene,'spin')[0],.2)
    np.testing.assert_allclose(r.select_field(scene,'error')[0],-.1)


@pytest.mark.parametrize('changes',[
    {'length_unit':'nm'}, {'spacing':np.array([.1,-.2,.3])},
    {'beta':np.ones((3,4,6))}, {'alpha':np.full((3,4,5),np.nan)},
    {'density':np.ones((3,4,5))*9}, {'bonds':np.array([[0,0]])},
    {'atomic_numbers':np.array([1.,1.])}, {'alpha':-np.ones((3,4,5))},
])
def test_invalid_inputs_fail_before_rendering(tmp_path,changes):
    with pytest.raises(ValueError):
        r.load_scene(save(tmp_path,**changes))


def test_grid_axis_order_and_physical_contour_position(tmp_path):
    scene=r.load_scene(save(tmp_path))
    scene['origin']=np.array([10.,20.,30.])
    scene['spacing']=np.array([.3,.4,.5])
    field=np.indices((5,6,7))[0].astype(float)
    grid=r.make_grid(scene,field)
    surface=grid.contour([1.5],scalars='density',method='marching_cubes')
    assert surface.n_points>0
    np.testing.assert_allclose(surface.bounds,[10.45,10.45,20.,22.,30.,33.],atol=1e-5)


def test_camera_uses_fixed_grid_not_surface_amplitude(tmp_path):
    scene=r.load_scene(save(tmp_path))
    first=r.default_camera(scene,900,650)
    scene['fields']['alpha'] *= 100
    assert first==r.default_camera(scene,900,650)
    r.validate_camera(first,900,650)
    with pytest.raises(ValueError):
        r.validate_camera(first,650,900)


def test_premultiplied_resize_does_not_leak_hidden_matte():
    data=np.zeros((32,32,4),dtype=np.uint8)
    data[:,:,:3]=[0,255,0]  # Invisible green must not bleed into red edges.
    data[8:24,8:24,:]=[255,0,0,255]
    reduced=np.array(r.reduce_rgba(data,(13,13)))
    assert np.any((reduced[:,:,3]>0)&(reduced[:,:,3]<255))
    assert np.all(reduced[:,:,1:3]==0)
    assert np.all(reduced[reduced[:,:,3]==0,:3]==0)


def test_explicit_empty_bonds_and_inferred_distance(tmp_path):
    scene=r.load_scene(save(tmp_path,positions=np.array([[0.,0.,0.],[.7,0.,0.]]),bonds=np.empty((0,2),dtype=int)))
    assert scene['bonds'].shape==(0,2)
    np.testing.assert_array_equal(r.infer_bonds(scene),[[0,1]])
    scene['positions'][1]=[10.,0.,0.]
    assert r.infer_bonds(scene).shape==(0,2)
