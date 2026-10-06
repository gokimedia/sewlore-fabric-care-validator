"""Original Sewlore lesson code. No network, account access or physical test data."""
import csv
import io
import math
import re

INPUT_COLUMNS = (
    "sample_id", "before_unit", "after_unit", "before_length", "before_width",
    "after_length", "after_width", "care_method", "rectangle_assumption", "notes",
)
OUTPUT_COLUMNS = INPUT_COLUMNS + (
    "length_change_percent", "width_change_percent", "rectangular_area_change_percent",
)
ERROR_COLUMNS = ("record_number", "sample_id", "field", "message")
UNIT_MM = {"mm": 1.0, "cm": 10.0, "in": 25.4}
DECIMAL = re.compile(r"^\+?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:e[+-]?[0-9]+)?$", re.I)
BLANK_CSV = ",".join(INPUT_COLUMNS) + "\n"

def positive_number(value):
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("Use a finite decimal number greater than zero.")
    if isinstance(value, str) and not DECIMAL.fullmatch(value.strip()):
        raise ValueError("Use a decimal number with no unit text or thousands separator.")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError("The reading must be finite and greater than zero.")
    return number

def to_mm(value, unit):
    if unit not in UNIT_MM:
        raise ValueError("The unit must be cm, mm or in.")
    result = positive_number(value) * UNIT_MM[unit]
    if not math.isfinite(result) or result <= 0:
        raise ValueError("The converted length is outside the supported numeric range.")
    return result

def convert_length(value, from_unit, to_unit):
    if to_unit not in UNIT_MM:
        raise ValueError("The destination unit must be cm, mm or in.")
    result = to_mm(value, from_unit) / UNIT_MM[to_unit]
    if not math.isfinite(result) or result <= 0:
        raise ValueError("The conversion is outside the supported numeric range.")
    return result

def calculate_changes(before_length_mm, before_width_mm, after_length_mm, after_width_mm, rectangle_assumption=False):
    if not isinstance(rectangle_assumption, bool):
        raise ValueError("The rectangle assumption must be explicitly True or False.")
    before_length_mm, before_width_mm, after_length_mm, after_width_mm = map(
        positive_number, (before_length_mm, before_width_mm, after_length_mm, after_width_mm)
    )
    length_ratio = after_length_mm / before_length_mm
    width_ratio = after_width_mm / before_width_mm
    if not all(math.isfinite(r) and r > 0 for r in (length_ratio, width_ratio)):
        raise ValueError("These magnitudes cannot be compared reliably.")
    length = (1 - length_ratio) * 100
    width = (1 - width_ratio) * 100
    if not all(math.isfinite(r) for r in (length, width)):
        raise ValueError("The axis change is outside the supported numeric range.")
    area = None
    if rectangle_assumption:
        ratio = length_ratio * width_ratio
        area = (1 - ratio) * 100
        if not math.isfinite(area) or ratio <= 0:
            raise ValueError("The requested rectangular area change cannot be represented reliably.")
    return {"length_change_percent": length, "width_change_percent": width,
            "rectangular_area_change_percent": area}

def validate_csv(raw_csv):
    """Return separately validated records and diagnostics. Header is logical record 1."""
    if not isinstance(raw_csv, str):
        raise TypeError("Provide CSV as text.")
    if len(raw_csv) > 1_000_000:
        return [], [{"record_number": 0, "sample_id": "", "field": "CSV", "message": "Use a CSV smaller than one million characters."}]
    diagnostics = []
    def issue(number, sample_id, field, message):
        diagnostics.append({"record_number": number, "sample_id": sample_id, "field": field, "message": message})
    try:
        reader = csv.reader(io.StringIO(raw_csv.removeprefix("\ufeff"), newline=""), strict=True)
        header = next(reader, None)
        if header != list(INPUT_COLUMNS):
            issue(1, "", "header", "Use the exact supplied header, once, in its supplied order.")
            return [], diagnostics
        rows = list(reader)  # Parse the entire structure before calculating any record.
    except csv.Error as error:
        issue(0, "", "CSV", f"CSV structure could not be read: {error}")
        return [], diagnostics
    validated = []
    for number, cells in enumerate(rows, start=2):
        if not cells:  # Ignore a completely empty line, never a partly empty record.
            continue
        sample_id = cells[0].strip() if cells else ""
        if len(cells) != len(INPUT_COLUMNS):
            issue(number, sample_id, "columns", f"Expected {len(INPUT_COLUMNS)} cells; found {len(cells)}.")
            continue
        row = dict(zip(INPUT_COLUMNS, cells))
        start_errors = len(diagnostics)
        row["sample_id"] = sample_id
        row["care_method"] = row["care_method"].strip()
        for field in ("sample_id", "care_method"):
            if not row[field]: issue(number, sample_id, field, "Record this value before comparing the sample.")
        for field in ("before_unit", "after_unit"):
            row[field] = row[field].strip().lower()
            if row[field] not in UNIT_MM: issue(number, sample_id, field, "Use cm, mm or in.")
        if row["before_unit"] in UNIT_MM and row["after_unit"] in UNIT_MM and row["before_unit"] != row["after_unit"]:
            issue(number, sample_id, "units", "Before and after units must match. Convert the readings first.")
        assumption = row["rectangle_assumption"].strip().lower()
        if assumption not in ("", "yes", "no"):
            issue(number, sample_id, "rectangle_assumption", "Use yes only for actual rectangles; use no or leave blank otherwise.")
        row["rectangle_assumption"] = "yes" if assumption == "yes" else "no"
        mm = {}
        for field in ("before_length", "before_width", "after_length", "after_width"):
            unit = row["before_unit"] if field.startswith("before_") else row["after_unit"]
            try:
                row[field] = positive_number(row[field])
                mm[field] = to_mm(row[field], unit)
            except (ValueError, OverflowError) as error:
                issue(number, sample_id, field, str(error))
        if len(diagnostics) != start_errors:
            continue
        try:
            changes = calculate_changes(mm["before_length"], mm["before_width"], mm["after_length"], mm["after_width"], assumption == "yes")
            validated.append({**row, **changes})
        except ValueError as error:
            issue(number, sample_id, "calculation", str(error))
    return validated, diagnostics

def spreadsheet_safe(value):
    """Neutralize formula-like free text in exports; do not alter internal notes."""
    if value is None:
        return ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if not math.isfinite(value): raise ValueError("Cannot export a non-finite numeric value.")
        return format(value, ".12g")  # Genuine numeric negatives remain numbers.
    text = str(value)
    if text.startswith(("\t", "\r", "\n")) or text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text

def export_csv(records, columns):
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerow(columns)
    for row in records:
        writer.writerow([spreadsheet_safe(row.get(field)) for field in columns])
    return buffer.getvalue()

def export_validated(records):
    return export_csv(records, OUTPUT_COLUMNS)

def export_errors(diagnostics):
    return export_csv(diagnostics, ERROR_COLUMNS)
