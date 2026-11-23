# FORGE Validation Record

Executed September 30, 2026 in Python 3.12.14 with Streamlit 1.64.0, OpenAI SDK 3.22.1, Pydantic 2.13.5, python-dotenv 1.2.3, pytest 9.1.1 and Playwright 1.63.0.

## Automated tests — PASS

`python -m pytest -q`: **24 passed**. Raw output is in `test-results.txt`.

| Coverage | Observed result |
|---|---|
| End-to-end demo export | Complete 16-section brief with clickable sources |
| Evidence rejection | E4 and its opportunity excluded from downstream output |
| First approval gate | Empty/unknown approvals rejected |
| Second approval gate | Deep dive must belong to selected opportunities |
| State changes | New research/evidence/selection clears stale downstream outputs |
| Reference integrity | Unknown evidence IDs and missing assessment dimensions rejected |
| Input validation | Whitespace-only required input rejected |
| Logging | JSONL writes and session JSON exports parse successfully |
| Secrets | Environment key and common key patterns removed from test log output |
| Disk failure | In-memory export survives unavailable log directory |
| API request syntax | Real installed SDK serializes Responses search and strict schema requests |
| Evidence provenance | Findings outside actual citation annotations blocked |
| Approved input boundary | Only approved evidence and submitted human feedback sent onward |
| Error handling | Authentication, quota/rate limit, server error and timeout handled |
| Model output handling | Refusal, incomplete and malformed output blocked; raw malformed response retained |
| Streamlit AppTest | Research → exclusion → approvals → roadmap → critic → downloads renders without exceptions |

## Runtime and browser — PASS

A separate Streamlit server process returned `ok` from `/_stcore/health`.

An actual Chromium browser exercised the complete demo: loaded the app, excluded E4, submitted evidence approval, generated three remaining options, selected a deep dive, submitted comments, generated a roadmap, ran the critic and downloaded both a Markdown brief and JSON audit log. It then captured a mobile-width view. No Streamlit exception was present at the end.

Seven PNG captures are in `screenshots/`. The browser-downloaded outputs are `sample_outputs/browser_downloaded_brief.md` and `sample_outputs/browser_session.json`. A silent recording of the real browser walkthrough is included as `sample_outputs/FORGE_silent_demo.mp4`; it is supplemental evidence, not a narrated 5–7 minute submission. Captures were visually inspected and disabled demo-input contrast was improved.

The standard browser download was unavailable in this environment. A packaged Chromium executable was used for testing. That browser is not part of application runtime dependencies. The reproducible capture script supports `FORGE_CHROMIUM` for an explicitly supplied browser executable.

## Not established by these tests

- No paid live OpenAI call: the environment had no API key. Mock transport tests verify request/response integration, not actual account access or model behavior.
- No factual entailment benchmark, calibrated model confidence, adversarial security assessment, user study or operational pilot.
- No cloud deployment, multi-user load test, durable session recovery or production security certification.
- No measured cost savings, downtime reduction, accuracy improvement or user productivity result.

## Reproduce

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/generate_sample.py
python -m playwright install chromium
python scripts/capture_demo.py
```

For the capture script, install Playwright's FFmpeg as part of its normal browser installation if recording support is missing. Follow the separate live smoke-test checklist in `DEPLOYMENT.md` after adding your own authorized key.
