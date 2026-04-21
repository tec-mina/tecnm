#!/usr/bin/env python3
"""
pdf_markdown_compare.py - Heuristic analyzer for extracted markdown.

Despite the historical name, this script does not parse PDFs. It inspects a
markdown file and flags patterns that often indicate extraction problems.

Usage:
    python scripts/pdf_markdown_compare.py document.md
    python scripts/pdf_markdown_compare.py document.md --report analysis.txt
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class MarkdownAnalyzer:
    """Analyze markdown structure and content for common extraction issues."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.content = self.filepath.read_text(encoding="utf-8")
        self.lines = self.content.split("\n")
        self.tables = self._extract_tables()
        self.headings = self._extract_headings()

    def _extract_tables(self) -> List[Dict]:
        tables = []
        index = 0

        while index < len(self.lines):
            line = self.lines[index]
            if "|" in line and re.search(r"\|\s*:?-{3,}:?\s*\|", line):
                header = self.lines[index - 1] if index > 0 else ""
                separator = line
                rows = []
                row_index = index + 1

                while row_index < len(self.lines) and "|" in self.lines[row_index]:
                    rows.append(self.lines[row_index])
                    row_index += 1

                tables.append(
                    {
                        "start_line": index,
                        "header": header,
                        "separator": separator,
                        "rows": rows,
                    }
                )
                index = row_index
            else:
                index += 1

        return tables

    def _extract_headings(self) -> List[Dict]:
        headings = []
        for index, line in enumerate(self.lines):
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                headings.append(
                    {
                        "line": index,
                        "level": len(match.group(1)),
                        "text": match.group(2).strip(),
                    }
                )
        return headings

    def has_explicit_page_markers(self) -> bool:
        return "<!-- Page" in self.content or "<!-- PAGE_BREAK -->" in self.content

    def detect_suspicious_numbers(self) -> List[Tuple[int, str]]:
        suspicious = []
        for index, line in enumerate(self.lines):
            if re.search(r"\b\d{1,3}\b", line) and re.search(r"\w+\s+\d{1,3}\s+\w+", line):
                suspicious.append((index + 1, line.strip()[:100]))
        return suspicious

    def detect_heading_jumps(self) -> List[Tuple[int, str]]:
        jumps = []
        previous = None
        for heading in self.headings:
            if previous is not None and heading["level"] > previous + 1:
                jumps.append((heading["line"] + 1, heading["text"]))
            previous = heading["level"]
        return jumps

    def detect_repeated_lines(self, min_occurrences: int = 3) -> List[Tuple[str, int]]:
        counts: Dict[str, int] = {}
        for line in self.lines:
            stripped = line.strip()
            if not stripped or len(stripped) > 90:
                continue
            counts[stripped] = counts.get(stripped, 0) + 1

        return sorted(
            [(line, count) for line, count in counts.items() if count >= min_occurrences],
            key=lambda item: (-item[1], item[0]),
        )

    def detect_overlong_lines(self, threshold: int = 180) -> List[Tuple[int, str]]:
        findings = []
        for index, line in enumerate(self.lines):
            stripped = line.strip()
            if len(stripped) <= threshold:
                continue
            if stripped.startswith(("#", "|", ">", "<!--")):
                continue
            findings.append((index + 1, stripped[:100]))
        return findings


class AnalysisReport:
    """Generate a structured report for extracted markdown quality."""

    def __init__(self, markdown_file: str):
        self.analyzer = MarkdownAnalyzer(markdown_file)
        self.findings: List[Dict[str, str]] = []

    def check_structure(self) -> "AnalysisReport":
        headings = self.analyzer.headings

        if not self.analyzer.has_explicit_page_markers():
            self.findings.append(
                {
                    "type": "MISSING_PAGE_MARKERS",
                    "severity": "medium",
                    "message": "No explicit page boundary markers detected",
                    "details": "Consider adding page markers if pagination matters.",
                }
            )

        if headings and headings[0]["level"] != 1:
            self.findings.append(
                {
                    "type": "WRONG_HEADING_HIERARCHY",
                    "severity": "medium",
                    "message": f"First heading is H{headings[0]['level']}, not H1",
                    "details": None,
                }
            )

        jumps = self.analyzer.detect_heading_jumps()
        if jumps:
            self.findings.append(
                {
                    "type": "HEADING_LEVEL_JUMPS",
                    "severity": "medium",
                    "message": f"Found {len(jumps)} heading jumps larger than one level",
                    "details": " | ".join(
                        f"Line {line}: \"{text[:50]}\"" for line, text in jumps[:3]
                    ),
                }
            )

        repeated = self.analyzer.detect_repeated_lines()
        if repeated:
            self.findings.append(
                {
                    "type": "REPEATED_LINES",
                    "severity": "medium",
                    "message": f"Found {len(repeated)} repeated short lines",
                    "details": " | ".join(
                        f"\"{line[:40]}\" x{count}" for line, count in repeated[:5]
                    ),
                }
            )

        overlong = self.analyzer.detect_overlong_lines()
        if overlong:
            self.findings.append(
                {
                    "type": "OVERLONG_LINES",
                    "severity": "low",
                    "message": f"Found {len(overlong)} unusually long lines",
                    "details": " | ".join(
                        f"Line {line}: \"{snippet[:50]}\""
                        for line, snippet in overlong[:3]
                    ),
                }
            )

        return self

    def check_tables(self) -> "AnalysisReport":
        for table in self.analyzer.tables:
            header_cols = max(table["header"].count("|") - 1, 0)
            if header_cols == 0:
                continue

            for row in table["rows"]:
                row_cols = row.count("|") - 1
                if row_cols != header_cols:
                    self.findings.append(
                        {
                            "type": "TABLE_MISALIGNED",
                            "severity": "high",
                            "message": f"Table near line {table['start_line'] + 1} has misaligned columns",
                            "details": f"Expected {header_cols} columns but found {row_cols}.",
                        }
                    )
                    break

        return self

    def check_suspicious_numbers(self) -> "AnalysisReport":
        suspicious = self.analyzer.detect_suspicious_numbers()
        if suspicious:
            self.findings.append(
                {
                    "type": "EMBEDDED_PAGE_NUMBERS",
                    "severity": "high",
                    "message": f"Found {len(suspicious)} lines with suspicious embedded numbers",
                    "details": " | ".join(
                        f"Line {line}: \"{snippet[:50]}\""
                        for line, snippet in suspicious[:3]
                    ),
                }
            )
        return self

    def get_status(self) -> str:
        if not self.analyzer.content.strip():
            return "BLOCKED_MISSING_CONTEXT"

        if not self.findings:
            return "PASS"

        severities = {finding["severity"] for finding in self.findings}
        if "high" in severities or "critical" in severities:
            return "ISSUES_FOUND"
        return "PASS"

    def generate_text_report(self) -> str:
        status = self.get_status()

        lines = [f"Status: {status}", "", "Findings:"]
        if status == "BLOCKED_MISSING_CONTEXT":
            lines.append("- Markdown output is empty or unreadable; extraction needs a better source or OCR.")
            return "\n".join(lines)

        if not self.findings:
            lines.append("- No obvious structural issues detected.")
            return "\n".join(lines)

        for finding in self.findings:
            lines.append(
                f"- [{finding['severity'].upper()}] {finding['message']}"
            )
            if finding.get("details"):
                lines.append(f"  Details: {finding['details']}")

        return "\n".join(lines)


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in {"-h", "--help"}:
        print(__doc__)
        sys.exit(0)

    md_file = Path(sys.argv[1])
    if not md_file.exists():
        print(f"Error: Markdown file '{md_file}' not found", file=sys.stderr)
        sys.exit(1)

    report = AnalysisReport(str(md_file))
    report.check_structure().check_tables().check_suspicious_numbers()
    output = report.generate_text_report()

    if "--report" in sys.argv:
        index = sys.argv.index("--report")
        if index + 1 >= len(sys.argv):
            print("Error: --report requires a file path", file=sys.stderr)
            sys.exit(1)
        report_file = Path(sys.argv[index + 1])
        report_file.write_text(output, encoding="utf-8")
        print(f"Report written to: {report_file}")
    else:
        print(output)


if __name__ == "__main__":
    main()
