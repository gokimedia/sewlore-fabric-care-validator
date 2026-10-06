# Fabric-Care CSV Validator | Sewlore

An original Streamlit interface for checking anonymous before-and-after fabric-care records before calculating changes. It adds useful batch diagnostics and separate accepted-record/correction downloads to Sewlore's existing standard-library validation core. It does not repeat the geometric overlay lesson or claim a measured fabric dataset.

The initial input is the supplied header with **no sample rows**. Validation runs only after the user confirms the anonymous-record restriction and presses **Validate CSV**. **Load hypothetical example** supplies three explicitly invented software rows: two accepted records and one mismatched-unit record. No fabric was washed, pressed or measured for these examples.

## Inputs and privacy

CSV must be UTF-8 (optional BOM), at most **128 KiB** and **250 non-empty sample records**. Keep the ten supplied columns in order. Use anonymous codes such as `sample-001` (`sample-` plus 1–6 digits), matching `cm`, `mm` or `in` units, and four positive finite numeric readings. Allowed care-method codes are `wash`, `dry`, `wash-and-dry`, `rinse`, `steam`, `press`, or `other`; these describe what the user actually did and do not prescribe care. Keep detailed method notes in the user's own records. **Leave the notes column empty.** Use `yes` for the rectangle assumption only when both paired spans describe actual flat rectangles; otherwise use `no` or leave blank.

Do not upload names, contact details, body measurements, personal identifiers, financial, health or other sensitive information. Uploaded or pasted CSV travels to the Streamlit server and is processed in memory. The application does not write user CSV to disk, use data caching, call external APIs, add analytics or print user data to logs. Session state temporarily holds the submitted result so download buttons can use it; clearing entries removes this app's result reference. This is **not browser-only processing**. Ordinary hosting-platform requests and usage statistics follow the platform's policy. The local configuration disables library usage statistics, but Community Cloud currently forces `browser.gatherUsageStats=true`; this app cannot promise zero platform telemetry.

Malformed quoting, unsupported encoding or a policy/limit violation rejects the submission before calculations. A record with inconsistent columns or numerical errors is diagnosed by the unchanged calculation core. Valid records and correction notes remain separate. Changing the input hides previous results until explicit revalidation. Exports neutralize formula-like text as well as quoting CSV cells; numeric negative percentages remain numeric. Inspect spreadsheet import behaviour before relying on the exported file.

## Meaning of results

For each axis, contraction is `(before − after) / before × 100`. Positive means contraction; negative means expansion. Rectangular-area contraction is `100 × (1 − after_length / before_length × after_width / before_width)` and is omitted without the explicit rectangle assumption. Results describe entered readings, not a laboratory test, measurement certification, garment fit, recommended care or a prediction of later cycles. Physical fabric testing is not claimed.

The interactive guide links to the [recording guide](https://sewlore-preparation-notes.blogspot.com/2026/10/what-to-record-before-cutting-fabric.html), [browser-local single-pair calculator](https://sewlore-fabric-shrinkage.web.app/), [stretch and recovery method](https://sewlore.com/blogs/sewing-journal/measure-fabric-stretch-and-record-recovery), and [fabric and elastic guide](https://sewlore.com/blogs/sewing-journal/choose-fabric-and-elastic-for-sewing).

## Run locally

Use Python 3.12 and the pinned Streamlit dependency:

```sh
python -m venv .venv
# Activate this environment using the instructions for your operating system.
python -m pip install --index-url https://pypi.org/simple -r requirements.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.headless true
```

The existing prepared local environment contains Streamlit 1.65.0. No server is left running by package preparation. Run the new boundary and native app-flow checks with:

```sh
python -B -m unittest discover -s tests -v
```

`validator.py` is a byte-identical copy of the original Sewlore Colab validation core, whose 22 tests already passed. These new checks target the input policy and interface; the unchanged 22-test suite is not duplicated or rerun. Streamlit's native AppTest executes the application without a browser; visual/mobile and hosted behaviour require separate browser review.

## Public repository and deployment

Only publish the source files in the manifest's public-file allowlist: `app.py`, `validator.py`, `input_policy.py`, `requirements.txt`, `.streamlit/config.toml`, `.gitignore`, `README.md`, `LICENSE.txt`, the header-only template, the labelled hypothetical demo and the two test files. Do not upload `.venv`, private manifests, validation reports or runtime data. There are no secrets, external database credentials or account SDKs in this app.

Community Cloud deploys from a GitHub repository where the deploying user has admin access. Select the actual repository, branch and `app.py`, choose Python 3.12 and an available descriptive subdomain, and verify public sharing. The actual URL is not invented or embedded in this draft. This preparation does not create an account, authorize OAuth, accept Terms, push source or deploy an app. Official onboarding: [connect GitHub](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account), [deploy](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy), and [share](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app).

Original code and educational copy © 2026 Sewlore, under the MIT licence in `LICENSE.txt`. The licence grants no trademark ownership or platform endorsement.
