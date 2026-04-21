"""
output/validator.py — Post-extraction heuristic quality analysis.

Analyzes Markdown structure without re-parsing the PDF.

Issues detected:
  MISSING_PAGE_MARKERS       → no <!-- Page --> markers
  WRONG_HEADING_HIERARCHY    → first heading is not H1
  HEADING_LEVEL_JUMPS        → level jump > 1 (e.g., H1 → H4)
  REPEATED_LINES             → same short line appears 3+ times (artifact)
  OVERLONG_LINES             → lines > 180 chars (configurable)
  TABLE_MISALIGNED           → column count varies within a table
  EMBEDDED_PAGE_NUMBERS      → suspicious standalone numerals
  EMPTY_OUTPUT               → Markdown is empty or < 50 chars

Status:
  PASS         → no issues
  ISSUES_FOUND → high/critical severity flags detected
  BLOCKED      → output empty or unreadable (do not write to disk)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


_OVERLONG_LINE_CHARS = 180
_REPEATED_LINE_MIN = 3
_EMPTY_THRESHOLD = 50
_PAGE_MARKER_RE = re.compile(r"<!-- Page \d+ -->")
_HEADING_RE = re.compile(r"^(#{1,6})\s")
_STANDALONE_NUM_RE = re.compile(r"^\s*\d{1,4}\s*$")


@dataclass
class ValidationIssue:
    code: str
    severity: str    # "critical" | "high" | "medium" | "low"
    description: str
    line: int | None = None


@dataclass
class ValidatorResult:
    status: str                   # "PASS" | "ISSUES_FOUND" | "BLOCKED"
    quality_score: float          # 0–100
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def run(markdown: str, overlong_threshold: int = _OVERLONG_LINE_CHARS) -> ValidatorResult:
    issues: list[ValidationIssue] = []
    warnings: list[str] = []

    # BLOCKED: empty output
    if not markdown or len(markdown.strip()) < _EMPTY_THRESHOLD:
        return ValidatorResult(
            status="BLOCKED",
            quality_score=0.0,
            issues=[ValidationIssue(
                code="EMPTY_OUTPUT",
                severity="critical",
                description=f"Markdown is empty or under {_EMPTY_THRESHOLD} characters",
            )],
        )

    lines = markdown.split("\n")

    # Strip frontmatter for content analysis
    content_lines = _strip_frontmatter(lines)

    # BLOCKED: page markers present but zero real text content
    # (happens when all OCR features are unavailable for scanned PDFs)
    if _PAGE_MARKER_RE.search(markdown):
        text_only = _PAGE_MARKER_RE.sub("", "\n".join(content_lines))
        if len(text_only.strip()) < _EMPTY_THRESHOLD:
            return ValidatorResult(
                status="BLOCKED",
                quality_score=0.0,
                issues=[ValidationIssue(
                    code="EMPTY_CONTENT",
                    severity="critical",
                    description=(
                        "Page markers found but no extractable text. "
                        "PDF likely requires OCR (tesseract / easyocr)."
                    ),
                )],
            )

    # 1. Missing page markers
    if not _PAGE_MARKER_RE.search(markdown):
        issues.append(ValidationIssue(
            code="MISSING_PAGE_MARKERS",
            severity="medium",
            description="No <!-- Page N --> markers found in output",
        ))

    # 2. Heading hierarchy
    heading_issues = _check_headings(content_lines)
    issues.extend(heading_issues)

    # 3. Repeated lines (artifact detection)
    repeated = _find_repeated_lines(content_lines)
    if repeated:
        issues.append(ValidationIssue(
            code="REPEATED_LINES",
            severity="medium",
            description=f"{len(repeated)} short lines repeated {_REPEATED_LINE_MIN}+ times (possible extraction artifact)",
        ))

    # 4. Overlong lines
    overlong = [i + 1 for i, l in enumerate(content_lines)
                if len(l) > overlong_threshold and not l.startswith("|")]
    if overlong:
        issues.append(ValidationIssue(
            code="OVERLONG_LINES",
            severity="low",
            description=f"{len(overlong)} lines exceed {overlong_threshold} chars",
            line=overlong[0],
        ))

    # 5. Table alignment
    table_issues = _check_tables(content_lines)
    issues.extend(table_issues)

    # 6. Embedded page numbers
    embedded = sum(1 for l in content_lines if _STANDALONE_NUM_RE.match(l))
    if embedded > 3:
        issues.append(ValidationIssue(
            code="EMBEDDED_PAGE_NUMBERS",
            severity="low",
            description=f"{embedded} standalone numerals detected (possible extraction noise)",
        ))

    # Compute quality score
    score = _compute_score(issues, len(content_lines))

    # Status
    critical_high = [i for i in issues if i.severity in ("critical", "high")]
    if critical_high:
        status = "ISSUES_FOUND"
    elif issues:
        status = "ISSUES_FOUND"
    else:
        status = "PASS"

    return ValidatorResult(
        status=status,
        quality_score=score,
        issues=issues,
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Internal checks
# ---------------------------------------------------------------------------

def _strip_frontmatter(lines: list[str]) -> list[str]:
    if not lines or lines[0].strip() != "---":
        return lines
    try:
        end = lines.index("---", 1)
        return lines[end + 1:]
    except ValueError:
        return lines


def _check_headings(lines: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    heading_lines = [(i + 1, m.group(1)) for i, l in enumerate(lines)
                     if (m := _HEADING_RE.match(l))]

    if not heading_lines:
        return issues

    first_lineno, first_h = heading_lines[0]
    if len(first_h) != 1:
        issues.append(ValidationIssue(
            code="WRONG_HEADING_HIERARCHY",
            severity="high",
            description=f"First heading is H{len(first_h)}, expected H1",
            line=first_lineno,
        ))

    prev_level = len(first_h)
    for lineno, hashes in heading_lines[1:]:
        level = len(hashes)
        if level - prev_level > 1:
            issues.append(ValidationIssue(
                code="HEADING_LEVEL_JUMPS",
                severity="medium",
                description=f"Heading jumps from H{prev_level} to H{level} at line {lineno}",
                line=lineno,
            ))
        prev_level = level

    return issues


def _find_repeated_lines(lines: list[str]) -> list[str]:
    from collections import Counter
    short_lines = [l.strip() for l in lines
                   if 3 <= len(l.strip()) <= 60 and not l.strip().startswith("#")]
    counts = Counter(short_lines)
    return [l for l, c in counts.items() if c >= _REPEATED_LINE_MIN]


def _check_tables(lines: list[str]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    in_table = False
    table_start = 0
    col_counts: list[int] = []

    for i, line in enumerate(lines):
        if "|" in line and len(line.strip()) > 3:
            if not in_table:
                in_table = True
                table_start = i + 1
                col_counts = []
            col_counts.append(line.count("|"))
        else:
            if in_table and len(col_counts) > 1:
                if len(set(col_counts)) > 1:
                    issues.append(ValidationIssue(
                        code="TABLE_MISALIGNED",
                        severity="high",
                        description=f"Table at line {table_start} has inconsistent column counts: {sorted(set(col_counts))}",
                        line=table_start,
                    ))
            in_table = False
            col_counts = []

    return issues


def _compute_score(issues: list[ValidationIssue], line_count: int) -> float:
    score = 100.0
    penalties = {"critical": 40, "high": 15, "medium": 8, "low": 3}
    for issue in issues:
        score -= penalties.get(issue.severity, 3)
    return round(max(0.0, min(100.0, score)), 1)
