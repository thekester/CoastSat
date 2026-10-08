"""Regression tests for snow/ice masking."""

import ast
import unittest
from pathlib import Path

import numpy as np
from skimage import morphology


def load_mask_functions():
    """Load the mask functions without importing optional GDAL dependencies."""
    source_path = Path(__file__).parent / 'coastsat' / 'SDS_preprocess.py'
    tree = ast.parse(source_path.read_text(encoding='utf-8'))
    names = {'create_cloud_mask', 'create_snow_mask'}
    functions = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
    namespace = {'np': np, 'morphology': morphology}
    module = ast.Module(body=functions, type_ignores=[])
    exec(compile(module, str(source_path), 'exec'), namespace)
    return namespace


class TestSnowMask(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        functions = load_mask_functions()
        cls.create_cloud_mask = staticmethod(functions['create_cloud_mask'])
        cls.create_snow_mask = staticmethod(functions['create_snow_mask'])

    def test_landsat_qa_pixel_snow_bit_is_masked(self):
        qa = np.zeros((20, 20), dtype=np.uint16)
        qa[4, 7] = 1 << 5

        for cloud_mask_issue in (False, True):
            with self.subTest(cloud_mask_issue=cloud_mask_issue):
                mask = self.create_cloud_mask(qa, 'L8', cloud_mask_issue)
                self.assertTrue(mask[4, 7])
                self.assertEqual(mask.sum(), 1)

    def test_sentinel_scl_snow_ice_class_is_masked(self):
        qa = np.zeros((20, 20), dtype=np.uint16)
        scl = np.zeros((20, 20), dtype=np.uint8)
        scl[3, 8] = 11

        mask = self.create_snow_mask(qa, 'S2', scl)

        self.assertTrue(mask[3, 8])
        self.assertEqual(mask.sum(), 1)

    def test_legacy_sentinel_qa60_without_scl_has_no_snow_mask(self):
        qa = np.zeros((20, 20), dtype=np.uint16)

        mask = self.create_snow_mask(qa, 'S2')

        self.assertFalse(mask.any())

    def test_existing_landsat_cloud_mask_is_preserved(self):
        qa = np.zeros((20, 20), dtype=np.uint16)
        qa[4:12, 5:13] = 1 << 3

        mask = self.create_cloud_mask(qa, 'L8', False)

        self.assertTrue(mask[6, 6])
        self.assertFalse(mask[0, 0])

    def test_existing_sentinel_qa60_cloud_mask_is_preserved(self):
        qa = np.zeros((20, 20), dtype=np.uint16)
        qa[4:12, 5:13] = 1 << 10

        mask = self.create_cloud_mask(qa, 'S2', False)

        self.assertTrue(mask[6, 6])
        self.assertFalse(mask[0, 0])


if __name__ == '__main__':
    unittest.main()
