# Running and Sharing FORGE

## Local runtime

Use the README quick start. The tested interpreter is Python 3.12. Keep the terminal process running while using the app. Stop with Ctrl+C. Demo mode requires no credentials.

## GitHub-ready publication

Create a repository under your own account when ready and add the project files. This package does not publish a repository for you. Check `.gitignore` before your first commit. Never add `.env`, `.streamlit/secrets.toml`, runtime logs, credentials or confidential input. The public sample outputs contain only the fictional demo case.

## Streamlit Community Cloud target

This package uses the standard `app.py`, `requirements.txt` and `.streamlit/config.toml` layout. Use Python 3.12 if the host offers it. Connect your repository through the host's deployment flow and select `app.py` as the entry point. For live mode, add server-side secrets:

```toml
OPENAI_API_KEY = "your_key_here"
OPENAI_MODEL = "gpt-6.1-terra"
```

The app reads those values server-side. Do not put them in source control. No deployed instance has been tested or created by this build. Consult the host's current deployment documentation if its UI changes.

Local disk on a managed host may be ephemeral. Download logs before the session ends. This MVP intentionally has no authentication or quota controls. Prefer a keyless demo for a publicly accessible portfolio. Add host-level access control and budget protection before sharing a live-key instance widely.

## First live smoke test

1. Add the API key, start a fresh session, choose Live and confirm model access.
2. Enter a nonconfidential problem. Run research and inspect the sources and dates.
3. Exclude one finding. Confirm it does not appear in the exported Strategist input.
4. Generate opportunities; check evidence support and rubric compliance.
5. Select a deep dive and add a concrete scope constraint. Inspect the roadmap's response to it.
6. Run the critic. Verify all thirteen categories and the nontechnology alternative.
7. Download the brief and log. Inspect costs/usage in your API account and document observed latency.
8. If a stage fails, preserve the log and retry intentionally. Do not silently substitute demo results for live output.

## Troubleshooting

Missing key: use Demo or add the environment/host secret. Authentication: check the account and key. Rate limit/quota: check billing and limits. Unsupported model/tool: choose a model your account can access with Responses, web search and JSON schema support. Empty citations: refine the question and rerun; FORGE blocks unsourced findings. Invalid output: retry the stage. Disk logging warning: export the in-memory log before closing. Blank page: inspect the Streamlit terminal error and confirm dependencies are installed in the active virtual environment.
