# FORGE | Portfolio Case Study

## Problem

A technology recommendation is only useful if a decision maker can inspect its evidence, understand the tradeoffs and decide what to test. Generic AI answers often make that process difficult to trace.

## Approach

FORGE structures the decision into research, evidence approval, opportunity evaluation, human selection, pilot planning and adversarial review. It turns the result into a source-linked strategy brief rather than a chat transcript.

## My Role

I defined the product problem, target users, workflow, human review requirements and portfolio goals in the development brief. An AI coding assistant implemented and tested this MVP from that brief. My next responsibility is to review the code and source support, run live trials, evaluate the tool with users and explain the design decisions. This case study should be updated as I complete those steps; it does not imply that I personally hand-coded every component or conducted user testing already.

## Architecture

A Python/Streamlit interface coordinates three logical agents. The Researcher searches and structures evidence. The Strategist generates opportunities and a roadmap after human approval. The Critic reviews the proposed plan in a separate request. Pydantic contracts and explicit state transitions constrain the process; JSONL logs preserve runtime interactions.

## Human-Centered Design Decisions

Users can reject evidence before it influences recommendations, inspect the rating criteria, choose opportunities to pursue, and add implementation priorities. Changing an approval invalidates outdated downstream output. The final brief includes unresolved criticism so uncertainty is visible at the point of decision.

## Challenges

A real URL does not necessarily support a generated claim. FORGE checks source provenance and citation membership but still depends on human source inspection. Another challenge is separating promising technology from demonstrated value: the application proposes measurements instead of reporting invented savings. The offline demo provides a reliable presentation path and is explicitly distinguished from live research.

## Results

The implemented MVP supports the complete offline aviation workflow, downloadable Markdown briefs and session audit exports. Automated workflow, API transport and Streamlit UI tests pass; exact test results are in `TESTING.md`. No paid API run, user study, production deployment or business improvement has been established.

## Lessons Learned

The development illustrates why human review must change what the system can do, not merely appear as a warning. It also shows that source checking, session state and failure behavior are as important as the quality of the prompt. These are implementation lessons, not findings from a completed user study.

## Future Development

The next priority is live evaluation with verified source/claim pairs, followed by user testing. Durable session storage, stronger claim-level grounding and cost controls should come before expanding agent count or adding operational automation.

## Possible Résumé Bullets

Use these after reviewing the implementation and being prepared to demonstrate it:

- Defined and developed FORGE with AI coding assistance, a Python/Streamlit technology strategy prototype combining research, opportunity evaluation, pilot roadmaps and adversarial AI review.
- Designed two human approval gates with approved-evidence filtering, transparent qualitative criteria, citation checks and auditable session exports.
- Built a public-data aviation demonstration and automated tests for workflow state, API request handling, source filtering and strategy-brief generation.

Do not claim reduced downtime, financial savings, deployed customers or validated decision improvements without a completed evaluation.
