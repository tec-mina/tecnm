#!/usr/bin/env python3
"""
markdown_fixer.py - Safe mechanical fixes for extracted markdown files.

This script applies low-risk cleanup to markdown extracted from PDFs.
It is useful for ligatures, control characters, special spaces, repeated blank
lines, and cautious paragraph rejoining. It is not a semantic proofreader.

Usage:
    python scripts/markdown_fixer.py input.md --analyze
    python scripts/markdown_fixer.py input.md --fix-all --output output.md
    python scripts/markdown_fixer.py input.md --fix-ligatures --fix-control-chars --fix-spaces --output output.md
"""

import re
import sys
from pathlib import Path
from typing import List


class MarkdownFixer:
    """Apply low-risk cleanup passes to extracted markdown."""

    LIGATURES = {
        "ﬁ": "fi",
        "ﬂ": "fl",
        "ﬀ": "ff",
        "ﬃ": "ffi",
        "ﬄ": "ffl",
        "ﬆ": "st",
        "ﬅ": "ft",
    }

    def __init__(self, content: str):
        self.original = content
        self.content = content
        self.issues: List[str] = []

    @staticmethod
    def _is_fence(line: str) -> bool:
        stripped = line.strip()
        return stripped.startswith("```") or stripped.startswith("~~~")

    @staticmethod
    def _is_special_block_line(line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False

        if stripped.startswith(("#", ">", "|", "<!--")):
            return True

        if re.match(r"^(-{3,}|\*{3,})$", stripped):
            return True

        if re.match(r"^\d+[.)]\s+", stripped):
            return True

        if re.match(r"^[A-Za-z][.)]\s+", stripped):
            return True

        if stripped.startswith(("- ", "* ", "+ ")):
            return True

        return False

    @classmethod
    def _looks_like_prose(cls, line: str) -> bool:
        stripped = line.strip()
        return bool(stripped) and not cls._is_special_block_line(stripped)

    def fix_ligatures(self) -> "MarkdownFixer":
        found = []
        for ligature, replacement in self.LIGATURES.items():
            if ligature in self.content:
                count = self.content.count(ligature)
                found.append(f"{ligature} ({count}x)")
                self.content = self.content.replace(ligature, replacement)

        if found:
            self.issues.append(f"Fixed ligatures: {', '.join(found)}")
        return self

    def fix_control_chars(self) -> "MarkdownFixer":
        before = len(self.content)
        self.content = "".join(
            char for char in self.content if ord(char) >= 32 or char in "\n\r\t"
        )
        removed = before - len(self.content)
        if removed:
            self.issues.append(f"Removed {removed} control characters")
        return self

    def fix_spaces(self) -> "MarkdownFixer":
        replacements = {
            "\xa0": " ",
            "\u2003": " ",
            "\u2002": " ",
            "\u00a0": " ",
        }

        count = 0
        for special, regular in replacements.items():
            count += self.content.count(special)
            self.content = self.content.replace(special, regular)

        if count:
            self.issues.append(f"Fixed {count} special space characters")
        return self

    def fix_paragraphs(self) -> "MarkdownFixer":
        lines = self.content.split("\n")
        fixed_lines = []
        i = 0
        in_fence = False
        joins = 0

        while i < len(lines):
            line = lines[i]

            if self._is_fence(line):
                in_fence = not in_fence
                fixed_lines.append(line)
                i += 1
                continue

            should_join = False
            join_without_space = False

            if not in_fence and i + 1 < len(lines):
                next_line = lines[i + 1]
                current_stripped = line.rstrip()
                next_stripped = next_line.strip()

                if self._looks_like_prose(current_stripped) and self._looks_like_prose(
                    next_stripped
                ):
                    ends_cleanly = current_stripped.endswith((".", ":", "?", "!", ";"))

                    if current_stripped.endswith("-") and re.search(
                        r"[A-Za-z]-$", current_stripped
                    ):
                        should_join = True
                        join_without_space = True
                    elif not ends_cleanly:
                        should_join = True

            if should_join:
                if join_without_space:
                    combined = current_stripped[:-1] + next_stripped
                else:
                    combined = current_stripped + " " + next_stripped
                fixed_lines.append(combined)
                joins += 1
                i += 2
            else:
                fixed_lines.append(line)
                i += 1

        if joins:
            self.issues.append(f"Rejoined {joins} broken prose lines")

        self.content = "\n".join(fixed_lines)
        return self

    def fix_double_spaces(self) -> "MarkdownFixer":
        original = self.content
        self.content = re.sub(r"\n\n\n+", "\n\n", self.content)
        if self.content != original:
            self.issues.append("Normalized paragraph spacing")
        return self

    def analyze(self) -> List[str]:
        issues = []

        found_ligatures = [lig for lig in self.LIGATURES if lig in self.content]
        if found_ligatures:
            issues.append(
                f"Found {len(found_ligatures)} types of ligatures: {found_ligatures}"
            )

        control_chars = [
            char for char in self.content if ord(char) < 32 and char not in "\n\r\t"
        ]
        if control_chars:
            issues.append(f"Found {len(control_chars)} control characters")

        special_spaces = (
            self.content.count("\xa0")
            + self.content.count("\u2003")
            + self.content.count("\u2002")
        )
        if special_spaces:
            issues.append(f"Found {special_spaces} special/non-breaking spaces")

        excessive_blanks = len(re.findall(r"\n\n\n+", self.content))
        if excessive_blanks:
            issues.append(
                f"Found {excessive_blanks} places with 3+ consecutive newlines"
            )

        hyphen_breaks = len(re.findall(r"[A-Za-z]-\n[A-Za-z]", self.content))
        if hyphen_breaks:
            issues.append(f"Found {hyphen_breaks} likely hyphenated line breaks")

        return issues or ["No obvious issues detected"]

    def get_changes_summary(self) -> str:
        if not self.issues:
            return "No changes made."
        return "\n".join(f"- {issue}" for issue in self.issues)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: File '{input_file}' not found", file=sys.stderr)
        sys.exit(1)

    content = input_file.read_text(encoding="utf-8")
    fixer = MarkdownFixer(content)

    analyze_only = "--analyze" in sys.argv
    fix_ligatures = "--fix-ligatures" in sys.argv or "--fix-all" in sys.argv
    fix_control = "--fix-control-chars" in sys.argv or "--fix-all" in sys.argv
    fix_spaces = "--fix-spaces" in sys.argv or "--fix-all" in sys.argv
    fix_para = "--fix-paragraphs" in sys.argv or "--fix-all" in sys.argv

    output_file = None
    for index, arg in enumerate(sys.argv):
        if arg == "--output" and index + 1 < len(sys.argv):
            output_file = Path(sys.argv[index + 1])
            break

    if analyze_only:
        for issue in fixer.analyze():
            print(f"- {issue}")
        return

    if fix_ligatures:
        fixer.fix_ligatures()
    if fix_control:
        fixer.fix_control_chars()
    if fix_spaces:
        fixer.fix_spaces()
    if fix_para:
        fixer.fix_paragraphs()

    fixer.fix_double_spaces()

    if output_file:
        output_file.write_text(fixer.content, encoding="utf-8")
        print(f"Written to: {output_file}")
        print(fixer.get_changes_summary())
        return

    print(fixer.content)


if __name__ == "__main__":
    main()
