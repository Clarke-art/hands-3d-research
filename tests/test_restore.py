import unittest, pathlib,sys,importlib.util
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from midi_inspect import inspect
class RestorationTests(unittest.TestCase):
    def test_original_midi(self):
        files=list((ROOT/'examples').rglob('*.mid'))
        self.assertTrue(files)
        for p in files:
            result=inspect(p);self.assertGreater(result['note_on'],0);self.assertGreater(result['tracks'],0)
    def test_invalid_midi_rejected(self):
        with self.assertRaises(ValueError):inspect(ROOT/'README.md')
    def test_legacy_geometry_known_separation(self):
        try: import numpy as np
        except ImportError: self.skipTest("Install requirements-geometry.txt for optional numeric smoke")
        p=ROOT/'src/legacy/experiments/hands_long_context_corridor_ik_bridge_r2/triangle_distance.py'
        s=importlib.util.spec_from_file_location('triangle_distance',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
        a=np.array([[[0.,0.,0.],[1.,0.,0.],[0.,1.,0.]]]);b=a+np.array([0,0,2.])
        d,_,_=m.distances(a,b);np.testing.assert_allclose(d,[2.])
if __name__=='__main__':unittest.main()
