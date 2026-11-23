# Start Here — FORGE

FORGE is built. You can run the complete offline aviation demo without an API key.

## Run it on your Mac

1. Unzip `FORGE.zip`.
2. Open Terminal in the extracted `FORGE` folder.
3. Run these commands using Python 3.12:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local address printed in Terminal. Leave Terminal running while you use the app.

## Try the whole workflow

1. Keep **Demo** selected. Click **Research Opportunity**.
2. Open **Evidence**. Inspect the sources; uncheck E4 if you want to exclude the manufacturing option.
3. Click **Approve Evidence & Continue**, then **Generate Technology Opportunities**.
4. Open **Opportunities**. Inspect the evaluations, choose your deep dive and add priorities.
5. Click **Approve Selection & Build Roadmap**.
6. Open **Roadmap**, then click **Run Independent AI Strategy Review**.
7. Read **Critic**, then open **Final brief** to download the report and audit log.

## Turn on live AI research

Copy `.env.example` to `.env`. Add your OpenAI API key there, never in source code. Start a new app session and choose **Live**. API access and usage charges are separate requirements. The model can be changed in the sidebar if needed.

Live mode is implemented and tested with mocked API responses; a paid live run was not possible in the build environment. Run the checklist in `docs/DEPLOYMENT.md` before presenting live research.

## Your included materials

- `README.md`: full setup, architecture, controls and limitations.
- `docs/PROJECT_REPORT.md`: graduate project report.
- `docs/ACADEMIC_REFERENCES.md`: five journal sources and scope notes.
- `docs/VIDEO_DEMO_SCRIPT.md`: narrated 5–7 minute demonstration script.
- `docs/PRESENTATION_OUTLINE.md`: nine-slide outline.
- `docs/PORTFOLIO_CASE_STUDY.md`: case study and résumé bullets.
- `docs/TESTING.md`: actual validation results.
- `sample_outputs/`: sample brief, runtime logs and silent demo recording.
- `screenshots/`: real application screenshots.

## Before final submission

Add a key and verify a live session, record your narration, and export this ChatGPT build conversation if your professor requires every development prompt and response. App session logs cover runtime interactions only. Hosting instructions are included, but no public app or GitHub repository has been published.
