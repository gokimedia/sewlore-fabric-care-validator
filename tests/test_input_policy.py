"""Boundary checks for the new upload layer; fixtures are hypothetical software data."""
import csv
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from input_policy import MAX_BYTES, MAX_RECORDS, validate_submission
from validator import BLANK_CSV, INPUT_COLUMNS

HERE = Path(__file__).resolve().parents[1]
DEMO = (HERE / "demo-hypothetical.csv").read_bytes()


def fixture(**changes):
    row = dict(zip(INPUT_COLUMNS, ["sample-001", "cm", "cm", "20", "20", "19", "19.5", "wash", "yes", ""]))
    row.update(changes)
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(INPUT_COLUMNS)
    writer.writerow([row[k] for k in INPUT_COLUMNS])
    return output.getvalue().encode("utf-8")


class InputPolicyTests(unittest.TestCase):
    def test_blank_and_utf8_bom_remain_empty(self):
        for raw in (BLANK_CSV.encode(), b"\xef\xbb\xbf" + BLANK_CSV.encode()):
            self.assertEqual(validate_submission(raw), ([], []))

    def test_byte_limit_is_inclusive_and_not_a_character_limit(self):
        raw = BLANK_CSV.encode()
        self.assertEqual(validate_submission(raw + b"\n" * (MAX_BYTES - len(raw))), ([], []))
        for oversized in (b"x" * (MAX_BYTES + 1), ("é" * (MAX_BYTES // 2 + 1)).encode()):
            rows, errors = validate_submission(oversized)
            self.assertFalse(rows)
            self.assertEqual(errors[0]["field"], "file size")

    def test_nonempty_record_limit_not_empty_line_count(self):
        row = fixture().split(b"\n", 1)[1]
        raw = BLANK_CSV.encode() + row * MAX_RECORDS
        records, errors = validate_submission(raw)
        self.assertEqual(len(records), MAX_RECORDS)
        self.assertFalse(errors)
        self.assertEqual(validate_submission(raw + row)[1][0]["field"], "record limit")

    def test_encoding_null_and_structural_failures_are_not_repaired(self):
        for raw, field in [(b"\xff", "encoding"), (BLANK_CSV.encode() + b"\x00", "encoding"),
                           (fixture() + b'"unterminated\n', "CSV"), (b"unrecognized,header\n", "header")]:
            rows, errors = validate_submission(raw)
            self.assertFalse(rows)
            self.assertEqual(errors[0]["field"], field)

    def test_anonymous_policy_does_not_echo_rejected_free_text(self):
        rows, errors = validate_submission(fixture(sample_id="person name", care_method="personal note", notes="private detail"))
        self.assertFalse(rows)
        self.assertEqual({e["field"] for e in errors}, {"sample_id", "care_method", "notes"})
        self.assertTrue(all(e["sample_id"] == "" for e in errors))
        self.assertNotIn("private detail", str(errors))
        self.assertNotIn("person name", str(errors))

    def test_short_row_diagnostics_redact_unrecognized_identifiers(self):
        rows, errors = validate_submission(BLANK_CSV.encode() + b"person name,cm\n")
        self.assertFalse(rows)
        self.assertEqual(errors[0]["field"], "columns")
        self.assertEqual(errors[0]["sample_id"], "")

    def test_demo_integrates_core_without_discarding_valid_records(self):
        rows, errors = validate_submission(DEMO)
        self.assertEqual([r["sample_id"] for r in rows], ["sample-001", "sample-003"])
        self.assertEqual(errors[0]["sample_id"], "sample-002")
        self.assertEqual(errors[0]["field"], "units")
        self.assertAlmostEqual(rows[0]["rectangular_area_change_percent"], 7.375)
        self.assertAlmostEqual(rows[1]["length_change_percent"], -5)
        self.assertIsNone(rows[1]["rectangular_area_change_percent"])


if __name__ == "__main__":
    unittest.main()
