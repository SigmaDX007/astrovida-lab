import json
import tempfile
import unittest
from pathlib import Path
from alienlab.storage import list_rows, register_hypothesis, report_markdown, save_run
class TestStorage(unittest.TestCase):
    def test_registration_and_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp)/"lab.sqlite"
            hid = register_hypothesis(db, title="Exemplo", claim="Absorção A",
                null_hypothesis="Sem absorção", prediction="Fluxo menor",
                falsification="Sem contraste", confounders="Ruído")
            self.assertEqual(len(list_rows(db, "hypotheses")), 1)
            eid = save_run(db, hypothesis_id=hid, data_origin="SINTÉTICO",
                data_sha256="a"*64, parameters={"seed":42}, results={"p_value":.01})
            self.assertTrue(eid.startswith("E-"))
            self.assertEqual(json.loads(list_rows(db,"runs")[0]["parameters_json"]), {"seed":42})
            self.assertEqual(list_rows(db,"hypotheses")[0]["status"], "testada_exploratoriamente")
            self.assertIn("SINTÉTICO", report_markdown(db))
    def test_reject_missing_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/"lab.sqlite"
            with self.assertRaises(ValueError):
                register_hypothesis(db, title="x", claim="", null_hypothesis="H0",
                    prediction="p", falsification="f", confounders="c")
            with self.assertRaises(ValueError):
                save_run(db, hypothesis_id="missing", data_origin="local",
                    data_sha256="bad", parameters={}, results={})
    def test_allowlist(self):
        with self.assertRaises(ValueError):
            list_rows("anything.sqlite", "runs; DROP TABLE hypotheses")
