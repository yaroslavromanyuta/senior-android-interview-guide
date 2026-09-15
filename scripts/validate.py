#!/usr/bin/env python3
"""Validate guide structure and baseline integrity using stdlib only."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = (ROOT / "index.html", ROOT / "reference" / "original-guide.html")
CHECKSUM_FILE = ROOT / "reference" / "original-guide.sha256"
MIN_DOCUMENT_BYTES = 1_000
STAGE2_KEY = "kotlin-type-system-state-modeling"
STAGE3_KEY = "advanced-kotlin-jvm"
STAGE4_KEY = "android-tasks-back-stack-deep-links-intents-pending-intent"


def validate_html(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"{path.relative_to(ROOT)}: file is missing"]

    content = path.read_text(encoding="utf-8")
    label = path.relative_to(ROOT)
    if len(content.encode("utf-8")) < MIN_DOCUMENT_BYTES:
        errors.append(f"{label}: document is empty or unexpectedly small")
    if not re.search(r"<title(?:\s[^>]*)?>\s*\S.*?</title>", content, re.I | re.S):
        errors.append(f"{label}: non-empty HTML title is missing")
    for language in ("uk", "en"):
        if not re.search(rf'data-lang=["\']{language}["\']', content, re.I):
            errors.append(f"{label}: {language!r} language view is missing")
    return errors


def validate_baseline_checksum() -> list[str]:
    baseline = ROOT / "reference" / "original-guide.html"
    if not CHECKSUM_FILE.is_file():
        return ["reference/original-guide.sha256: checksum file is missing"]
    fields = CHECKSUM_FILE.read_text(encoding="ascii").strip().split()
    if not fields:
        return ["reference/original-guide.sha256: checksum is empty"]
    expected = fields[0].lower()
    actual = hashlib.sha256(baseline.read_bytes()).hexdigest()
    if actual != expected:
        return ["reference/original-guide.html: immutable baseline checksum mismatch"]
    return []


def validate_index_structure() -> list[str]:
    """Check stable navigation contracts without coupling to prose."""
    content = (ROOT / "index.html").read_text(encoding="utf-8")
    errors: list[str] = []

    ids = re.findall(r'\bid=["\']([^"\']+)["\']', content, re.I)
    duplicate_ids = sorted({value for value in ids if ids.count(value) > 1})
    if duplicate_ids:
        errors.append(f"index.html: duplicate ids: {', '.join(duplicate_ids)}")

    id_set = set(ids)
    unresolved = sorted({
        target
        for target in re.findall(r'\bhref=["\']#([^"\']+)["\']', content, re.I)
        if target not in id_set
    })
    if unresolved:
        errors.append(f"index.html: unresolved internal hashes: {', '.join(unresolved)}")

    for stage_number, stage_key in ((2, STAGE2_KEY), (3, STAGE3_KEY), (4, STAGE4_KEY)):
        expected_stage_ids = (stage_key, f"en-{stage_key}")
        if content.count(f'data-key="{stage_key}"') != 2:
            errors.append(
                f"index.html: Stage {stage_number} must have one shared data-key per language"
            )
        for stage_id in expected_stage_ids:
            if ids.count(stage_id) != 1:
                errors.append(
                    f"index.html: expected exactly one Stage {stage_number} id {stage_id!r}"
                )
            toc_contract = f'data-target="{stage_id}" href="#{stage_id}"'
            if content.count(toc_contract) != 1:
                errors.append(
                    f"index.html: expected exactly one Stage {stage_number} TOC link for {stage_id!r}"
                )

    for prefix in ("", "en-"):
        ordered_ids = (
            f'{prefix}android-process-lifecycle-state-restoration',
            f'{prefix}{STAGE2_KEY}',
            f'{prefix}{STAGE3_KEY}',
            f'{prefix}{STAGE4_KEY}',
            f'{prefix}kotlin-for-android',
        )
        positions = [content.find(f'id="{value}"') for value in ordered_ids]
        if -1 in positions or positions != sorted(positions):
            errors.append(
                f"index.html: {prefix or 'uk-'}Stages 2–4 must follow Stage 1 and precede Kotlin for Android"
            )

    stage4_contracts = (
        "objective", "mental-model", "internals", "tasks-affinity",
        "documents-multiwindow", "back", "navigation", "intents", "applinks",
        "pendingintent", "notifications", "guarantees", "version-sensitive",
        "tradeoffs", "production-scenario", "review-trap", "adb", "likely-qa",
        "followups", "self-check", "english-skeletons", "answer-30", "answer-2min",
        "sources",
    )
    for prefix in ("stage4-uk-", "en-stage4-"):
        for suffix in stage4_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 4 contract id {stage_id!r}")

    for marker in (
        "These are likely practice questions, not a confirmed or guaranteed interview list.",
        "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
        "OnBackInvokedDispatcher", "OnBackPressedDispatcher", "FLAG_IMMUTABLE",
        "Intent.filterEquals()", "pm get-app-links", "onNewIntent()",
    ):
        if marker not in content:
            errors.append(f"index.html: Stage 4 focused contract marker is missing: {marker!r}")

    for prefix in ("stage4-uk-", "en-stage4-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 5)):
            match = re.search(
                rf'id="{re.escape(prefix + suffix)}".*?</h2>.*?<ol>(.*?)</ol>',
                content,
                re.S,
            )
            count = len(re.findall(r"<li>", match.group(1))) if match else 0
            if count != expected:
                errors.append(
                    f"index.html: {prefix + suffix!r} must contain exactly {expected} list items; found {count}"
                )
    return errors


def main() -> int:
    errors: list[str] = []
    for html_file in HTML_FILES:
        errors.extend(validate_html(html_file))
    if (ROOT / "index.html").is_file():
        errors.extend(validate_index_structure())
    if (ROOT / "reference" / "original-guide.html").is_file():
        errors.extend(validate_baseline_checksum())

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Validation passed: HTML basics, unique/resolved anchors, Stage 2–4 navigation/contracts, and baseline checksum are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
