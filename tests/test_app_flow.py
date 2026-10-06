"""Streamlit's native simulated-app tests; no browser or hosted account access."""
from pathlib import Path
import sys
import unittest

from streamlit.testing.v1 import AppTest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
from validator import BLANK_CSV


def button(app, label):
    return next(item for item in app.button if item.label == label)


class AppFlowTests(unittest.TestCase):
    def create(self):
        app = AppTest.from_file(str(HERE / "app.py"), default_timeout=15).run()
        self.assertFalse(app.exception)
        return app

    def test_blank_default_consent_and_explicit_submit(self):
        app = self.create()
        self.assertEqual(app.text_area[0].value, BLANK_CSV)
        self.assertTrue(button(app, "Validate CSV").disabled)
        self.assertFalse(app.checkbox[0].value)
        app.checkbox[0].check().run()
        button(app, "Validate CSV").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["submitted_result"]["records"], [])
        self.assertTrue(any("no sample records" in item.value for item in app.info))

    def test_demo_results_stale_input_and_clear(self):
        app = self.create()
        button(app, "Load hypothetical example").click().run()
        self.assertTrue(any("Hypothetical software example" in item.value for item in app.warning))
        self.assertTrue(button(app, "Validate CSV").disabled)
        app.checkbox[0].check().run()
        button(app, "Validate CSV").click().run()
        self.assertFalse(app.exception)
        result = app.session_state["submitted_result"]
        self.assertEqual(len(result["records"]), 2)
        self.assertEqual(len(result["errors"]), 1)
        self.assertEqual(len(app.dataframe), 2)
        app.text_area[0].set_value(BLANK_CSV).run()
        self.assertTrue(any("input changed" in item.value for item in app.warning))
        self.assertEqual(len(app.dataframe), 0)
        button(app, "Clear entries and results").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.text_area[0].value, BLANK_CSV)
        self.assertFalse(app.checkbox[0].value)
        self.assertNotIn("submitted_result", app.session_state)

    def test_native_upload_uses_the_same_policy(self):
        app = self.create()
        app.radio[0].set_value("Upload CSV").run()
        app.file_uploader[0].upload("hypothetical.csv", (HERE / "demo-hypothetical.csv").read_bytes(), "text/csv").run()
        app.checkbox[0].check().run()
        button(app, "Validate CSV").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state["submitted_result"]["records"]), 2)


if __name__ == "__main__":
    unittest.main()
