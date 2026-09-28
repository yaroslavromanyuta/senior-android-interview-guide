# Senior Android Interview Preparation Guide

A bilingual (Ukrainian/English) HTML guide for structured Senior Android interview preparation.

## Repository layout

- `index.html` — the working guide; this file will evolve through small, reviewable updates.
- `reference/original-guide.html` — immutable baseline copied from the source guide. Do not edit it.
- `reference/original-guide.sha256` — checksum used to verify the baseline has not changed.
- `scripts/validate.py` — dependency-free structural validation for both HTML documents.
- `scripts/browser_smoke_stage*.py` — optional headless (Selenium + Chrome) mobile smoke tests per stage.
- `.github/workflows/pages.yml` — validates the guide and publishes `index.html` to GitHub Pages on every push to `main`.

## Incremental workflow

1. Keep `reference/original-guide.html` unchanged.
2. Make focused content or presentation changes only in `index.html`.
3. Run validation:

   ```bash
   python3 scripts/validate.py
   ```

4. Review the diff, then commit one coherent change at a time.

`index.html` started as an exact copy of the baseline and has since been expanded stage by stage (Stages 1–32).

## Guide structure

Each language view (UK, then EN) contains:

1. An introduction.
2. Stages 1–32, one topic per stage. Topic material lives only in its stage, including a "Практичні нотатки" / "Practice notes" subsection where one exists.
3. Cross-cutting sections after Stage 32: interview answer patterns (UK), the senior edge-case bank, senior in a team, and preparation (with the final checklist and advice).

The sidebar TOC mirrors the major sections. When a section is added or removed, update its TOC entry too; `scripts/validate.py` fails on dangling links.

## Viewing locally

Open `index.html` directly in a browser. No build step or external service is required.

## Viewing online (GitHub Pages)

The `Deploy guide to GitHub Pages` workflow publishes only `index.html` (not the reference baseline or scripts).
One-time setup:

1. GitHub Pages requires a public repository, or a private one on a paid plan (GitHub Pro/Team/Enterprise).
   Note that the published site is public either way (except private Pages on GitHub Enterprise Cloud).
2. In **Settings → Pages**, set **Source** to **GitHub Actions**.
3. Push to `main` or run the workflow manually from the **Actions** tab.

The site is then available at `https://yaroslavromanyuta.github.io/senior-android-interview-guide/`.
