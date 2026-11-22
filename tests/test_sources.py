import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from alienlab.sources import PS_COLUMNS, exoplanet_query, sha256_file
class TestSources(unittest.TestCase):
    @patch("alienlab.sources.requests.get")
    def test_nasa_query_filter_no_injection(self, get):
        payload = ",".join(PS_COLUMNS) + "\nK2-18 b,K2-18,1,2,2.6,280,10,0.1,3400,30,2015,Transit\n"
        get.return_value = Mock(text=payload, status_code=200)
        data, url = exoplanet_query(100, "K2-18")
        self.assertEqual(len(data), 1)
        self.assertTrue(url.startswith("https://exoplanetarchive.ipac.caltech.edu/TAP/sync?"))
        self.assertEqual(get.call_args.kwargs["timeout"], 45)
        self.assertNotIn("K2-18", get.call_args.kwargs["params"]["query"])
    @patch("alienlab.sources.requests.get")
    def test_limit_validation(self, get):
        with self.assertRaises(ValueError):
            exoplanet_query(5000)
        get.assert_not_called()
    def test_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"sample.csv"
            path.write_bytes(b"abc")
            self.assertEqual(sha256_file(path), hashlib.sha256(b"abc").hexdigest())
