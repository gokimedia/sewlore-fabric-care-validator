"""Sewlore's original fabric-care CSV diagnostic interface.

User CSVs are processed in server memory. No file writes, cache decorators,
external APIs, account integration or application-added analytics are used.
"""
from pathlib import Path

import streamlit as st

from input_policy import MAX_BYTES, MAX_RECORDS, fingerprint, validate_submission
from validator import BLANK_CSV, export_errors, export_validated

HERE = Path(__file__).resolve().parent
DEMO = (HERE / "demo-hypothetical.csv").read_text(encoding="utf-8")

st.set_page_config(page_title="Fabric-Care CSV Validator | Sewlore", page_icon="🧵", layout="centered")


def reset_input(example=False):
    st.session_state["paste_csv"] = DEMO if example else BLANK_CSV
    st.session_state["input_mode"] = "Paste CSV"
    st.session_state["permission"] = False
    st.session_state["upload_epoch"] = st.session_state.get("upload_epoch", 0) + 1
    st.session_state.pop("submitted_result", None)


st.session_state.setdefault("paste_csv", BLANK_CSV)
st.session_state.setdefault("upload_epoch", 0)

st.caption("SEWLORE · FABRIC PREPARATION")
st.title("Fabric-Care CSV Validator")
st.header("Check the records before calculating the changes.", divider="gray")
st.write("Find missing readings, inconsistent units and unusable CSV rows. Accepted records and correction notes are available as separate downloads.")
st.info("Privacy: pasted or uploaded CSV is sent to this app's server and processed in memory. This app does not write it to disk, cache it or send it to an external API. Use anonymous fabric-sample codes only. Do not enter names, contact details, body measurements, financial or health information. Leave the notes column empty. Hosting-platform requests and usage statistics follow its own policy.")

left, right = st.columns(2)
left.button("Load hypothetical example", on_click=reset_input, args=(True,), width="stretch")
right.button("Clear entries and results", on_click=reset_input, width="stretch")

mode = st.radio("CSV input method", ["Paste CSV", "Upload CSV"], key="input_mode", horizontal=True)
if mode == "Paste CSV":
    source = st.text_area("CSV text", key="paste_csv", height=210,
                          help="The supplied header starts with no records. Keep its columns in their original order.")
    payload = source.encode("utf-8")
else:
    uploaded = st.file_uploader("Choose one anonymous fabric-care CSV", type="csv", accept_multiple_files=False,
                                max_upload_size=1, key=f"csv_upload_{st.session_state['upload_epoch']}",
                                help="UTF-8 only. The app accepts up to 128 KiB and 250 non-empty records.")
    payload = uploaded.getvalue() if uploaded is not None else b""

if payload == DEMO.encode("utf-8"):
    st.warning("Hypothetical software example: these three rows are invented to demonstrate validation. No fabric was washed, pressed or measured for this example.")

st.caption(f"Maximum {MAX_BYTES // 1024} KiB · {MAX_RECORDS} non-empty records · UTF-8 with optional BOM")
st.checkbox("I confirm that this CSV contains only anonymous fabric-sample records and no personal or sensitive information.", key="permission")

if st.button("Validate CSV", type="primary", disabled=not st.session_state.get("permission", False)):
    accepted, errors = validate_submission(payload)
    st.session_state["submitted_result"] = {
        "input_hash": fingerprint(payload), "records": accepted, "errors": errors,
    }

result = st.session_state.get("submitted_result")
if result and result["input_hash"] != fingerprint(payload):
    st.warning("The input changed. Validate this version to replace the previous results.")
    result = None

if result is not None:
    records, errors = result["records"], result["errors"]
    st.subheader("Validation results")
    if records:
        st.success(f"{len(records)} accepted sample record(s).")
        st.write("Positive percentages mean contraction; negative percentages mean expansion. A blank area result means no rectangular-area assumption was made.")
        preview = [{
            "Sample code": row["sample_id"], "Unit": row["before_unit"],
            "Length contraction (%)": row["length_change_percent"],
            "Width contraction (%)": row["width_change_percent"],
            "Rectangular area contraction (%)": row["rectangular_area_change_percent"],
        } for row in records]
        st.dataframe(preview, hide_index=True, width="stretch")
    elif not errors:
        st.info("The header is valid, but there are no sample records. No fabric-change calculation has been made.")
    if errors:
        st.error(f"{len(errors)} correction note(s). Correct the source CSV and validate again.")
        st.dataframe(errors, hide_index=True, width="stretch")
    st.download_button("Download accepted records CSV", export_validated(records),
                       file_name="fabric-care-accepted.csv", mime="text/csv", on_click="ignore")
    st.download_button("Download correction notes CSV", export_errors(errors),
                       file_name="fabric-care-corrections.csv", mime="text/csv", on_click="ignore")
    st.caption("Exports quote CSV cells and neutralize formula-like text. Numeric signed results stay numeric. Check a spreadsheet import before relying on it.")
else:
    st.caption("Nothing has been validated yet. Validation runs only when you press Validate CSV.")

with st.expander("Column guide and blank template", expanded=False):
    st.write("Use sample-001 or another sample- followed by 1–6 digits. This is a fabric code, never a person's name. Before and after units must match: cm, mm or in. Enter four finite readings greater than zero, without unit text inside the numeric cells.")
    st.write("Care-method codes: wash, dry, wash-and-dry, rinse, steam, press or other. These name the treatment you actually performed; they are not care recommendations. Keep temperatures, cycles and detailed method notes in your own records. Leave notes empty here.")
    st.write("Use yes in rectangle_assumption only when both before and after readings describe rectangular, flat spans. Use no or leave it blank to omit area. CSV record numbers count logical records, with the header as record 1; a quoted line break stays inside its record.")
    st.download_button("Download blank CSV template", BLANK_CSV, file_name="fabric-care-blank.csv", mime="text/csv", on_click="ignore")

st.header("Keep a usable before-and-after record")
st.markdown("""
Start with an anonymous code for each fabric sample, then mark the span you will
measure. Keep length and width separate. Use the same marked span before and
after the care treatment, and record the actual method, resting or drying
condition and units in your own project notes. Choose care from the fabric
manufacturer's guidance; the names in this app do not prescribe a treatment.
The [recording guide](https://sewlore-preparation-notes.blogspot.com/2026/10/what-to-record-before-cutting-fabric.html)
explains how pattern revision and paired sample notes stay useful together.

Give each pair one unit. A before reading in centimetres and an after reading
in millimetres can look like a dramatic change while describing similar
lengths. This validator flags the mismatch instead of guessing your intention.
Convert the readings first, check the original notes, and resubmit. A missing,
zero or non-finite reading cannot be used as a reliable baseline. A correction
note points to the record and field; it does not silently replace a value.

For an accepted axis, contraction is `(before − after) / before × 100`.
An after span larger than its before span produces a negative percentage,
which remains visible as expansion. Use the
[single-pair shrinkage calculator](https://sewlore-fabric-shrinkage.web.app/)
when you want to compare one pair without sending a CSV to this hosted app.
That calculator performs its arithmetic in your browser.

Area is optional. Multiplying the two side ratios compares rectangular areas,
not the amount of material in an irregular or distorted shape. It also does
not establish garment fit, a care standard or what another care cycle will
do. Keep an unusual value visible and check its context rather than clipping
it to zero. Pulling a sample and releasing it is a different method; the
[stretch and recovery guide](https://sewlore.com/blogs/sewing-journal/measure-fabric-stretch-and-record-recovery)
keeps those readings distinct from fabric-care measurements.

Download accepted records and correction notes separately. The accepted file
contains only rows that passed this check; it is not a complete replacement
for your original record. Save your own source notes and resolve every
correction before comparing samples. All demonstrations here are hypothetical
software examples. They are not observations from a physical fabric test or
evidence of measurement precision. The
[fabric and elastic guide](https://sewlore.com/blogs/sewing-journal/choose-fabric-and-elastic-for-sewing)
helps connect sample preparation with the requirements of an actual pattern.
""")
st.divider()
st.caption("Original tool and educational copy © 2026 Sewlore · MIT code licence")
st.markdown("[Sewlore](https://sewlore.com/) · Thoughtful preparation for your next sewing project.")
