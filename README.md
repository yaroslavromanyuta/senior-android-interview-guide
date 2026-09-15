# Senior Android Interview Preparation Guide

A bilingual (Ukrainian/English) HTML guide for structured Senior Android interview preparation.

## Repository layout

- `index.html` — the working guide; this file will evolve through small, reviewable updates.
- `reference/original-guide.html` — immutable baseline copied from the source guide. Do not edit it.
- `reference/original-guide.sha256` — checksum used to verify the baseline has not changed.
- `scripts/validate.py` — dependency-free structural validation for both HTML documents.

## Incremental workflow

1. Keep `reference/original-guide.html` unchanged.
2. Make focused content or presentation changes only in `index.html`.
3. Run validation:

   ```bash
   python3 scripts/validate.py
   ```

4. Review the diff, then commit one coherent change at a time.

The initial `index.html` is an exact copy of the baseline. It is intentionally a starting point and will evolve incrementally.

## Viewing locally

Open `index.html` directly in a browser. No build step, external service, or GitHub Pages deployment is required.
