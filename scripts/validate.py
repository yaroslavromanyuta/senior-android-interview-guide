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
STAGE5_KEY = "android-background-execution"
STAGE6_KEY = "android-permissions-storage-notifications"
STAGE7_KEY = "kotlin-coroutines-foundations-internals"
STAGE8_KEY = "kotlin-coroutines-failures-supervision-testing"
STAGE9_KEY = "kotlin-flow-foundations"
STAGE10_KEY = "kotlin-hot-flows-ui-state-events"
STAGE11_KEY = "advanced-kotlin-flow-production"
STAGE12_KEY = "android-ui-architecture-state-modeling"
STAGE13_KEY = "clean-architecture-android-modularization"
STAGE14_KEY = "jetpack-compose-runtime-state"
STAGE15_KEY = "compose-effects-navigation-viewmodel"
STAGE16_KEY = "jetpack-compose-performance"
STAGE17_KEY = "dependency-injection-android"
STAGE18_KEY = "android-networking-fundamentals"
STAGE19_KEY = "authentication-token-refresh-android-mobile-security"
STAGE20_KEY = "local-persistence-sqlite-room-datastore"
STAGE21_KEY = "offline-first-architecture-paging-3"
STAGE22_KEY = "senior-android-testing-strategy"
STAGE23_KEY = "senior-android-reliability-observability"
STAGE24_KEY = "android-memory-threading"
STAGE25_KEY = "startup-rendering-performance"
STAGE26_KEY = "build-release-delivery-engineering"
STAGE27_KEY = "system-design-offline-first-commerce-news-feed"
STAGE28_KEY = "system-design-chat-real-time-updates"
STAGE29_KEY = "system-design-payments-orders"
STAGE30_KEY = "system-design-auth-analytics-feature-flags"
STAGE31_KEY = "migration-design-live-android-product"
STAGE32_KEY = "senior-engineering-practice"


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

    for stage_number, stage_key in (
        (2, STAGE2_KEY), (3, STAGE3_KEY), (4, STAGE4_KEY), (5, STAGE5_KEY),
        (6, STAGE6_KEY), (7, STAGE7_KEY), (8, STAGE8_KEY), (9, STAGE9_KEY),
        (10, STAGE10_KEY), (11, STAGE11_KEY), (12, STAGE12_KEY), (13, STAGE13_KEY),
        (14, STAGE14_KEY), (15, STAGE15_KEY), (16, STAGE16_KEY), (17, STAGE17_KEY),
        (18, STAGE18_KEY), (19, STAGE19_KEY), (20, STAGE20_KEY), (21, STAGE21_KEY),
        (22, STAGE22_KEY), (23, STAGE23_KEY), (24, STAGE24_KEY), (25, STAGE25_KEY),
        (26, STAGE26_KEY), (27, STAGE27_KEY), (28, STAGE28_KEY), (29, STAGE29_KEY),
        (30, STAGE30_KEY), (31, STAGE31_KEY), (32, STAGE32_KEY),
    ):
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
            f'{prefix}{STAGE5_KEY}',
            f'{prefix}{STAGE6_KEY}',
            f'{prefix}{STAGE7_KEY}',
            f'{prefix}{STAGE8_KEY}',
            f'{prefix}{STAGE9_KEY}',
            f'{prefix}{STAGE10_KEY}',
            f'{prefix}{STAGE11_KEY}',
            f'{prefix}{STAGE12_KEY}',
            f'{prefix}{STAGE13_KEY}',
            f'{prefix}{STAGE14_KEY}',
            f'{prefix}{STAGE15_KEY}',
            f'{prefix}{STAGE16_KEY}',
            f'{prefix}{STAGE17_KEY}',
            f'{prefix}{STAGE18_KEY}',
            f'{prefix}{STAGE19_KEY}',
            f'{prefix}{STAGE20_KEY}',
            f'{prefix}{STAGE21_KEY}',
            f'{prefix}{STAGE22_KEY}',
            f'{prefix}{STAGE23_KEY}',
            f'{prefix}{STAGE24_KEY}',
            f'{prefix}{STAGE25_KEY}',
            f'{prefix}{STAGE26_KEY}',
            f'{prefix}{STAGE27_KEY}',
            f'{prefix}{STAGE28_KEY}',
            f'{prefix}{STAGE29_KEY}',
            f'{prefix}{STAGE30_KEY}',
            f'{prefix}{STAGE31_KEY}',
            f'{prefix}{STAGE32_KEY}',
            f'{prefix}kotlin-for-android',
        )
        positions = [content.find(f'id="{value}"') for value in ordered_ids]
        if -1 in positions or positions != sorted(positions):
            errors.append(
                f"index.html: {prefix or 'uk-'}Stages 2–32 must follow Stage 1 and precede Kotlin for Android"
            )

        stage5_id = f"{prefix}{STAGE5_KEY}"
        stage6_id = f"{prefix}{STAGE6_KEY}"
        stage7_id = f"{prefix}{STAGE7_KEY}"
        stage8_id = f"{prefix}{STAGE8_KEY}"
        stage9_id = f"{prefix}{STAGE9_KEY}"
        stage10_id = f"{prefix}{STAGE10_KEY}"
        stage11_id = f"{prefix}{STAGE11_KEY}"
        stage12_id = f"{prefix}{STAGE12_KEY}"
        stage13_id = f"{prefix}{STAGE13_KEY}"
        stage14_id = f"{prefix}{STAGE14_KEY}"
        stage15_id = f"{prefix}{STAGE15_KEY}"
        stage16_id = f"{prefix}{STAGE16_KEY}"
        stage17_id = f"{prefix}{STAGE17_KEY}"
        stage18_id = f"{prefix}{STAGE18_KEY}"
        stage19_id = f"{prefix}{STAGE19_KEY}"
        stage20_id = f"{prefix}{STAGE20_KEY}"
        stage21_id = f"{prefix}{STAGE21_KEY}"
        stage22_id = f"{prefix}{STAGE22_KEY}"
        stage23_id = f"{prefix}{STAGE23_KEY}"
        stage24_id = f"{prefix}{STAGE24_KEY}"
        stage25_id = f"{prefix}{STAGE25_KEY}"
        stage26_id = f"{prefix}{STAGE26_KEY}"
        stage27_id = f"{prefix}{STAGE27_KEY}"
        stage28_id = f"{prefix}{STAGE28_KEY}"
        stage29_id = f"{prefix}{STAGE29_KEY}"
        stage30_id = f"{prefix}{STAGE30_KEY}"
        stage31_id = f"{prefix}{STAGE31_KEY}"
        stage32_id = f"{prefix}{STAGE32_KEY}"
        major_ids = re.findall(
            r'<details\s+class="major-section"[^>]*\bid="([^"]+)"',
            content,
            re.I,
        )
        if (
            stage5_id not in major_ids
            or stage6_id not in major_ids
            or stage7_id not in major_ids
            or stage8_id not in major_ids
            or stage9_id not in major_ids
            or stage10_id not in major_ids
            or stage11_id not in major_ids
            or stage12_id not in major_ids
            or stage13_id not in major_ids
            or stage14_id not in major_ids
            or stage15_id not in major_ids
            or stage16_id not in major_ids
            or stage17_id not in major_ids
            or stage18_id not in major_ids
            or stage19_id not in major_ids
            or stage20_id not in major_ids
            or stage21_id not in major_ids
            or stage22_id not in major_ids
            or stage23_id not in major_ids
            or stage24_id not in major_ids
            or stage25_id not in major_ids
            or stage26_id not in major_ids
            or stage27_id not in major_ids
            or stage28_id not in major_ids
            or stage29_id not in major_ids
            or stage30_id not in major_ids
            or stage31_id not in major_ids
            or stage32_id not in major_ids
            or f"{prefix}kotlin-for-android" not in major_ids
            or major_ids.index(stage6_id) != major_ids.index(stage5_id) + 1
            or major_ids.index(stage7_id) != major_ids.index(stage6_id) + 1
            or major_ids.index(stage8_id) != major_ids.index(stage7_id) + 1
            or major_ids.index(stage9_id) != major_ids.index(stage8_id) + 1
            or major_ids.index(stage10_id) != major_ids.index(stage9_id) + 1
            or major_ids.index(stage11_id) != major_ids.index(stage10_id) + 1
            or major_ids.index(stage12_id) != major_ids.index(stage11_id) + 1
            or major_ids.index(stage13_id) != major_ids.index(stage12_id) + 1
            or major_ids.index(stage14_id) != major_ids.index(stage13_id) + 1
            or major_ids.index(stage15_id) != major_ids.index(stage14_id) + 1
            or major_ids.index(stage16_id) != major_ids.index(stage15_id) + 1
            or major_ids.index(stage17_id) != major_ids.index(stage16_id) + 1
            or major_ids.index(stage18_id) != major_ids.index(stage17_id) + 1
            or major_ids.index(stage19_id) != major_ids.index(stage18_id) + 1
            or major_ids.index(stage20_id) != major_ids.index(stage19_id) + 1
            or major_ids.index(stage21_id) != major_ids.index(stage20_id) + 1
            or major_ids.index(stage22_id) != major_ids.index(stage21_id) + 1
            or major_ids.index(stage23_id) != major_ids.index(stage22_id) + 1
            or major_ids.index(stage24_id) != major_ids.index(stage23_id) + 1
            or major_ids.index(stage25_id) != major_ids.index(stage24_id) + 1
            or major_ids.index(stage26_id) != major_ids.index(stage25_id) + 1
            or major_ids.index(stage27_id) != major_ids.index(stage26_id) + 1
            or major_ids.index(stage28_id) != major_ids.index(stage27_id) + 1
            or major_ids.index(stage29_id) != major_ids.index(stage28_id) + 1
            or major_ids.index(stage30_id) != major_ids.index(stage29_id) + 1
            or major_ids.index(stage31_id) != major_ids.index(stage30_id) + 1
            or major_ids.index(stage32_id) != major_ids.index(stage31_id) + 1
            or major_ids.index(f"{prefix}kotlin-for-android") != major_ids.index(stage32_id) + 1
        ):
            errors.append(
                f"index.html: {stage6_id!r} must immediately follow {stage5_id!r}, "
                f"{stage7_id!r} must immediately follow {stage6_id!r}, and "
                f"{stage8_id!r} must immediately follow {stage7_id!r}, and "
                f"{stage9_id!r} must immediately follow {stage8_id!r}, and "
                f"{stage10_id!r} must immediately follow {stage9_id!r}, and "
                f"{stage11_id!r} must immediately follow {stage10_id!r}, and "
                f"{stage12_id!r} must immediately follow {stage11_id!r}, and "
                f"{stage13_id!r} must immediately follow {stage12_id!r}, and "
                f"{stage14_id!r} must immediately follow {stage13_id!r}, and "
                f"{stage15_id!r} must immediately follow {stage14_id!r}, and "
                f"{stage16_id!r} must immediately follow {stage15_id!r}, and "
                f"{stage17_id!r} must immediately follow {stage16_id!r}, and "
                f"{stage18_id!r} must immediately follow {stage17_id!r}, and "
                f"{stage19_id!r} must immediately follow {stage18_id!r}, and "
                f"{stage20_id!r} must immediately follow {stage19_id!r}, and "
                f"{stage21_id!r} must immediately follow {stage20_id!r}, and "
                f"{stage22_id!r} must immediately follow {stage21_id!r}, and "
                f"{stage23_id!r} must immediately follow {stage22_id!r}, and "
                f"{stage24_id!r} must immediately follow {stage23_id!r}, and "
                f"{stage25_id!r} must immediately follow {stage24_id!r}, and "
                f"{stage26_id!r} must immediately follow {stage25_id!r}, and "
                f"{stage27_id!r} must immediately follow {stage26_id!r}, and "
                f"{stage28_id!r} must immediately follow {stage27_id!r}, and "
                f"{stage29_id!r} must immediately follow {stage28_id!r}, and "
                f"{stage30_id!r} must immediately follow {stage29_id!r}, and "
                f"{stage31_id!r} must immediately follow {stage30_id!r}, and "
                f"final Stage 32 {stage32_id!r} must immediately follow {stage31_id!r} and precede Kotlin for Android"
            )

        toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage5_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage6_id)}"[^>]*>',
            content,
            re.S,
        )
        if not toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage6_id!r} must be immediately after {stage5_id!r}"
            )

        stage7_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage6_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage7_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage7_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage7_id!r} must be immediately after {stage6_id!r}"
            )

        stage8_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage7_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage8_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage8_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage8_id!r} must be immediately after {stage7_id!r}"
            )

        stage9_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage8_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage9_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage9_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage9_id!r} must be immediately after {stage8_id!r}"
            )

        stage10_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage9_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage10_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage10_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage10_id!r} must be immediately after {stage9_id!r}"
            )

        stage11_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage10_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage11_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage11_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage11_id!r} must be immediately after {stage10_id!r}"
            )

        stage12_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage11_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage12_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage12_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage12_id!r} must be immediately after {stage11_id!r}"
            )

        stage13_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage12_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage13_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage13_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage13_id!r} must be immediately after {stage12_id!r}"
            )

        stage14_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage13_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage14_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage14_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage14_id!r} must be immediately after {stage13_id!r}"
            )

        stage15_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage14_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage15_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage15_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage15_id!r} must be immediately after {stage14_id!r}"
            )

        stage16_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage15_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage16_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage16_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage16_id!r} must be immediately after {stage15_id!r}"
            )

        stage17_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage16_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage17_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage17_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage17_id!r} must be immediately after {stage16_id!r}"
            )

        stage18_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage17_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage18_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage18_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage18_id!r} must be immediately after {stage17_id!r}"
            )

        stage19_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage18_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage19_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage19_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage19_id!r} must be immediately after {stage18_id!r}"
            )

        stage20_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage19_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage20_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage20_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage20_id!r} must be immediately after {stage19_id!r}"
            )

        stage21_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage20_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage21_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage21_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage21_id!r} must be immediately after {stage20_id!r}"
            )

        stage22_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage21_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage22_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage22_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage22_id!r} must be immediately after {stage21_id!r}"
            )

        stage23_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage22_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage23_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage23_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage23_id!r} must be immediately after {stage22_id!r}"
            )

        stage24_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage23_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage24_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage24_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage24_id!r} must be immediately after {stage23_id!r}"
            )

        stage25_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage24_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage25_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage25_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage25_id!r} must be immediately after {stage24_id!r}"
            )

        stage26_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage25_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage26_id)}"[^>]*>',
            content,
            re.S,
        )
        if not stage26_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage26_id!r} must be immediately after {stage25_id!r}"
            )

        stage27_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage26_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage27_id)}"[^>]*>',
            content, re.S,
        )
        if not stage27_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage27_id!r} must be immediately after {stage26_id!r}"
            )

        stage28_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage27_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage28_id)}"[^>]*>',
            content, re.S,
        )
        if not stage28_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage28_id!r} must be immediately after {stage27_id!r}"
            )

        stage29_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage28_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage29_id)}"[^>]*>',
            content, re.S,
        )
        if not stage29_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage29_id!r} must be immediately after {stage28_id!r}"
            )

        stage30_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage29_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage30_id)}"[^>]*>',
            content, re.S,
        )
        if not stage30_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage30_id!r} must be immediately after {stage29_id!r}"
            )

        stage31_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage30_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage31_id)}"[^>]*>',
            content, re.S,
        )
        if not stage31_toc_adjacency:
            errors.append(
                f"index.html: TOC link {stage31_id!r} must be immediately after {stage30_id!r}"
            )

        stage32_toc_adjacency = re.search(
            rf'<li class="toc-major">\s*<a data-target="{re.escape(stage31_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(stage32_id)}"[^>]*>.*?</a>\s*'
            rf'</li>\s*<li class="toc-major">\s*<a data-target="{re.escape(prefix + "kotlin-for-android")}"[^>]*>',
            content, re.S,
        )
        if not stage32_toc_adjacency:
            errors.append(
                f"index.html: final TOC link {stage32_id!r} must be immediately after {stage31_id!r} and before Kotlin for Android"
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

    stage5_contracts = (
        "objective", "mental-model", "internals", "services", "broadcasts",
        "workmanager", "fgs", "alarms", "guarantees", "version-sensitive",
        "decision-framework", "tradeoffs", "production-scenario", "review-trap",
        "testing", "likely-qa", "followups", "self-check", "english-skeletons",
        "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage5-uk-", "en-stage5-"):
        for suffix in stage5_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 5 contract id {stage_id!r}")

    for marker in (
        "These are likely practice questions, not a confirmed or guaranteed interview list.",
        "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
        "RECEIVER_NOT_EXPORTED", "goAsync()", "APPEND_OR_REPLACE",
        "MAX_DATA_BYTES = 10,240", "ForegroundServiceStartNotAllowedException",
        "canScheduleExactAlarms()", "user-initiated data transfer",
        "at-least-once-like", "adb shell dumpsys jobscheduler",
    ):
        if marker not in content:
            errors.append(f"index.html: Stage 5 focused contract marker is missing: {marker!r}")

    for prefix in ("stage5-uk-", "en-stage5-"):
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

    stage6_contracts = (
        "objective", "mental-model", "internals", "permissions-state",
        "activity-results", "location", "capability-evolution", "notifications",
        "storage", "visibility-sharing", "guarantees", "version-matrix",
        "decision-framework", "tradeoffs", "production-scenario", "review-trap",
        "testing", "likely-qa", "followups", "self-check", "english-skeletons",
        "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage6-uk-", "en-stage6-"):
        for suffix in stage6_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 6 contract id {stage_id!r}")

    stage6_sections: dict[str, str] = {}
    for stage_id in (STAGE6_KEY, f"en-{STAGE6_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage6_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 6 section {stage_id!r}")

    common_stage6_markers = (
        "READ_MEDIA_VISUAL_USER_SELECTED", "POST_NOTIFICATIONS",
        "QUERY_ALL_PACKAGES", "FLAG_GRANT_READ_URI_PERMISSION",
        "adb shell cmd appops get", "ActivityResultContracts.RequestMultiplePermissions",
        "ACCESS_BACKGROUND_LOCATION", "NEARBY_WIFI_DEVICES", "MANAGE_EXTERNAL_STORAGE",
    )
    language_markers = {
        STAGE6_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "shouldShowRequestPermissionRationale()</code> не є повним oracle постійної відмови",
            "permission/channel/URI можуть змінитися поза app",
            "channels persist, і app не може підняти importance, яку user знизив",
            "File paths і document URIs не взаємозамінні",
            "Не приписуйте універсальну OEM-поведінку Android platform",
        ),
        f"en-{STAGE6_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "shouldShowRequestPermissionRationale()</code> is not a complete permanent-denial oracle",
            "Permissions can change outside the app",
            "channels persist, and an app cannot raise importance that the user lowered",
            "File paths and document URIs are not interchangeable",
            "Do not present any OEM behavior as universal Android behavior",
        ),
    }
    for stage_id, section in stage6_sections.items():
        for marker in (*common_stage6_markers, *language_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 6 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage6-uk-", "en-stage6-"):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage7_contracts = (
        "objective", "mental-model", "internals", "continuation", "job-builders",
        "dispatchers", "cancellation", "android-ownership", "bridging", "guarantees",
        "version-sensitive", "decision-framework", "tradeoffs", "production-scenario",
        "review-trap", "likely-qa", "followups", "self-check", "english-skeletons",
        "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage7-uk-", "en-stage7-"):
        for suffix in stage7_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 7 contract id {stage_id!r}")

    stage7_sections: dict[str, str] = {}
    for stage_id in (STAGE7_KEY, f"en-{STAGE7_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage7_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 7 section {stage_id!r}")

    common_stage7_markers = (
        "Continuation&lt;T&gt;", "CoroutineContext", "Main.immediate",
        "limitedParallelism", "suspendCancellableCoroutine", "NonCancellable",
        "repeatOnLifecycle", "ThreadLocal.asContextElement", "runBlocking",
        "-Dkotlinx.coroutines.debug", "GlobalScope",
    )
    language_stage7_markers = {
        STAGE7_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "Coroutine — не thread", "suspend</code> саме по собі не переносить роботу з main",
            "Cancellation is <strong>cooperative</strong>",
            "не гарантія DB transaction, exactly-once network effect чи business atomicity",
        ),
        f"en-{STAGE7_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "A coroutine is not a thread", "suspend</code> does not automatically move work off main",
            "Cancellation is <strong>cooperative</strong>",
            "does not guarantee database transactions, exactly-once network effects, or business atomicity",
        ),
    }
    for stage_id, section in stage7_sections.items():
        for marker in (*common_stage7_markers, *language_stage7_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 7 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage7-uk-", "en-stage7-"):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage8_contracts = (
        "objective", "mental-model", "internals", "builder-propagation", "supervision",
        "cancellation-cleanup", "timeouts-callback-flow", "flow-boundaries", "guarantees",
        "version-sensitive", "decision-test-framework", "deterministic-testing",
        "android-testing", "debugging", "tradeoffs", "production-scenario", "review-trap",
        "likely-qa", "followups", "self-check", "english-skeletons", "answer-30",
        "answer-2min", "sources",
    )
    for prefix in ("stage8-uk-", "en-stage8-"):
        for suffix in stage8_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 8 contract id {stage_id!r}")

    stage8_sections: dict[str, str] = {}
    for stage_id in (STAGE8_KEY, f"en-{STAGE8_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage8_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 8 section {stage_id!r}")

    common_stage8_markers = (
        "CoroutineExceptionHandler", "SupervisorJob", "supervisorScope", "CancellationException",
        "NonCancellable", "withTimeoutOrNull", "callbackFlow", "awaitClose", "runTest",
        "TestScope", "StandardTestDispatcher", "UnconfinedTestDispatcher", "TestCoroutineScheduler",
        "Dispatchers.setMain", "Dispatchers.resetMain", "backgroundScope", "advanceTimeBy",
        "runCurrent", "advanceUntilIdle", "CoroutineName", "DebugProbes", "Turbine",
    )
    language_stage8_markers = {
        STAGE8_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "supervisor ізолює propagation failure дитини, але не report-ить і не handle-ить її автоматично",
            "Virtual time пропускає сумісні delays, а не реальний blocking/I/O",
            "runTest</code> не робить production races неможливими",
            "Flow content навмисно вузький; повна модель Flow належить Stages 9–11",
        ),
        f"en-{STAGE8_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "A supervisor isolates child-failure propagation; it does not report or handle the failure automatically",
            "Virtual time skips compatible delays, not real blocking or I/O",
            "runTest</code> does not make production races impossible",
            "Flow coverage is deliberately narrow; the broader Flow model belongs to Stages 9–11",
        ),
    }
    for stage_id, section in stage8_sections.items():
        for marker in (*common_stage8_markers, *language_stage8_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 8 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage8-uk-", "en-stage8-"):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage9_contracts = (
        "objective", "mental-model", "internals", "builders-sequential", "context",
        "operators", "rate-mismatch", "callbacks", "lifecycle", "exposure-ownership",
        "guarantees", "version-sensitive", "decision-framework", "tradeoffs",
        "production-scenario", "review-trap", "testing", "likely-qa", "followups",
        "self-check", "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage9-uk-", "en-stage9-"):
        for suffix in stage9_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 9 contract id {stage_id!r}")

    stage9_sections: dict[str, str] = {}
    for stage_id in (STAGE9_KEY, f"en-{STAGE9_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage9_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 9 section {stage_id!r}")

    common_stage9_markers = (
        "flowOf", "asFlow", "exception transparency", "flowOn", "collectLatest",
        "distinctUntilChanged", "ProducerScope", "trySend", "awaitClose",
        "repeatOnLifecycle", "flowWithLifecycle", "collectAsStateWithLifecycle",
        "StateFlow", "SharedFlow", "Channel", "Reactive Streams", "exactly-once",
    )
    language_stage9_markers = {
        STAGE9_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "cold не означає background, caching або single execution",
            "Flow does not cache by default",
            "intermediate <strong>values are dropped</strong>",
            "належить Stage 10, а advanced combine/flatten/retry composition — Stage 11",
        ),
        f"en-{STAGE9_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "Cold does not mean background, cached, or single execution",
            "Flow does not cache by default",
            "intermediate <strong>values are dropped</strong>",
            "is reserved for Stage 10; advanced combine, flattening, and retry composition is reserved for Stage 11",
        ),
    }
    for stage_id, section in stage9_sections.items():
        for marker in (*common_stage9_markers, *language_stage9_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 9 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage9-uk-", "en-stage9-"):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage10_contracts = (
        "objective", "mental-model", "internals", "stateflow", "sharedflow", "sharing",
        "channel", "guarantees", "version-sensitive", "decision-matrix", "tradeoffs",
        "production-scenario", "review-trap", "testing", "likely-qa", "followups",
        "self-check", "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage10-uk-", "en-stage10-"):
        for suffix in stage10_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 10 contract id {stage_id!r}")

    stage10_sections: dict[str, str] = {}
    for stage_id in (STAGE10_KEY, f"en-{STAGE10_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage10_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 10 section {stage_id!r}")

    common_stage10_markers = (
        "updateAndGet", "getAndUpdate", "extraBufferCapacity", "onBufferOverflow",
        "subscriptionCount", "resetReplayCache", "replayExpirationMillis", "Eagerly",
        "Lazily", "WhileSubscribed", "RENDEZVOUS", "BUFFERED", "CONFLATED", "UNLIMITED",
        "trySend", "onUndeliveredElement", "receiveAsFlow", "consumeAsFlow",
        "repeatOnLifecycle", "collectAsStateWithLifecycle", "SavedStateHandle",
        "No primitive alone", "process death", "exactly-once",
    )
    language_stage10_markers = {
        STAGE10_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "StateFlow не event queue", "Replay — memory cache, не durable storage",
            "Receive не означає", "upstream може restart-нути",
        ),
        f"en-{STAGE10_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "StateFlow is therefore not an event queue", "Replay is an in-memory cache, not durable storage",
            "Receive does not mean", "upstream can restart",
        ),
    }
    for stage_id, section in stage10_sections.items():
        for marker in (*common_stage10_markers, *language_stage10_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 10 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage10-uk-", "en-stage10-"):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage11_contracts = (
        "objective", "mental-model", "internals", "composition", "latest-search",
        "multi-source", "errors-retry", "sharing-cache", "fusion-concurrency",
        "callbacks-lifecycle", "guarantees", "version-sensitive", "decision-framework",
        "tradeoffs", "production-scenario", "review-trap", "testing-observability",
        "likely-qa", "followups", "self-check", "english-skeletons", "answer-30",
        "answer-2min", "sources",
    )
    for prefix in ("stage11-uk-", "en-stage11-"):
        for suffix in stage11_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 11 contract id {stage_id!r}")

    stage11_sections: dict[str, str] = {}
    for stage_id in (STAGE11_KEY, f"en-{STAGE11_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage11_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 11 section {stage_id!r}")

    common_stage11_markers = (
        "combine", "zip", "merge", "flatMapLatest", "flatMapConcat", "flatMapMerge",
        "transformLatest", "mapLatest", "debounce", "distinctUntilChanged", "catch",
        "onCompletion", "retryWhen", "CancellationException", "stateIn", "shareIn",
        "replayExpirationMillis", "callbackFlow", "awaitClose", "flatMapMerge(concurrency",
        "TestCoroutineScheduler", "repeatOnLifecycle", "exactly-once",
    )
    language_stage11_markers = {
        STAGE11_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "combine чекає перше значення від кожного input",
            "catch не ловить failures downstream collector",
            "latest-оператори скасовують cooperative",
            "Replay hot sharing — не durable cache",
        ),
        f"en-{STAGE11_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "combine waits for the first value from every input",
            "catch does not catch downstream collector failures",
            "latest operators cancel cooperatively",
            "Hot-sharing replay is not a durable cache",
        ),
    }
    for stage_id, section in stage11_sections.items():
        for marker in (*common_stage11_markers, *language_stage11_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 11 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage11-uk-", "en-stage11-"):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage12_contracts = (
        "objective", "mental-model", "state-taxonomy", "state-shape", "ownership",
        "udf-events-effects", "concurrency", "guarantees", "version-sensitive",
        "decision-matrix", "tradeoffs", "production-scenario", "review-trap",
        "testing-observability", "likely-qa", "followups", "self-check",
        "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage12-uk-", "en-stage12-"):
        for suffix in stage12_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 12 contract id {stage_id!r}")

    stage12_sections: dict[str, str] = {}
    for stage_id in (STAGE12_KEY, f"en-{STAGE12_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage12_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 12 section {stage_id!r}")

    common_stage12_markers = (
        "MVVM", "MVI", "UDF", "StateFlow is not an event queue", "SavedStateHandle",
        "collectAsStateWithLifecycle()", "repeatOnLifecycle", "rememberSaveable", "requestId",
        "source of truth", "process death", "idempotency", "MutableStateFlow.update",
    )
    language_stage12_markers = {
        STAGE12_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "UDF does not inherently serialize async effects",
            "Immutable data does not make nested mutable members safe",
            "ViewModel survives process death",
            "SavedStateHandle</code> retains small restorable values",
            "One UI state object is always superior",
            "Architecture pattern names guarantee separation",
        ),
        f"en-{STAGE12_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "UDF does not inherently serialize async effects",
            "Immutable data does not make nested mutable members safe",
            "ViewModel survives process death",
            "SavedStateHandle</code> retains small restorable values",
            "One UI state object is always superior",
            "Architecture pattern names guarantee separation",
        ),
    }
    for stage_id, section in stage12_sections.items():
        for marker in (*common_stage12_markers, *language_stage12_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 12 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage12-uk-", "en-stage12-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage13_contracts = (
        "objective", "mental-model", "dependency-graph", "layers-models", "inversion-use-cases",
        "packages-modules", "module-types", "boundaries", "build-ownership", "guarantees",
        "version-sensitive", "decision-framework", "tradeoffs", "production-migration",
        "review-trap", "fitness-rules", "likely-qa", "followups", "self-check",
        "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage13-uk-", "en-stage13-"):
        for suffix in stage13_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 13 contract id {stage_id!r}")

    stage13_sections: dict[str, str] = {}
    for stage_id in (STAGE13_KEY, f"en-{STAGE13_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage13_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 13 section {stage_id!r}")

    common_stage13_markers = (
        "dependency rule", "policy", "mechanism", "presentation", "domain", "data",
        "DTO", "UI model", "repository interface", "package-by-feature", "package-by-layer",
        "Gradle module", "api", "implementation", "Kotlin/JVM", "dynamic feature",
        "fan-out", "navigation contract", "convention plugin", "strangler", "fitness",
    )
    language_stage13_markers = {
        STAGE13_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "Немає обов’язкової кількості шарів", "Repository не є автоматично domain abstraction",
            "Interfaces alone do not decouple", "Modules do not guarantee runtime isolation or security",
            "Modularization does not guarantee quality or build speed",
        ),
        f"en-{STAGE13_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "There is no mandated layer count", "A repository is not automatically a domain abstraction",
            "Interfaces alone do not decouple", "Modules do not guarantee runtime isolation or security",
            "Modularization does not guarantee quality or build speed",
        ),
    }
    for stage_id, section in stage13_sections.items():
        for marker in (*common_stage13_markers, *language_stage13_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 13 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage13-uk-", "en-stage13-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage14_contracts = (
        "objective", "mental-model", "runtime-topology", "snapshots", "phases",
        "state-authoring", "persistence", "hoisting", "derived-policies",
        "identity-lifecycle", "compiler-interop", "guarantees", "version-sensitive",
        "decision-framework", "tradeoffs", "production-scenario", "review-trap",
        "likely-qa", "followups", "self-check", "english-skeletons", "answer-30",
        "answer-2min", "sources",
    )
    for prefix in ("stage14-uk-", "en-stage14-"):
        for suffix in stage14_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 14 contract id {stage_id!r}")

    stage14_sections: dict[str, str] = {}
    for stage_id in (STAGE14_KEY, f"en-{STAGE14_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage14_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 14 section {stage_id!r}")

    common_stage14_markers = (
        "slot table", "positional", "restart scope", "initial composition", "recomposition",
        "snapshot", "mutable snapshot", "conflict", "Composition", "Layout", "Draw",
        "mutableStateOf", "mutableStateListOf", "MutableList", "rememberSaveable",
        "SaveableStateRegistry", "Saver", "mapSaver", "listSaver", "ViewModel",
        "lowest", "plain state holder", "derivedStateOf", "snapshotFlow",
        "structuralEqualityPolicy", "referentialEqualityPolicy", "neverEqualPolicy",
        "key(item.id)", "Composer", "@Stable", "collectAsStateWithLifecycle",
        "idempotent", "side-effect-free", "Stage 15", "Stage 16",
    )
    language_stage14_markers = {
        STAGE14_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "не durable storage", "може виконатися повторно", "бути пропущений або скасований",
        ),
        f"en-{STAGE14_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "not durable storage", "run in a different order", "be skipped, or be cancelled",
        ),
    }
    for stage_id, section in stage14_sections.items():
        for marker in (*common_stage14_markers, *language_stage14_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 14 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage14-uk-", "en-stage14-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage15_contracts = (
        "objective", "mental-model", "topology", "effects", "keys-snapshotflow",
        "lifecycle-collection", "route-content", "viewmodel-scoping", "savedstate",
        "navigation-stack", "outcomes", "guarantees", "version-sensitive",
        "decision-framework", "tradeoffs", "production-scenario", "review-trap",
        "testing", "likely-qa", "followups", "self-check", "english-skeletons",
        "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage15-uk-", "en-stage15-"):
        for suffix in stage15_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 15 contract id {stage_id!r}")

    stage15_sections: dict[str, str] = {}
    for stage_id in (STAGE15_KEY, f"en-{STAGE15_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage15_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 15 section {stage_id!r}")

    common_stage15_markers = (
        "SideEffect", "LaunchedEffect", "DisposableEffect", "rememberCoroutineScope",
        "rememberUpdatedState", "produceState", "snapshotFlow", "semantic", "cooperative",
        "abandoned", "collectAsStateWithLifecycle", "stateless", "ViewModelStoreOwner",
        "CreationExtras", "createSavedStateHandle", "hiltViewModel", "SavedStateHandle",
        "NavHost", "NavController", "back-stack", "composable&lt;T&gt;", "toRoute&lt;T&gt;",
        "popUpTo", "inclusive", "launchSingleTop", "saveState", "restoreState",
        "multiple back stacks", "Deep links are untrusted", "SharedFlow", "Channel",
        "durable exactly-once", "process death", "TestNavHostController", "ComposeNavigator",
        "Navigation 3", "Stage 17",
    )
    language_stage15_markers = {
        STAGE15_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "ViewModel survives configuration change, але не process death",
            "Key controls restart, not “handled once forever”",
            "NavController</code> destination на source of truth",
        ),
        f"en-{STAGE15_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "A ViewModel survives configuration change of its owner, not process death",
            "A key controls restart, not “handled once forever.”",
            "NavController</code> destination into the source of truth",
        ),
    }
    for stage_id, section in stage15_sections.items():
        for marker in (*common_stage15_markers, *language_stage15_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 15 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage15-uk-", "en-stage15-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage16_contracts = (
        "objective", "mental-model", "topology", "evidence", "recomposition-stability",
        "phases-caching", "lazy-layout", "rendering-animation", "guarantees",
        "version-sensitive", "decision-framework", "tradeoffs", "production-scenario",
        "review-trap", "testability", "likely-qa", "followups", "self-check",
        "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage16-uk-", "en-stage16-"):
        for suffix in stage16_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 16 contract id {stage_id!r}")

    stage16_sections: dict[str, str] = {}
    for stage_id in (STAGE16_KEY, f"en-{STAGE16_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage16_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 16 section {stage_id!r}")

    common_stage16_markers = (
        "Macrobenchmark", "Microbenchmark", "Perfetto", "System Trace", "Layout Inspector",
        "Compose compiler reports", "JankStats", "restartable", "skippable", "strong skipping",
        "Kotlin 2.0.20+", "@Stable", "@Immutable", "immutable collections",
        "stability configuration", "instance", "lambda", "block-form", "provider",
        "composition→composition", "layout→composition", "derivedStateOf", "remember(keys)",
        "contentType", "Paging", "SubcomposeLayout", "Intrinsic", "graphicsLayer",
        "image", "overdraw", "animation", "release/profileable", "Baseline Profile",
        "Stage 25", "representative", "warmup", "regression budget", "debug builds",
        "keys preserve identity but do not guarantee zero recomposition",
    )
    language_stage16_markers = {
        STAGE16_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "Менше recompositions не обов’язково означає швидші frames",
            "stable annotations не роблять mutable data safe",
            "remember не робить expensive work free",
            "більше modules/abstractions тут irrelevant",
        ),
        f"en-{STAGE16_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "Fewer recompositions do not necessarily mean faster frames",
            "stable annotations do not make mutable data safe",
            "remember does not make expensive work free",
            "more modules/abstractions are irrelevant",
        ),
    }
    for stage_id, section in stage16_sections.items():
        for marker in (*common_stage16_markers, *language_stage16_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 16 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage16-uk-", "en-stage16-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage17_contracts = (
        "objective", "mental-model", "graph-internals", "lifecycle-topology", "bindings",
        "advanced-bindings", "viewmodel-compose", "modules", "testing", "runtime-assisted",
        "startup-resources", "guarantees", "version-sensitive", "decision-framework",
        "tradeoffs", "production-scenario", "review-trap", "observability", "likely-qa",
        "followups", "self-check", "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage17-uk-", "en-stage17-"):
        for suffix in stage17_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 17 contract id {stage_id!r}")

    stage17_sections: dict[str, str] = {}
    for stage_id in (STAGE17_KEY, f"en-{STAGE17_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage17_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 17 section {stage_id!r}")

    common_stage17_markers = (
        "dependency inversion", "dependency injection", "service locator", "constructor injection",
        "composition root", "Dagger", "generated factories", "Provider", "@Inject", "@Binds",
        "@Provides", "qualifier", "multibinding", "Lazy", "SingletonComponent",
        "ActivityRetainedComponent", "ViewModelComponent", "ActivityComponent", "FragmentComponent",
        "ViewComponent", "ServiceComponent", "SavedStateHandle", "@HiltViewModel", "Compose",
        "KSP", "KAPT", "Gradle", "assisted injection", "captive dependency", "thread safety",
        "component dependencies", "subcomponents", "test module replacement", "third-party SDK",
        "Compile-time graph validation does not validate runtime business configuration",
        "Lazy/Provider break eager construction but can hide cycles",
        "Test module replacement does not prove production wiring",
    )
    language_stage17_markers = {
        STAGE17_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "DI не створює architectural separation або testability автоматично",
            "Hilt ViewModel scope слідує за ViewModel instance, а не navigation destination магічно",
            "singleton є один на generated component/process instance, не cross-process і не durable global singleton",
        ),
        f"en-{STAGE17_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "DI does not create architectural separation or testability automatically",
            "Hilt ViewModel scope follows the ViewModel instance, not a navigation destination by magic",
            "singleton is per generated component/process instance, not a cross-process or durable global singleton",
        ),
    }
    for stage_id, section in stage17_sections.items():
        for marker in (*common_stage17_markers, *language_stage17_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 17 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage17-uk-", "en-stage17-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage18_contracts = (
        "objective", "mental-model", "topology", "interceptors", "execution",
        "http-semantics", "cache", "timeouts-retries", "bodies-serialization",
        "pagination-connectivity-security", "errors-observability", "guarantees",
        "version-sensitive", "decision-framework", "tradeoffs", "production-scenario",
        "review-trap", "testing", "likely-qa", "followups", "self-check",
        "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage18-uk-", "en-stage18-"):
        for suffix in stage18_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 18 contract id {stage_id!r}")

    stage18_sections: dict[str, str] = {}
    for stage_id in (STAGE18_KEY, f"en-{STAGE18_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage18_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 18 section {stage_id!r}")

    common_stage18_markers = (
        "Retrofit", "Converter", "CallAdapter", "RealCall", "Dispatcher", "application interceptor",
        "network interceptor", "connection", "DNS", "route", "socket", "TLS", "Authenticator",
        "execute()", "suspend", "cancellation", "safe", "idempotent", "2xx", "Content-Type",
        "Cache-Control", "ETag", "If-None-Match", "Last-Modified", "Vary", "304 Not Modified",
        "connect timeout", "read timeout", "write timeout", "call timeout", "Retry-After",
        "backoff", "jitter", "one-shot", "ResponseBody", "unknown", "missing", "null",
        "pagination", "cursor", "NetworkCallback", "Network Security Config", "transport",
        "protocol", "parsing", "domain", "EventListener", "correlation ID", "MockWebServer",
        "contract tests", "Stage 19", "Stage 21",
    )
    language_stage18_markers = {
        STAGE18_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "2xx може містити domain failure", "Retry не гарантує success або exactly-once",
            "не може відкрутити request, який server уже обробив",
            "GET safety/idempotency — protocol semantics, не доказ",
            "OkHttp cache obeys HTTP rules and is not repository persistence",
            "Retrofit does not move every adapter or arbitrary custom code off the main thread by magic",
            "Timeouts are not end-to-end business deadlines automatically",
            "DNS result або connectivity callback не гарантує internet чи backend reachability",
        ),
        f"en-{STAGE18_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "A 2xx response may still contain a domain failure",
            "A retry guarantees neither success nor exactly-once processing",
            "cannot undo a request that the server has already processed",
            "GET safety and idempotency are protocol semantics, not proof",
            "OkHttp cache obeys HTTP rules and is not repository persistence",
            "Retrofit does not move work off the main thread by magic for every adapter",
            "Timeouts are not end-to-end business deadlines automatically",
            "DNS result or connectivity callback does not guarantee internet or backend reachability",
        ),
    }
    for stage_id, section in stage18_sections.items():
        for marker in (*common_stage18_markers, *language_stage18_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 18 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage18-uk-", "en-stage18-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage19_contracts = (
        "objective", "mental-model", "topology", "oauth-oidc", "native-flow",
        "redirect-boundaries", "token-lifecycle", "okhttp-boundaries", "concurrent-refresh",
        "retry-logout-semantics", "storage", "transport-pinning", "platform-boundaries",
        "integrity-replay-time", "observability-response", "guarantees", "version-sensitive",
        "decision-framework", "tradeoffs", "production-scenario", "review-trap", "testing",
        "likely-qa", "followups", "self-check", "english-skeletons", "answer-30",
        "answer-2min", "sources",
    )
    for prefix in ("stage19-uk-", "en-stage19-"):
        for suffix in stage19_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 19 contract id {stage_id!r}")

    stage19_sections: dict[str, str] = {}
    for stage_id in (STAGE19_KEY, f"en-{STAGE19_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage19_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 19 section {stage_id!r}")

    common_stage19_markers = (
        "OAuth 2", "OIDC", "authorization server", "resource server", "access token",
        "refresh token", "ID token", "Authorization Code", "PKCE", "external user-agent",
        "state", "nonce", "redirect URI", "App Link", "rotation", "revocation",
        "Interceptor", "Authenticator", "401", "403", "single-flight", "Mutex", "Deferred",
        "version", "generation", "idempotency", "replayable", "Android Keystore", "biometric",
        "backup", "screenshot", "clipboard", "analytics", "Network Security Config", "cleartext",
        "certificate pinning", "backup pins", "WebView", "Custom Tabs", "PendingIntent",
        "Play Integrity", "device clock", "offline", "remote revocation", "incident response",
        "Stage 18",
    )
    language_stage19_markers = {
        STAGE19_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "PKCE зменшує ризик перехоплення authorization code, але не усуває весь phishing або compromise пристрою.",
            "HTTPS автентифікує transport endpoint у межах trust model, але не доводить business correctness.",
            "Pinning не захищає compromised app/process і може повністю зламати connectivity.",
            "Keystore не робить token недоступним після того, як app легітимно decrypt/use його.",
            "Refresh serialization не створює exactly-once server effects.",
            "Logout не може відкликати requests, які server уже обробив.",
            "401 не завжди означає, що треба refresh.",
            "Mobile client не може безпечно вбудувати universal secret.",
            "Biometric success сам по собі не автентифікує backend session.",
        ),
        f"en-{STAGE19_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "PKCE mitigates authorization-code interception but not all phishing or device compromise.",
            "HTTPS authenticates the transport endpoint under its trust model, not business correctness.",
            "Pinning does not protect a compromised app or process and can brick connectivity.",
            "Keystore does not make a token inaccessible after the app legitimately decrypts or uses it.",
            "Refresh serialization does not create exactly-once server effects.",
            "Logout cannot retract requests the server already processed.",
            "A 401 does not always mean refresh.",
            "A mobile client cannot safely embed a universal secret.",
            "Biometric success does not authenticate a backend session by itself.",
        ),
    }
    for stage_id, section in stage19_sections.items():
        for marker in (*common_stage19_markers, *language_stage19_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 19 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage19-uk-", "en-stage19-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage20_contracts = (
        "objective", "mental-model", "topology", "sqlite-journals", "schema-modeling",
        "transactions", "room-reactive", "relations-batching", "migrations",
        "operational-recovery", "datastore", "boundaries", "guarantees",
        "version-sensitive", "decision-framework", "tradeoffs", "production-scenario",
        "review-trap", "testing", "likely-qa", "followups", "self-check",
        "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage20-uk-", "en-stage20-"):
        for suffix in stage20_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 20 contract id {stage_id!r}")

    stage20_sections: dict[str, str] = {}
    for stage_id in (STAGE20_KEY, f"en-{STAGE20_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage20_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 20 section {stage_id!r}")

    common_stage20_markers = (
        "SQLite", "page", "connection", "rollback journal", "WAL", "checkpoint", "ACID",
        "Room", "DAO", "generated", "compile-time", "type converter", "primary key",
        "unique", "foreign key", "cascade", "composite index", "selectivity", "EXPLAIN QUERY PLAN",
        "normalization", "denormalized", "@Transaction", "suspend", "network I/O", "upsert",
        "Flow", "invalidation", "query rerun", "cancellation", "junction", "N+1", "SQLite variable",
        "pagination", "Stage 21", "exportSchema", "AutoMigration", "RenameColumn", "DeleteColumn",
        "MigrationTestHelper", "identity hash", "prepackaged", "fallbackToDestructiveMigration",
        "multi-process", "corruption", "disk-full", "backup", "encryption", "Preferences DataStore",
        "Proto DataStore", "updateData", "CorruptionHandler", "SharedPreferencesMigration", "apply()",
        "commit()", "single source of truth",
    )
    language_stage20_markers = {
        STAGE20_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "DB transaction не є атомарною network+DB transaction.",
            "WAL не означає кілька одночасних writers.",
            "Room Flow не повідомляє точні змінені rows.",
            "Foreign keys захищають лише оголошені валідні constraints.",
            "Auto migration не може вивести business transformation.",
            "Destructive migration видаляє дані.",
            "DataStore не робить операції між stores атомарними.",
            "Persistence не є автоматично encrypted або backup-safe.",
        ),
        f"en-{STAGE20_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "A DB transaction is not an atomic network-plus-DB transaction.",
            "WAL does not mean multiple simultaneous writers.",
            "Room Flow does not identify the exact changed rows.",
            "Foreign keys protect only declared valid constraints.",
            "Auto migration cannot infer a business transformation.",
            "Destructive migration deletes data.",
            "DataStore does not make cross-store operations atomic.",
            "Persistence is not automatically encrypted or backup-safe.",
        ),
    }
    for stage_id, section in stage20_sections.items():
        for marker in (*common_stage20_markers, *language_stage20_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 20 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage20-uk-", "en-stage20-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>.*?</strong>", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage21_contracts = (
        "objective", "mental-model", "internals", "conflicts", "checkpoints-ordering",
        "paging-internals", "paging-config", "guarantees", "version-sensitive",
        "decision-framework", "tradeoffs", "production-scenario", "review-trap", "testing",
        "likely-qa", "followups", "self-check", "english-skeletons", "answer-30",
        "answer-2min", "sources",
    )
    for prefix in ("stage21-uk-", "en-stage21-"):
        for suffix in stage21_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 21 contract id {stage_id!r}")

    stage21_sections: dict[str, str] = {}
    for stage_id in (STAGE21_KEY, f"en-{STAGE21_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage21_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 21 section {stage_id!r}")

    common_stage21_markers = (
        "canonical read", "single source of truth", "online-only", "offline-first", "local-first",
        "stale-while-revalidate", "TTL", "tombstone", "outbox", "PENDING", "RUNNING", "ACKED",
        "WorkManager", "idempotency key", "client-generated", "Server-wins", "client-wins", "LWW",
        "version vectors", "change token", "checkpoint", "full resync", "tenant", "process death",
        "Pager", "PagingSource", "PagingData", "LoadParams.Refresh", "Append", "Prepend",
        "getRefreshKey", "anchorPosition", "source", "mediator", "cachedIn", "placeholders",
        "prefetchDistance", "maxSize", "Room", "RemoteMediator", "initialize()",
        "endOfPaginationReached", "remote keys", "total order", "stable cursor", "insertSeparators",
        "exactly-once", "observ", "Stage 20",
    )
    language_stage21_markers = {
        STAGE21_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "SSOT не створює automatic consistency", "Offline-first does not mean all actions work offline",
            "Transaction захищає лише local DB", "Optimistic UI can be rejected",
            "it does not solve conflicts itself", "Paging load order/completion can vary",
        ),
        f"en-{STAGE21_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "SSOT does not create automatic consistency", "Offline-first does not mean all actions work offline",
            "A transaction protects only the local DB", "Optimistic UI can be rejected",
            "it does not solve conflicts itself", "Paging load order and completion can vary",
        ),
    }
    for stage_id, section in stage21_sections.items():
        for marker in (*common_stage21_markers, *language_stage21_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 21 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage21-uk-", "en-stage21-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage22_contracts = (
        "objective", "mental-model", "taxonomy", "seams", "test-doubles", "environments",
        "layer-tests", "coroutine-internals", "structured-concurrency", "flow-testing",
        "data-network-paging", "compose", "hilt", "screenshot", "flaky-ci", "guarantees",
        "version-sensitive", "decision-framework", "tradeoffs", "production-scenario",
        "review-trap", "likely-qa", "followups", "self-check", "english-skeletons",
        "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage22-uk-", "en-stage22-"):
        for suffix in stage22_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 22 contract id {stage_id!r}")

    stage22_sections: dict[str, str] = {}
    for stage_id in (STAGE22_KEY, f"en-{STAGE22_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage22_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 22 section {stage_id!r}")

    common_stage22_markers = (
        "test pyramid", "testing trophy", "Unit", "Integration", "Component", "E2E",
        "Contract", "Screenshot", "performance", "accessibility", "observable state",
        "Fake", "Stub", "Mock", "Spy", "Robolectric", "instrumented", "ViewModel",
        "repository", "runTest", "TestScope", "TestDispatcher", "TestCoroutineScheduler",
        "StandardTestDispatcher", "UnconfinedTestDispatcher", "advanceUntilIdle", "runCurrent",
        "backgroundScope", "Dispatchers.setMain", "Dispatchers.resetMain", "CancellationException",
        "first()", "toList()", "Turbine", "StateFlow", "SharedFlow", "Room", "MigrationTestHelper",
        "MockWebServer", "PagingSource", "RemoteMediator", "semantics tree", "useUnmergedTree=true",
        "testTag", "mainClock.autoAdvance", "StateRestorationTester", "@TestInstallIn",
        "@UninstallModules", "@BindValue", "HiltAndroidRule", "HiltTestApplication",
        "property-based", "fuzzing", "sharding", "mutation testing", "failure artifacts",
        "E2E cannot cover all combinations", "test doubles must preserve relevant contract",
    )
    language_stage22_markers = {
        STAGE22_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "runTest</code> virtualizes delays лише на participating test dispatchers",
            "advanceUntilIdle()</code> може приховати scheduling assumptions",
            "Mocks verify configured interactions, not business correctness",
            "In-memory Room is not migration or disk fidelity",
            "Compose idle does not mean arbitrary external async is done",
            "Screenshot pass is environment-specific", "coverage is not confidence",
            "Retrying flaky tests does not make them deterministic",
        ),
        f"en-{STAGE22_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "runTest</code> virtualizes delays only on participating test dispatchers",
            "advanceUntilIdle()</code> may hide scheduling assumptions",
            "Mocks verify configured interactions, not business correctness",
            "In-memory Room is not migration or disk fidelity",
            "Compose idle does not mean arbitrary external async is done",
            "screenshot pass is environment-specific", "coverage is not confidence",
            "Retrying flaky tests does not make them deterministic",
        ),
    }
    for stage_id, section in stage22_sections.items():
        for marker in (*common_stage22_markers, *language_stage22_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 22 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage22-uk-", "en-stage22-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage23_contracts = (
        "objective", "mental-model", "reliability-topology", "slo-model", "error-taxonomy",
        "resilience-controls", "degradation", "vitals-signals", "crash-anr-native", "telemetry",
        "privacy-cardinality", "alerting-operations", "flags-rollouts", "incident-lifecycle",
        "initialization-skew", "testing-ownership", "guarantees", "version-sensitive",
        "decision-framework", "tradeoffs", "production-scenario", "review-trap", "likely-qa",
        "followups", "self-check", "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage23-uk-", "en-stage23-"):
        for suffix in stage23_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 23 contract id {stage_id!r}")

    stage23_sections: dict[str, str] = {}
    for stage_id in (STAGE23_KEY, f"en-{STAGE23_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage23_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 23 section {stage_id!r}")

    common_stage23_markers = (
        "user journey", "SLI", "SLO", "SLA", "error budget", "Availability", "Correctness",
        "Durability", "Freshness", "domain outcomes", "exponential backoff", "jitter",
        "idempotency", "Circuit breaker", "Bulkhead", "Rate limit", "Retry-After", "offline",
        "cache", "fallback", "startup", "crash", "ANR", "frozen frames", "battery", "network",
        "Android vitals", "input dispatch", "broadcast receiver", "service", "content-provider",
        "main", "tombstone", "OutOfMemoryError", "Crashlytics", "non-fatal", "Logs/events",
        "Metrics", "Traces", "Crash reports", "Breadcrumbs", "correlation ID", "sampling",
        "cardinality", "tokens", "redaction", "consent", "retention", "/build/version/device/OS/network",
        "burn-rate", "deduplicate", "dashboard", "runbook", "Remote Config", "cached",
        "staged rollout", "rollback", "backward/forward compatible", "Detect", "Triage", "Mitigate",
        "Recover", "Learn", "reproduction", "crash before initialization", "monotonic clock",
        "ingestion time", "fault injection", "Chaos", "accountable team", "Stage 24", "Stage 25",
    )
    language_stage23_markers = {
        STAGE23_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "no-crash session is not a correct session", "Telemetry absence is not evidence of health",
            "Crashlytics/nonfatal capture is best effort", "Stack trace alone is not root cause",
            "Correlation ID helps join evidence but not causality",
            "Client-side circuit breaker does not protect all clients globally",
            "Retries can amplify incidents and duplicate effects",
            "Feature flag is not an instant guaranteed kill switch",
            "Staged rollout/canary limits exposure but does not prove safety",
            "ANR rate aggregate can hide cohorts", "logs are events, not metrics",
            "SLO не гарантує кожну сесію",
        ),
        f"en-{STAGE23_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "no-crash session is not a correct session", "Telemetry absence is not evidence of health",
            "Crashlytics/nonfatal capture is best effort", "A stack trace alone is not root cause",
            "A correlation ID helps join evidence but not causality",
            "A client-side circuit breaker does not protect all clients globally",
            "Retries can amplify incidents and duplicate effects",
            "A feature flag is not an instant guaranteed kill switch",
            "staged rollout/canary limits exposure but does not prove safety",
            "ANR rate aggregates can hide cohorts", "logs are events, not metrics",
            "An SLO does not guarantee every session",
        ),
    }
    for stage_id, section in stage23_sections.items():
        for marker in (*common_stage23_markers, *language_stage23_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 23 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage23-uk-", "en-stage23-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage24_contracts = (
        "objective", "mental-model", "process-memory", "art-gc", "references",
        "leak-topology", "lifecycle-resources", "caches-bitmaps", "allocation-pressure",
        "memory-pressure", "profiling", "threading-topology", "jmm", "concurrency-failures",
        "coroutines", "cancellation-sync", "strictmode", "guarantees", "version-sensitive",
        "decision-framework", "tradeoffs", "production-scenario", "review-trap", "likely-qa",
        "followups", "self-check", "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage24-uk-", "en-stage24-"):
        for suffix in stage24_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 24 contract id {stage_id!r}")

    stage24_sections: dict[str, str] = {}
    for stage_id in (STAGE24_KEY, f"en-{STAGE24_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage24_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 24 section {stage_id!r}")

    common_stage24_markers = (
        "managed ART heap", "native heap", "graphics", "ashmem", "GC roots", "WeakReference",
        "SoftReference", "PhantomReference", "ViewBinding", "onDestroyView", "LruCache", "sizeOf()",
        "hardware bitmap", "recycle()", "boxing", "onTrimMemory", "low-memory killer", "Memory Profiler",
        "heap dump", "dominator tree", "retained size", "allocation tracking", "LeakCanary", "Looper",
        "MessageQueue", "Handler", "Choreographer", "Binder thread-pool", "happens-before", "volatile",
        "synchronized", "Atomic", "check-then-act", "Deadlock", "Livelock", "Starvation",
        "Priority inversion", "confinement", "limitedParallelism", "caller-owned scope", "CancellationException",
        "Mutex", "Channels/actors", "runBlocking", "StrictMode", "Closeable", "Cleaner", "Stage 25",
    )
    language_stage24_markers = {
        STAGE24_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "Weak reference doesn't guarantee availability", "onTrimMemory may not arrive before kill",
            "atomics don't make a multi-variable invariant atomic",
            "synchronized establishes happens-before for the same monitor",
            "Cancellation не зупиняє non-cooperative blocking code",
            "StrictMode is detection, not proof", "Retained size needs context",
            "LeakCanary detects retained objects heuristically, not all leaks",
            "OOM stack allocation site may not be root cause",
        ),
        f"en-{STAGE24_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "A weak reference does not guarantee availability", "onTrimMemory may not arrive before kill",
            "atomics do not make a multi-variable invariant atomic",
            "synchronized establishes happens-before for the same monitor",
            "Cancellation does not stop non-cooperative blocking code",
            "StrictMode is detection, not proof", "Retained size needs context",
            "LeakCanary detects retained objects heuristically, not all leaks",
            "The OOM allocation site may not be the root cause",
        ),
    }
    for stage_id, section in stage24_sections.items():
        for marker in (*common_stage24_markers, *language_stage24_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 24 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage24-uk-", "en-stage24-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage25_contracts = (
        "objective", "mental-model", "startup-modes", "startup-internals", "initialization",
        "ttid-ttfd", "startup-measurement", "profiles-art", "frame-pipeline", "jank-anr",
        "recyclerview", "compose-lists", "compose-runtime", "render-costs", "render-tools",
        "statistics", "guarantees", "version-sensitive", "decision-framework", "tradeoffs",
        "production-scenario", "review-trap", "likely-qa", "followups", "self-check",
        "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage25-uk-", "en-stage25-"):
        for suffix in stage25_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 25 contract id {stage_id!r}")

    stage25_sections: dict[str, str] = {}
    for stage_id in (STAGE25_KEY, f"en-{STAGE25_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage25_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 25 section {stage_id!r}")

    common_stage25_markers = (
        "Zygote", "ContentProvider", "App Startup", "Initializer.dependencies()", "static initializers",
        "TTID", "TTFD", "reportFullyDrawn()", "Perfetto", "System Trace", "StartupTimingMetric",
        "StartupMode.COLD", "StartupMode.WARM", "StartupMode.HOT", "CompilationMode.None",
        "CompilationMode.Partial", "CompilationMode.Full", "Baseline Profile", "ProfileInstaller",
        "ProfileVerifier", "Cloud Profiles", "ART", "Choreographer", "RenderThread", "60 Hz",
        "120 Hz", "frozen", "ANR", "measure", "layout", "draw", "RecyclerView", "DiffUtil",
        "payload", "Stable IDs", "prefetch", "LazyColumn", "contentType", "strong skipping",
        "Kotlin 2.0.20+", "deferred", "back-writing", "derivedStateOf", "snapshotFlow", "overdraw",
        "graphicsLayer", "bitmap", "GC", "JankStats", "FrameMetrics", "Layout Inspector",
        "Compose compiler reports", "FrameTimingMetric", "p50", "p95", "p99", "thermal",
        "Staged rollout", "physical devices", "release-like",
    )
    language_stage25_markers = {
        STAGE25_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "TTID не означає usable/complete content", "TTFD requires app signal and can be wrong",
            "60Hz/120Hz frame budgets differ", "Skipped recomposition does not mean no layout/draw",
            "fewer recompositions does not automatically mean faster UI",
            "stable keys preserve identity but do not guarantee no recomposition",
            "Macrobenchmark results depend on device/build/compilation/setup",
            "profiler instrumentation can perturb timing", "Staged rollout metrics can hide cohorts",
            "guarantees neither a startup target nor installation before first run",
        ),
        f"en-{STAGE25_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "TTID does not mean usable or complete content", "TTFD requires an app signal and can be wrong",
            "60Hz/120Hz frame budgets differ", "Skipped recomposition does not mean no layout/draw",
            "fewer recompositions does not automatically mean faster UI",
            "stable keys preserve identity but do not guarantee no recomposition",
            "Macrobenchmark results depend on device/build/compilation/setup",
            "profiler instrumentation can perturb timing", "Staged rollout metrics can hide cohorts",
            "guarantees neither a startup target nor installation before first run",
        ),
    }
    for stage_id, section in stage25_sections.items():
        for marker in (*common_stage25_markers, *language_stage25_markers[stage_id]):
            if marker not in section:
                errors.append(
                    f"index.html: Stage 25 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage25-uk-", "en-stage25-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage26_contracts = (
        "objective", "mental-model", "gradle-internals", "incrementality-caches",
        "parallelism-diagnostics", "dependencies", "build-logic-modules", "kotlin-compilation",
        "compatibility-upgrades", "artifacts-r8", "signing", "variants-versioning",
        "ci-pipeline", "play-delivery", "guarantees", "version-sensitive",
        "decision-framework", "tradeoffs", "production-scenario", "review-trap", "likely-qa",
        "followups", "self-check", "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage26-uk-", "en-stage26-"):
        for suffix in stage26_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 26 contract id {stage_id!r}")

    stage26_sections: dict[str, str] = {}
    for stage_id in (STAGE26_KEY, f"en-{STAGE26_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content,
            re.I | re.S,
        )
        stage26_sections[stage_id] = match.group(1) if match else ""
        if not match:
            errors.append(f"index.html: unable to isolate Stage 26 section {stage_id!r}")

    common_stage26_markers = (
        "initialization", "configuration", "execution", "task graph", "Provider", "inputs", "outputs",
        "incremental", "up-to-date", "local build cache", "remote build cache", "configuration cache",
        "parallel", "Worker API", "Build Analyzer", "--profile", "build scan", "privacy",
        "content filter", "dependency locking", "dependency verification", "version catalog",
        "convention plugin", "build-logic", "buildSrc", "critical path", "ABI", "KAPT", "KSP",
        "AGP", "JDK", "Gradle", "Kotlin", "APK", "AAB", "split APK", "dynamic feature",
        "resource shrinking", "R8", "keep rule", "mapping.txt", "retrace", "Baseline Profile",
        "upload key", "app signing key", "Play App Signing", "key rotation", "versionCode", "versionName",
        "build type", "product flavor", "manifest merge", "BuildConfig", "SBOM", "provenance", "checksum",
        "immutable", "least privilege", "staged rollout", "halt", "resume", "crash", "ANR",
        "expand-contract", "Stage 25", "Stage 27",
    )
    language_stage26_markers = {
        STAGE26_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "Modularization does not automatically speed builds", "KSP is not a drop-in guarantee",
            "Obfuscation is not security or secret protection", "CI green does not prove production safety",
            "AAB is a publishing format", "Staged rollout limits exposure but does not prove safety",
        ),
        f"en-{STAGE26_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "Modularization does not automatically speed builds", "KSP is not a drop-in guarantee",
            "Obfuscation is not security or secret protection", "CI green does not prove production safety",
            "AAB is a publishing format", "Staged rollout limits exposure but does not prove safety",
        ),
    }
    for stage_id, section in stage26_sections.items():
        for marker in (*common_stage26_markers, *language_stage26_markers[stage_id]):
            if marker.lower() not in section.lower():
                errors.append(
                    f"index.html: Stage 26 section {stage_id!r} is missing focused marker {marker!r}"
                )

    for prefix in ("stage26-uk-", "en-stage26-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
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
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(
                        f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}"
                    )

    stage27_contracts = (
        "objective", "mental-model", "requirements", "comparison", "architecture", "data-flow",
        "data-model", "pagination", "freshness", "sync-state", "workmanager", "commerce",
        "failure-matrix", "observability", "guarantees", "decision-framework", "tradeoffs",
        "incident", "review-trap", "likely-qa", "followups", "self-check", "english-skeletons",
        "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage27-uk-", "en-stage27-"):
        for suffix in stage27_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 27 contract id {stage_id!r}")

    stage27_sections: dict[str, str] = {}
    for stage_id in (STAGE27_KEY, f"en-{STAGE27_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content, re.I | re.S,
        )
        section = match.group(1) if match else ""
        stage27_sections[stage_id] = section
        if not match:
            errors.append(f"index.html: unable to isolate Stage 27 section {stage_id!r}")

    stage27_markers = (
        "news", "commerce", "U", "N", "R/W", "Room", "SSOT", "network", "authority",
        "pending intent", "entity", "domain", "UI", "cross-reference", "ordering", "cursor",
        "RemoteMediator", "transaction", "TTL", "stale-while-revalidate", "provenance", "ETag",
        "Initial load", "Refresh", "Append", "dedup", "stable", "query key", "logout",
        "optimistic", "pessimistic", "outbox", "inbox", "idempotency", "backoff", "jitter",
        "dependencies", "conflict", "LWW", "merge", "manual", "tombstone", "reconcil",
        "WorkManager", "expedited", "price", "inventory", "promotion", "tax", "payment",
        "order confirmation", "ambiguous", "auth", "process death", "corruption", "migration",
        "partial page", "out-of-order", "compatibility", "clock skew", "correlation", "redact",
        "encrypted", "account", "fault injection", "contract",
        "cache hit", "connectivity callback", "Stage 28", "Stage 29",
    )
    stage27_language_markers = {
        STAGE27_KEY: ("не exact-time", "не universal authority", "не offline-only"),
        f"en-{STAGE27_KEY}": ("not exact-time", "not universal authority", "not offline-only"),
    }
    for stage_id, section in stage27_sections.items():
        for marker in (*stage27_markers, *stage27_language_markers[stage_id]):
            if marker.lower() not in section.lower():
                errors.append(f"index.html: Stage 27 section {stage_id!r} is missing focused marker {marker!r}")

    for prefix in ("stage27-uk-", "en-stage27-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
            match = re.search(rf'id="{re.escape(prefix + suffix)}".*?</h2>.*?<ol>(.*?)</ol>', content, re.S)
            count = len(re.findall(r"<li>", match.group(1))) if match else 0
            if count != expected:
                errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} list items; found {count}")
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}")

    stage28_contracts = (
        "objective", "mental-model", "requirements", "architecture", "transport", "lifecycle",
        "state-machine", "ordering", "sync-protocol", "internals", "presence", "security",
        "reliability", "testing", "api-guidance", "guarantees", "decision-framework", "tradeoffs",
        "incident", "review-trap", "likely-qa", "followups", "self-check", "english-skeletons",
        "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage28-uk-", "en-stage28-"):
        for suffix in stage28_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 28 contract id {stage_id!r}")

    stage28_sections: dict[str, str] = {}
    for stage_id in (STAGE28_KEY, f"en-{STAGE28_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content, re.I | re.S,
        )
        section = match.group(1) if match else ""
        stage28_sections[stage_id] = section
        if not match:
            errors.append(f"index.html: unable to isolate Stage 28 section {stage_id!r}")

    stage28_markers = (
        "one-to-one", "group", "text/media", "reactions", "edits", "deletes", "read receipts",
        "delivery", "presence", "typing", "offline", "multi-device", "history pagination", "privacy",
        "latency", "reliability", "battery", "UI", "ViewModel", "repository", "local DB", "outbox",
        "sync engine", "WebSocket", "SSE", "long polling", "HTTP", "FCM", "SSOT", "authority",
        "heartbeats", "Doze", "network handover", "backoff", "jitter", "reconnect storm", "token",
        "resume cursor", "PENDING", "SENDING", "ACCEPTED", "DELIVERED", "READ", "FAILED",
        "CANCELLED", "clientOperationId", "serverMessageId", "idempotency", "ambiguous timeout",
        "attachment", "dependsOn", "per conversation", "overlap", "out of order", "gap", "backfill",
        "tombstone", "thread", "client clocks", "snapshot", "delta", "cursor expiry", "full resync",
        "transaction", "crash", "backpressure", "conflate", "StateFlow", "TTL", "structured",
        "eventual", "TLS", "server-side authorization", "account", "media URL", "notification",
        "E2EE", "metadata", "correlation", "PII", "fake transport", "migration", "contract",
        "load", "chaos", "capabilities", "expand-contract", "Stage 29",
    )
    for stage_id, section in stage28_sections.items():
        for marker in stage28_markers:
            if marker.lower() not in section.lower():
                errors.append(f"index.html: Stage 28 section {stage_id!r} is missing focused marker {marker!r}")

    for prefix in ("stage28-uk-", "en-stage28-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
            match = re.search(rf'id="{re.escape(prefix + suffix)}".*?</h2>.*?<ol>(.*?)</ol>', content, re.S)
            count = len(re.findall(r"<li>", match.group(1))) if match else 0
            if count != expected:
                errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} list items; found {count}")
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}")

    stage29_contracts = (
        "objective", "mental-model", "requirements", "boundaries", "architecture", "data-model",
        "order-state-machine", "payment-state-machine", "checkout-sequence", "recovery", "idempotency",
        "webhooks", "atomicity-inventory", "offline-security", "observability", "testing",
        "failure-matrix", "guarantees", "decision-framework", "tradeoffs", "incident", "review-trap",
        "likely-qa", "followups", "self-check", "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage29-uk-", "en-stage29-"):
        for suffix in stage29_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 29 contract id {stage_id!r}")

    stage29_sections: dict[str, str] = {}
    for stage_id in (STAGE29_KEY, f"en-{STAGE29_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content, re.I | re.S,
        )
        section = match.group(1) if match else ""
        stage29_sections[stage_id] = section
        if not match:
            errors.append(f"index.html: unable to isolate Stage 29 section {stage_id!r}")

    stage29_markers = (
        "cart", "checkout", "order", "payment", "fulfillment", "refund", "digital", "physical", "service",
        "Play Billing", "backend verification", "acknowledgement", "PCI", "tokenization", "hosted", "PAN", "CVV",
        "TLS", "Keystore", "minorUnits", "currency", "rounding", "binary floating point", "state machine",
        "terminal", "nonterminal", "reason code", "state-machine version", "authorization", "capture", "partial",
        "decline", "cancellation", "expiry", "void", "dispute", "chargeback", "settlement", "idempotency",
        "payload fingerprint", "scope", "TTL", "UUID", "ambiguous", "process death", "3DS", "deep link",
        "return URL", "replay", "tamper", "webhook", "signature", "event ID", "out-of-order", "missing",
        "inbox", "ledger", "monotonic", "polling", "reconciliation", "Room transaction", "distributed transaction",
        "saga", "compensation", "outbox", "inventory reservation", "oversell", "promotion", "tax", "shipping",
        "immutable", "offline", "WorkManager", "correlation ID", "redact", "audit", "PII", "fake provider",
        "sandbox", "migration", "property", "invariant", "Exactly-once", "provisional", "clock/client timestamps",
        "obfuscation/encryption", "Stage 30",
    )
    stage29_language_markers = {
        STAGE29_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "Payment UI success is not durable order confirmation",
            "webhook receipt is not necessarily settlement",
            "WorkManager is not an exact scheduler and should not own silent payment retries",
        ),
        f"en-{STAGE29_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "Payment UI success is not durable order confirmation",
            "webhook receipt is not necessarily settlement",
            "WorkManager is not an exact scheduler and should not own silent payment retries",
        ),
    }
    for stage_id, section in stage29_sections.items():
        for marker in (*stage29_markers, *stage29_language_markers[stage_id]):
            if marker.lower() not in section.lower():
                errors.append(f"index.html: Stage 29 section {stage_id!r} is missing focused marker {marker!r}")

    for prefix in ("stage29-uk-", "en-stage29-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
            match = re.search(rf'id="{re.escape(prefix + suffix)}".*?</h2>.*?<ol>(.*?)</ol>', content, re.S)
            count = len(re.findall(r"<li>", match.group(1))) if match else 0
            if count != expected:
                errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} list items; found {count}")
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}")

    stage30_contracts = (
        "objective", "requirements-ownership", "architecture", "auth-model", "auth-session",
        "auth-storage", "analytics-design", "analytics-pipeline", "flags-design", "flags-rollout",
        "integration-sequences", "failure-matrix", "guarantees", "api-version-guidance",
        "decisions-tradeoffs", "observability-testing", "incident", "review-trap", "likely-qa",
        "followups", "self-check", "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage30-uk-", "en-stage30-"):
        for suffix in stage30_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 30 contract id {stage_id!r}")

    stage30_sections: dict[str, str] = {}
    for stage_id in (STAGE30_KEY, f"en-{STAGE30_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content, re.I | re.S,
        )
        section = match.group(1) if match else ""
        stage30_sections[stage_id] = section
        if not match:
            errors.append(f"index.html: unable to isolate Stage 30 section {stage_id!r}")

    stage30_markers = (
        "identity", "authentication", "authorization", "session", "account", "device", "OAuth 2", "OIDC",
        "Authorization Code", "PKCE", "external user-agent", "redirect", "App Link", "state", "nonce",
        "code_verifier", "access token", "refresh token", "short-lived", "rotation", "reuse detection",
        "single-flight", "401", "403", "retry", "clock skew", "revocation", "multi-account", "offline",
        "Biometric", "Credential Manager", "passkeys", "Keystore", "client secret", "audience", "scope",
        "schema registry", "required", "optional", "source timestamp", "ingestion timestamp", "pseudonymous",
        "consent", "data minimization", "retention", "deletion", "PII", "allowlist", "denylist", "batch",
        "backoff", "jitter", "at-least-once", "sampling", "quota", "backpressure", "duplicate", "out of order",
        "observability", "exposure", "data-quality", "typed registry", "owner", "purpose", "default", "expiry",
        "build-time", "runtime", "last-known-good", "fetch", "activate", "min-fetch", "real-time",
        "targeting", "deterministic bucketing", "sticky", "contamination", "kill switch", "dependency",
        "invariant", "staged rollout", "guardrail", "circuit breaker", "flag debt", "control-plane",
        "data-plane", "anonymous", "process death", "account switch", "logout", "consent withdrawal",
        "CI green does not prove privacy/compliance",
    )
    stage30_language_markers = {
        STAGE30_KEY: (
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
            "PKCE does not replace redirect/state/nonce/issuer/audience/scope/server validation.",
            "Logout cannot guarantee immediate invalidation without server support",
            "Analytics delivery, order and exactly-once are not guaranteed",
            "Remote Config fetch success does not imply activation or valid business invariants",
            "Deterministic bucketing does not guarantee statistically valid experiments.",
        ),
        f"en-{STAGE30_KEY}": (
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
            "PKCE does not replace redirect/state/nonce/issuer/audience/scope/server validation.",
            "Logout cannot guarantee immediate invalidation without server support",
            "Analytics delivery, order, and exactly-once are not guaranteed",
            "Remote Config fetch success does not imply activation or valid business invariants",
            "Deterministic bucketing does not guarantee statistically valid experiments.",
        ),
    }
    for stage_id, section in stage30_sections.items():
        for marker in (*stage30_markers, *stage30_language_markers[stage_id]):
            if marker.lower() not in section.lower():
                errors.append(f"index.html: Stage 30 section {stage_id!r} is missing focused marker {marker!r}")

    for prefix in ("stage30-uk-", "en-stage30-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
            match = re.search(rf'id="{re.escape(prefix + suffix)}".*?</h2>.*?<ol>(.*?)</ol>', content, re.S)
            count = len(re.findall(r"<li>", match.group(1))) if match else 0
            if count != expected:
                errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} list items; found {count}")
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}")

    stage31_contracts = (
        "objective-discovery", "strategy", "control-plane", "topology", "slice-template",
        "xml-compose", "compose-state-nav", "compose-parity", "rx-inventory", "rx-semantics",
        "modularization", "compatibility-version", "safe-delivery", "vertical-sequence", "risk-matrix",
        "guarantees", "decision-framework", "tradeoffs", "observability-testing", "incident",
        "review-trap", "likely-qa", "followups", "self-check", "english-skeletons",
        "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage31-uk-", "en-stage31-"):
        for suffix in stage31_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 31 contract id {stage_id!r}")

    stage31_sections: dict[str, str] = {}
    for stage_id in (STAGE31_KEY, f"en-{STAGE31_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content, re.I | re.S,
        )
        section = match.group(1) if match else ""
        stage31_sections[stage_id] = section
        if not match:
            errors.append(f"index.html: unable to isolate Stage 31 section {stage_id!r}")

    stage31_markers = (
        "business", "pain/cost", "dependency/build graph", "runtime behavior", "ownership", "release cadence",
        "critical flows", "compatibility constraints", "unsupported assumptions", "success", "stop", "big bang",
        "branch by abstraction", "strangler", "vertical slices", "opportunistic", "RFC/ADR", "target", "interim",
        "dependency", "migration map", "owner", "risk tier", "quality gates", "telemetry", "budget", "deprecation",
        "checkpoint", "rollback", "roll-forward", "ComposeView", "ViewCompositionStrategy", "LifecycleOwner",
        "AndroidView", "AndroidViewBinding", "plain UI", "one state owner", "rememberSaveable", "SavedStateHandle",
        "Fragment", "navigation", "theme", "accessibility", "focus", "IME", "insets", "RecyclerView", "lazy list",
        "Baseline Profiles", "screenshot", "Preview", "disposal", "leak", "Single", "Maybe", "Completable",
        "Observable", "Flowable", "cold", "hot", "null", "error", "Disposable", "cooperative", "CoroutineContext",
        "flowOn", "exception transparency", "retry", "backpressure", "combine", "merge", "flatMapLatest",
        "StateFlow", "SharedFlow", "Channel", "repeatOnLifecycle", "callbackFlow", "awaitClose", "one authoritative",
        "structured concurrency", "runTest", "TestCoroutineScheduler", "package cleanup", "source", "Gradle module",
        "dynamic feature", "cohesion", "public API", "composition root", "DI", "resources", "data", "cycles",
        "common", "clean", "incremental", "CI", "binary", "source", "resource compatibility", "version catalogs",
        "convention plugins", "characterization", "golden", "contract", "dark", "shadow", "feature flag",
        "staged rollout", "canary", "crash/ANR", "jank", "expand", "migrate", "contract", "dual-read", "dual-write",
        "reconciliation", "old-client", "cleanup", "risk register", "failure matrix", "version-sensitive",
        "There is no safe universal 1:1 operator mapping", "mixed Rx/coroutine boundary",
        "Compiling interop does not prove lifecycle/state/accessibility parity",
        "Compose does not inherently make UI faster", "Flow is not drop-in Rx and StateFlow is not an event log",
        "Cancellation is cooperative", "repeatOnLifecycle stops/restarts collection but does not fix wrong upstream scope/sharing",
        "Feature flags do not roll back incompatible persisted data",
        "Staged rollout limits blast radius but doesn't prove safety or instantly remove installed versions",
        "Tests and CI green do not prove production parity",
        "Modularization does not automatically speed builds or enforce ownership",
        "Shadow traffic can create side effects/privacy/cost", "Dual-write has no atomic cross-system guarantee",
        "Rollback must be designed before rollout",
        "Migration complete means legacy dependencies/bridges/flags are removed and outcomes verified, not merely new code added",
    )
    stage31_language_markers = {
        STAGE31_KEY: ("Це likely practice questions, не підтверджений і не гарантований список співбесіди.",),
        f"en-{STAGE31_KEY}": ("These are likely practice questions, not a confirmed or guaranteed interview list.",),
    }
    for stage_id, section in stage31_sections.items():
        for marker in (*stage31_markers, *stage31_language_markers[stage_id]):
            if marker.lower() not in section.lower():
                errors.append(f"index.html: Stage 31 section {stage_id!r} is missing focused marker {marker!r}")

    for prefix in ("stage31-uk-", "en-stage31-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
            match = re.search(rf'id="{re.escape(prefix + suffix)}".*?</h2>.*?<ol>(.*?)</ol>', content, re.S)
            count = len(re.findall(r"<li>", match.group(1))) if match else 0
            if count != expected:
                errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} list items; found {count}")
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}")

    stage32_contracts = (
        "objective-scope", "operating-model", "code-review", "review-template", "mentorship",
        "mentorship-template", "decisions", "adr-template", "stakeholders", "stakeholder-template",
        "tradeoffs-prioritization", "debt-register", "tradeoff-template", "delivery-ownership",
        "interview-evidence", "story-inventory", "anti-patterns", "scenario", "review-trap",
        "guarantees", "decision-framework", "self-assessment", "likely-qa", "followups",
        "self-check", "english-skeletons", "answer-30", "answer-2min", "sources",
    )
    for prefix in ("stage32-uk-", "en-stage32-"):
        for suffix in stage32_contracts:
            stage_id = f"{prefix}{suffix}"
            if ids.count(stage_id) != 1:
                errors.append(f"index.html: expected exactly one Stage 32 contract id {stage_id!r}")

    stage32_sections: dict[str, str] = {}
    for stage_id in (STAGE32_KEY, f"en-{STAGE32_KEY}"):
        match = re.search(
            rf'<details\s+class="major-section"[^>]*\bid="{re.escape(stage_id)}"[^>]*>(.*?)</div></details>',
            content, re.I | re.S,
        )
        section = match.group(1) if match else ""
        stage32_sections[stage_id] = section
        if not match:
            errors.append(f"index.html: unable to isolate Stage 32 section {stage_id!r}")

    stage32_markers = (
        "ambiguity", "technical", "system/team outcomes",
        "sustainable pace", "escalat", "over-engineering", "Senior", "Lead", "Staff",
        "organization-dependent", "correctness", "security", "maintainability", "learning",
        "risk", "small", "reviewable", "author", "reviewer", "evidence", "tests", "BLOCKING",
        "NON-BLOCKING", "QUESTION", "SUGGESTION", "NIT", "rubber stamp", "architecture-by-comment",
        "approval", "latency", "pairing", "Socratic", "direct instruction", "scaffold", "feedback",
        "behavior", "impact", "next action", "psychological safety", "delegation", "sponsorship",
        "mentorship", "bottleneck", "two-way door", "one-way door", "decision owner", "deadline",
        "options", "constraints", "trade-offs", "assumptions", "confidence", "dissent",
        "disagree-and-commit", "spike", "expiry", "revisit", "ADR", "RFC", "outcome luck",
        "decision-makers", "affected groups", "business", "reliability", "cost", "delivery",
        "recommendation", "uncertainty", "scope", "dependencies", "bad news", "product", "backend",
        "QA", "design", "async", "meeting", "urgency", "reversibility", "cost of delay", "effort range",
        "debt taxonomy", "debt register", "incident", "compliance",
        "standardization", "autonomy", "patch", "root fix", "capacity", "residual risk",
        "vertical slices", "pre-mortem", "risk register", "observability", "rollout", "rollback",
        "post-release", "postmortem", "blameless", "accountability", "STAR", "CARL",
        "individual contribution", "verified", "metrics", "honest gap", "story inventory",
        "self-assessment", "30-second answer", "2-minute answer",
        "Code review and CI cannot prove correctness, security, or production safety",
        "Psychological safety does not mean avoiding direct feedback or lowering standards",
        "Mentoring does not guarantee immediate performance", "Delegation does not remove accountability",
        "A blameless postmortem does not mean no standards or ownership",
        "Estimates are uncertainty ranges, not promises", "Metrics can be gamed; activity is not impact",
        "Feature flags and staged rollout limit exposure but do not prove safety or instantly roll back irreversible state",
        "A technically optimal solution can be wrong under product or organizational constraints",
        "STAR structure cannot substitute for genuine evidence",
    )
    stage32_language_markers = {
        STAGE32_KEY: (
            "фінальний етап цього гайда", "немає етапів 33–35",
            "впливати без формальної влади", "Build vs buy",
            "Це likely practice questions, не підтверджений і не гарантований список співбесіди.",
        ),
        f"en-{STAGE32_KEY}": (
            "final stage of this guide", "There are no Stages 33–35",
            "influence without authority", "Build versus buy",
            "These are likely practice questions, not a confirmed or guaranteed interview list.",
        ),
    }
    for stage_id, section in stage32_sections.items():
        for marker in (*stage32_markers, *stage32_language_markers[stage_id]):
            if marker.lower() not in section.lower():
                errors.append(f"index.html: Stage 32 section {stage_id!r} is missing focused marker {marker!r}")

    for prefix in ("stage32-uk-", "en-stage32-"):
        for suffix, expected in (("likely-qa", 10), ("followups", 4), ("self-check", 4)):
            match = re.search(rf'id="{re.escape(prefix + suffix)}".*?</h2>.*?<ol>(.*?)</ol>', content, re.S)
            count = len(re.findall(r"<li>", match.group(1))) if match else 0
            if count != expected:
                errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} list items; found {count}")
            if suffix == "likely-qa" and match:
                labelled = len(re.findall(r"<li>\s*<strong>Q:", match.group(1), re.S))
                if labelled != expected:
                    errors.append(f"index.html: {prefix + suffix!r} must contain exactly {expected} labelled Q&A items; found {labelled}")

    forbidden_later_stage_entries = re.findall(
        r'<(?:a|details)\b[^>]*(?:data-target|data-key|id)="(?:en-)?(?:stage[-_]?3[3-5]|stage3[3-5]-)[^"]*"',
        content, re.I,
    )
    if forbidden_later_stage_entries:
        errors.append("index.html: final Stage 32 must not be followed by Stage 33–35 guide/TOC entries")
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

    print("Validation passed: HTML basics, unique/resolved anchors, Stage 2–32 navigation/contracts, final-stage boundary, and baseline checksum are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
