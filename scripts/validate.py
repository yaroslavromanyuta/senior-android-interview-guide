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
        (6, STAGE6_KEY), (7, STAGE7_KEY), (8, STAGE8_KEY),
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
            f'{prefix}kotlin-for-android',
        )
        positions = [content.find(f'id="{value}"') for value in ordered_ids]
        if -1 in positions or positions != sorted(positions):
            errors.append(
                f"index.html: {prefix or 'uk-'}Stages 2–8 must follow Stage 1 and precede Kotlin for Android"
            )

        stage5_id = f"{prefix}{STAGE5_KEY}"
        stage6_id = f"{prefix}{STAGE6_KEY}"
        stage7_id = f"{prefix}{STAGE7_KEY}"
        stage8_id = f"{prefix}{STAGE8_KEY}"
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
            or major_ids.index(stage6_id) != major_ids.index(stage5_id) + 1
            or major_ids.index(stage7_id) != major_ids.index(stage6_id) + 1
            or major_ids.index(stage8_id) != major_ids.index(stage7_id) + 1
        ):
            errors.append(
                f"index.html: {stage6_id!r} must immediately follow {stage5_id!r}, "
                f"{stage7_id!r} must immediately follow {stage6_id!r}, and "
                f"{stage8_id!r} must immediately follow {stage7_id!r}"
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

    print("Validation passed: HTML basics, unique/resolved anchors, Stage 2–8 navigation/contracts, and baseline checksum are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
