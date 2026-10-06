"""Small, bounded upload policy for anonymous fabric-sample records only."""
import csv
import hashlib
import io
import re

from validator import INPUT_COLUMNS, validate_csv

MAX_BYTES = 128 * 1024
MAX_RECORDS = 250
SAMPLE_CODE = re.compile(r"sample-[0-9]{1,6}\Z")
CARE_CODES = ("wash", "dry", "wash-and-dry", "rinse", "steam", "press", "other")


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()


def diagnostic(field, message, record_number=0, sample_id=""):
    return {"record_number": record_number, "sample_id": sample_id,
            "field": field, "message": message}


def validate_submission(data):
    """Validate bytes without saving files or caching data across sessions.

    The original calculation core stays unchanged. The upload layer adds byte,
    row, encoding and anonymous-record restrictions before calling that core.
    """
    if not isinstance(data, bytes):
        raise TypeError("Provide the CSV as bytes.")
    if len(data) > MAX_BYTES:
        return [], [diagnostic("file size", "Use a UTF-8 CSV no larger than 128 KiB.")]
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], [diagnostic("encoding", "Save the CSV as UTF-8. Other encodings are not guessed.")]
    if "\x00" in text:
        return [], [diagnostic("encoding", "The CSV contains a null byte. Export it again as plain UTF-8 text.")]
    try:
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if header != list(INPUT_COLUMNS):
            return [], [diagnostic("header", "Use the exact supplied header, once, in its supplied order.", 1)]
        policy_errors = []
        count = 0
        for number, cells in enumerate(reader, start=2):
            if not cells:
                continue
            count += 1
            if count > MAX_RECORDS:
                return [], [diagnostic("record limit", "Use at most 250 non-empty sample records per CSV.")]
            if len(cells) != len(INPUT_COLUMNS):
                continue  # The original core diagnoses inconsistent column counts.
            row = dict(zip(INPUT_COLUMNS, cells))
            sample_id = row["sample_id"].strip()
            code_ok = bool(SAMPLE_CODE.fullmatch(sample_id))
            safe_code = sample_id if code_ok else ""
            if not code_ok:
                policy_errors.append(diagnostic("sample_id", "Use an anonymous code such as sample-001; no names or identifiers for people.", number))
            if row["care_method"].strip() not in CARE_CODES:
                policy_errors.append(diagnostic("care_method", "Use wash, dry, wash-and-dry, rinse, steam, press or other. Keep detailed care notes in your own records.", number, safe_code))
            if row["notes"].strip():
                policy_errors.append(diagnostic("notes", "Leave notes empty in this hosted app. Keep any free-text notes on your own device.", number, safe_code))
    except csv.Error:
        return [], [diagnostic("CSV", "The quoted CSV structure could not be read. Check quotes and separators before calculating.")]
    if policy_errors:
        return [], policy_errors
    records, errors = validate_csv(text)
    # Do not echo a malformed record's unrecognized identifier into diagnostics.
    for issue in errors:
        if not SAMPLE_CODE.fullmatch(issue["sample_id"]):
            issue["sample_id"] = ""
    return records, errors
