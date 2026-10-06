# Fabric-Care CSV Validator | Sewlore

[Open the public Fabric-Care CSV Validator](https://sewlore-fabric-care-validator.streamlit.app/)

Check anonymous before-and-after fabric-care records before comparing their changes. This Streamlit app identifies missing readings, inconsistent units and unusable CSV rows, then offers accepted records and correction notes as separate downloads.

The initial input is the supplied header with **no sample rows**. Validation runs only after the user confirms the anonymous-record restriction and presses **Validate CSV**. **Load hypothetical example** supplies three explicitly invented software rows: two accepted records and one mismatched-unit record. No fabric was washed, pressed or measured for these examples.

## Inputs and privacy

CSV must be UTF-8 (optional BOM), at most **128 KiB** and **250 non-empty sample records**. Keep the ten supplied columns in order. Use anonymous codes such as `sample-001` (`sample-` plus 1–6 digits), matching `cm`, `mm` or `in` units, and four positive finite numeric readings. Allowed care-method codes are `wash`, `dry`, `wash-and-dry`, `rinse`, `steam`, `press`, or `other`; these describe what the user actually did and do not prescribe care. Keep detailed method notes in the user's own records. **Leave the notes column empty.** Use `yes` for the rectangle assumption only when both paired spans describe actual flat rectangles; otherwise use `no` or leave blank.

Do not upload names, contact details, body measurements, personal identifiers, financial, health or other sensitive information. Uploaded or pasted CSV travels to the Streamlit server and is processed in memory. The application does not write user CSV to disk, use data caching, call external APIs, add analytics or print user data to logs. Session state temporarily holds the submitted result so download buttons can use it; clearing entries removes this app's result reference. Ordinary hosting-platform requests and usage statistics follow the platform's policy. The local configuration disables library usage statistics, but Community Cloud currently forces `browser.gatherUsageStats=true`; platform telemetry remains outside the app's control.

Malformed quoting, unsupported encoding or a policy/limit violation rejects the submission before calculations. A record with inconsistent columns or numerical errors receives correction notes. Valid records and correction notes remain separate. Changing the input hides previous results until explicit revalidation. Exports neutralize formula-like text as well as quoting CSV cells; numeric negative percentages remain numeric. Inspect spreadsheet import behaviour before relying on the exported file.

## Meaning of results

For each axis, contraction is `(before − after) / before × 100`. Positive means contraction; negative means expansion. Rectangular-area contraction is `100 × (1 − after_length / before_length × after_width / before_width)` and is omitted without the explicit rectangle assumption. Results describe entered readings, not a laboratory test, measurement certification, garment fit, recommended care or a prediction of later cycles. Physical fabric testing is not claimed.

The interactive guide links to the [recording guide](https://sewlore-preparation-notes.blogspot.com/2026/10/what-to-record-before-cutting-fabric.html), [browser-local single-pair calculator](https://sewlore-fabric-shrinkage.web.app/), [stretch and recovery method](https://sewlore.com/blogs/sewing-journal/measure-fabric-stretch-and-record-recovery), and [fabric and elastic guide](https://sewlore.com/blogs/sewing-journal/choose-fabric-and-elastic-for-sewing).

## Run locally

Use Python 3.12 and the pinned Streamlit dependency:

```sh
python -m venv .venv
# Activate this environment using the instructions for your operating system.
python -m pip install --index-url https://pypi.org/simple -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true
```

Open [http://localhost:8502/](http://localhost:8502/) in your browser. Stop the local server with Ctrl+C.

## Tests

Run the boundary and native app-flow checks with:

```sh
python -B -m unittest discover -s tests -v
```

The ten checks cover UTF-8 and byte/record limits, malformed CSV, the anonymous-record policy, rejected-identifier redaction, accepted/error separation, the blank initial state, explicit submission, hypothetical example, native upload, stale-result hiding and clearing. Streamlit's native AppTest executes the interface without a browser. Test fixtures are hypothetical software inputs, not physical fabric observations.

## Hosted deployment and source

The public app runs on Streamlit Community Cloud from the [`main` branch of gokimedia/sewlore-fabric-care-validator](https://github.com/gokimedia/sewlore-fabric-care-validator), with `app.py` as its entrypoint and Python 3.12. `requirements.txt` pins Streamlit 1.65.0. Source updates on the deployed branch trigger Community Cloud updates.

`app.py` provides the interface, `input_policy.py` enforces the hosted input restrictions, and `validator.py` performs CSV validation, signed calculations and safe exports. The repository includes a header-only template, a labelled hypothetical demo and tests. `.streamlit/config.toml` supplies the theme and local configuration. There are no secrets, external database credentials or account SDKs in the app.

Original code and educational copy © 2026 Sewlore, under the MIT licence in `LICENSE.txt`. The licence grants no trademark ownership or platform endorsement.

[Sewlore](https://sewlore.com/) · Thoughtful preparation for your next sewing project.
