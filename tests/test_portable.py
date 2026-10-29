import unittest,pathlib,sys,json,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from midi_inspect import inspect
from fingering_demo import run
class PortableTests(unittest.TestCase):
    def test_midi_inputs(self):
        fs=list((ROOT/'examples/minimal').glob('*.mid'));self.assertEqual(len(fs),2)
        for f in fs:self.assertGreater(inspect(f)['note_on'],0)
    def test_fixed_fingering_core(self):
        r=run(ROOT/'examples/minimal/fingering_smoke.json');self.assertEqual(r['preserved_notes'],3);self.assertEqual(len(r['fingerings']),3)
    def test_core_asset_identity(self):
        import csv
        with (ROOT/'ASSET_MANIFEST.csv').open(encoding='utf-8') as f:
            for r in csv.DictReader(f):self.assertEqual(hashlib.sha256((ROOT/r['path']).read_bytes()).hexdigest(),r['sha256'])
if __name__=='__main__':unittest.main()
