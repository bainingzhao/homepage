import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('update_scholar', Path(__file__).parents[1]/'scripts/update_scholar.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CitationDataTests(unittest.TestCase):
    def test_bad_refresh_preserves_last_success(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)/'gs_data.json'
            good = dict(scholar_id='test', citedby=12, updated='2026-09-15T00:00:00+00:00')
            module.save(good, p, 'test')
            for bad in [None, -1, True, '12']:
                with self.assertRaises(ValueError):
                    module.save(dict(good, citedby=bad), p, 'test')
                self.assertEqual(json.loads(p.read_text()), good)
            with self.assertRaises(ValueError):
                module.save(dict(good, scholar_id='someone-else'), p, 'test')
            self.assertEqual(json.loads(p.read_text()), good)

    def test_verified_zero_is_valid(self):
        data = dict(scholar_id='test', citedby=0, updated='2026-09-15T00:00:00+00:00')
        self.assertEqual(module.validate(data, 'test')['citedby'], 0)

if __name__ == '__main__':
    unittest.main()
