import unittest
import numpy as np
from alienlab.core import candidate_score, demo_spectrum, spectral_contrast
WINDOWS = ((3.22, 3.38), ((3.0, 3.14), (3.46, 3.6)))
class TestScientificCore(unittest.TestCase):
    def test_injected_synthetic_feature(self):
        x, y = demo_spectrum(True)
        r = spectral_contrast(x, y, *WINDOWS)
        self.assertLess(r.effect, -0.03)
        self.assertLess(r.p_value, 0.05)
        self.assertLess(r.ci_high, 0)
    def test_flat_synthetic_null(self):
        x, _ = demo_spectrum(False)
        r = spectral_contrast(x, np.ones_like(x), *WINDOWS)
        self.assertEqual(r.effect, 0)
        self.assertEqual(r.p_value, 1.0)
    def test_repeatability(self):
        x, y = demo_spectrum(True)
        self.assertEqual(spectral_contrast(x, y, *WINDOWS),
                         spectral_contrast(x, y, *WINDOWS))
    def test_reject_overlap(self):
        x, y = demo_spectrum(True)
        with self.assertRaises(ValueError):
            spectral_contrast(x, y, (3.1, 3.4), ((3.0, 3.2), (3.5, 3.6)))
    def test_reject_few_points(self):
        with self.assertRaises(ValueError):
            spectral_contrast([1,2,3], [1,2,3], (1,1.5), ((2,2.5),(2.6,3)))
    def test_heuristic_missing_safe(self):
        self.assertEqual(candidate_score(1, 255), 100)
        self.assertIsNone(candidate_score(None, 255))
        self.assertIsNone(candidate_score(1, np.inf))
        self.assertTrue(0 <= candidate_score(2,300) <= 100)
