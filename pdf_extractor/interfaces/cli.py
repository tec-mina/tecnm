"""
interfaces/cli.py — Click + Rich command-line interface.

Architecture (Hexagonal / Ports-and-Adapters):

  This module is the *presentation layer* only.  It does NOT contain
  business logic — it wires Click options into ExtractionRequest and
  delegates everything to the use-cases in app/use_cases.py.

  The same use-case code can be wired to a FastAPI/WebSocket handler later
  without touching any business logic.

Two output modes
----------------
  Human  (default)  — Rich panels, tables, progress bars, emoji glyphs
  Agent  (--json)   — NDJSON event stream, one JSON object per line
                      compatible with Claude Desktop skills, Copilot agents,
                      and any structured log consumer

Subcommands
-----------
  extract       <pdf> [options]  — extract one or more PDFs
  inspect       <pdf> [options]  — profile without extracting
  capabilities                   — inventory system + Python tools
  strategies    [--tier TIER]    — list all strategies
    info        <name>           — details for one strategy
  cache         info | clear     — cache management
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click

# ── Lazy Rich helpers ─────────────────────────────────────────────────────────

def _has_rich() -> bool:
    try:
        import rich  # noqa: F401
        return True
    except ImportError:
        return False


def _console():
    from rich.console import Console
    return Console(stderr=False)


# ── Event handlers (IEventEmitter implementations) ────────────────────────────

class _JsonEmitter:
    """Prints each event as a JSON-line to stdout — for agents/CI."""

    def __call__(self, event: dict[str, Any]) -> None:
        sys.stdout.write(json.dumps(event, ensure_ascii=False) + "\n")
        sys.stdout.flush()


class _RichEmitter:
    """Formats events for human consumption using Rich (or plain text fallback)."""

    _ICONS = {
        "preflight":     "[bold cyan]◆[/]",
        "profile":       "[bold blue]◇[/]",
        "cache_hit":     "[bold yellow]⚡[/]",
        "strategy_plan": "[bold magenta]▶[/]",
        "feature_start": "  [dim]↳[/]",
        "feature_done":  "  [bold green]✓[/]",
        "feature_skip":  "  [dim yellow]⊘[/]",
        "validate":      "[bold cyan]◆[/]",
        "fix":           "[cyan]✎[/]",
        "done":          "[bold green]✔[/]",
        "error":         "[bold red]✗[/]",
        "dry_run":       "[bold yellow]❯[/]",
        "inspect":       "[bold blue]◎[/]",
        "capability":    "",
    }

    def __init__(self, verbose: bool = False) -> None:
        self._verbose = verbose
        self._use_rich = _has_rich()
        if self._use_rich:
            from rich.console import Console
            self._con = Console()

    def __call__(self, event: dict[str, Any]) -> None:
        name = event.get("event", "")
        handler = getattr(self, f"_ev_{name}", self._ev_default)
        handler(event)

    def _print(self, msg: str) -> None:
        if self._use_rich:
            self._con.print(msg)
        else:
            # Strip Rich markup for plain fallback
            import re
            plain = re.sub(r"\[/?[^\]]*\]", "", msg)
            print(plain)

    # ── per-event formatters ──────────────────────────────────────────────────

    def _ev_preflight(self, e: dict) -> None:
        status = "[green]OK[/]" if e.get("ok") else "[red]FAIL[/]"
        scanned = " [yellow](scanned)[/]" if e.get("is_scanned") else ""
        self._print(
            f"{self._ICONS['preflight']} [bold]{e.get('file', '')}[/] — "
            f"{e.get('pages', '?')} pages, {e.get('size_mb', 0):.1f} MB  {status}{scanned}"
        )
        for w in e.get("warnings", []):
            self._print(f"  [yellow]⚠[/] {w}")

    def _ev_profile(self, e: dict) -> None:
        parts = [
            f"text:{e.get('text', 0)}",
            f"scanned:{e.get('scanned', 0)}",
            f"tables:{e.get('tables', 0)}",
        ]
        lang = e.get("lang") or ""
        self._print(
            f"{self._ICONS['profile']} Profile  {' | '.join(parts)}"
            + (f"  lang={lang}" if lang else "")
        )

    def _ev_cache_hit(self, e: dict) -> None:
        self._print(f"{self._ICONS['cache_hit']} Cache hit — skipping extraction")

    def _ev_strategy_plan(self, e: dict) -> None:
        strategies = e.get("strategies", [])
        self._print(
            f"{self._ICONS['strategy_plan']} Strategies  "
            f"[cyan]{', '.join(strategies)}[/]"
        )

    def _ev_feature_start(self, e: dict) -> None:
        if self._verbose:
            self._print(
                f"{self._ICONS['feature_start']} running [italic]{e.get('name')}[/] …"
            )

    def _ev_feature_done(self, e: dict) -> None:
        conf = e.get("confidence", 0)
        conf_color = "green" if conf >= 0.85 else "yellow" if conf >= 0.7 else "red"
        self._print(
            f"{self._ICONS['feature_done']} {e.get('name', '')}  "
            f"[{conf_color}]conf={conf:.2f}[/]"
        )

    def _ev_feature_skip(self, e: dict) -> None:
        self._print(
            f"{self._ICONS['feature_skip']} [dim]{e.get('name', '')}[/]  "
            f"[dim]{e.get('reason', '')}[/]"
        )

    def _ev_validate(self, e: dict) -> None:
        score = e.get("score", 0)
        status = e.get("status", "")
        color = "green" if score >= 80 else "yellow" if score >= 60 else "red"
        issues = e.get("issues", 0)
        issue_txt = f"  {issues} issue{'s' if issues != 1 else ''}" if issues else ""
        self._print(
            f"{self._ICONS['validate']} Quality  [{color}]{score:.0f}/100[/]  "
            f"[dim]{status}[/]{issue_txt}"
        )

    def _ev_fix(self, e: dict) -> None:
        fixes = e.get("fixes", {})
        if fixes:
            parts = [f"{k}:{v}" for k, v in fixes.items() if v]
            self._print(f"{self._ICONS['fix']} Fixes  [dim]{', '.join(parts)}[/]")

    def _ev_done(self, e: dict) -> None:
        quality = e.get("quality", 0)
        color = "green" if quality >= 80 else "yellow" if quality >= 60 else "red"
        self._print(
            f"{self._ICONS['done']} [bold green]Done[/]  "
            f"[{color}]{quality:.0f}/100[/]  "
            f"[dim]{e.get('elapsed_sec', 0):.1f}s[/]  "
            f"→ [underline]{e.get('output', '')}[/]"
        )

    def _ev_error(self, e: dict) -> None:
        self._print(
            f"{self._ICONS['error']} [bold red]Error[/] "
            f"[dim]({e.get('phase', '')})[/]  {e.get('msg', '')}"
        )

    def _ev_dry_run(self, e: dict) -> None:
        plan = e.get("plan", {})
        self._print(f"{self._ICONS['dry_run']} [bold yellow]Dry-run plan:[/]")
        if self._use_rich:
            from rich.pretty import Pretty
            self._con.print(Pretty(plan))
        else:
            print(json.dumps(plan, indent=2, ensure_ascii=False))

    def _ev_inspect(self, e: dict) -> None:
        profile = e.get("profile", {})
        if self._use_rich:
            from rich.table import Table
            tbl = Table(show_header=False, box=None, padding=(0, 2))
            for key, val in profile.items():
                if key in ("metadata", "suggested_strategies"):
                    continue
                tbl.add_row(f"[dim]{key}[/]", str(val))
            self._con.print(tbl)
            strategies = profile.get("suggested_strategies", [])
            if strategies:
                self._con.print(
                    "  [bold]Suggested:[/] " + "[cyan]" + ", ".join(strategies) + "[/]"
                )
        else:
            for key, val in profile.items():
                print(f"  {key}: {val}")

    def _ev_capability(self, e: dict) -> None:
        pass  # handled in bulk by capabilities command

    def _ev_default(self, e: dict) -> None:
        if self._verbose:
            self._print(f"[dim]{json.dumps(e, ensure_ascii=False)}[/]")


# ── CLI root ──────────────────────────────────────────────────────────────────

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(message="%(version)s")
def main() -> None:
    """PDF Extractor — production-grade PDF → Markdown pipeline.

    Run with --json on any subcommand for NDJSON output (agent-friendly).
    """


# ── extract ───────────────────────────────────────────────────────────────────

@main.command()
@click.argument("pdfs", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--output-dir", "-o", default=".", show_default=True,
              help="Directory to write Markdown files into.")
@click.option("--strategy", "-s", "strategies", multiple=True,
              metavar="NAME",
              help="Strategy to use, e.g. text:fast, ocr:tesseract-basic. "
                   "Repeat for multiple. Default: auto-select.")
@click.option("--format", "output_format", default="md",
              type=click.Choice(["md", "json", "both"]), show_default=True,
              help="Output format(s).")
@click.option("--pages", "page_range", default=None, metavar="N-M",
              help="Limit extraction to page range, e.g. 1-10.")
@click.option("--with-images", is_flag=True, default=False,
              help="Extract and save embedded images.")
@click.option("--with-structure", is_flag=True, default=False,
              help="Include PDF bookmarks, annotations, form fields.")
@click.option("--no-toc", is_flag=True, default=False,
              help="Suppress auto-generated table of contents.")
@click.option("--no-fix", is_flag=True, default=False,
              help="Skip post-processing fixes.")
@click.option("--no-spell", is_flag=True, default=False,
              help="Disable OCR spell correction.")
@click.option("--no-cache", is_flag=True, default=False,
              help="Bypass read/write cache.")
@click.option("--quality-threshold", "quality_threshold", type=float, default=None,
              metavar="0-100",
              help="Fail if quality score is below this value.")
@click.option("--strict", is_flag=True, default=False,
              help="Fail if any requested strategy was unavailable or produced no content.")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show extraction plan without writing files.")
@click.option("--verbose", "-v", is_flag=True, default=False,
              help="Show per-feature progress.")
@click.option("--json", "json_output", is_flag=True, default=False,
              help="Emit NDJSON event stream (agent/CI mode).")
def extract(
    pdfs: tuple[str, ...],
    output_dir: str,
    strategies: tuple[str, ...],
    output_format: str,
    page_range: str | None,
    with_images: bool,
    with_structure: bool,
    no_toc: bool,
    no_fix: bool,
    no_spell: bool,
    no_cache: bool,
    quality_threshold: float | None,
    strict: bool,
    dry_run: bool,
    verbose: bool,
    json_output: bool,
) -> None:
    """Extract one or more PDFs to Markdown.

    PDFS can be file paths or glob patterns.
    """
    from ..app.use_cases import ExtractUseCase, ExtractionRequest

    emitter = _JsonEmitter() if json_output else _RichEmitter(verbose=verbose)
    use_case = ExtractUseCase(on_event=emitter)

    parsed_range = _parse_page_range(page_range)
    strategy_list = list(strategies) if strategies else None

    # Exit codes (stable contract for agents / CI):
    #   0 = ok, 1 = generic error, 2 = quality gate failed,
    #   3 = preflight failed, 4 = blocked (no content),
    #   5 = strict mode violation (requested strategy not used)
    exit_code = 0
    for pdf in pdfs:
        req = ExtractionRequest(
            pdf_path=pdf,
            output_dir=output_dir,
            strategies=strategy_list,
            page_range=parsed_range,
            with_images=with_images,
            output_format=output_format,
            no_cache=no_cache,
            no_fix=no_fix,
            apply_spell=not no_spell,
            quality_threshold=quality_threshold,
            dry_run=dry_run,
            with_toc=not no_toc,
            with_structure=with_structure,
        )
        result = use_case.execute(req)

        this_code = _classify_exit(result, strategy_list, strict)
        if this_code and not exit_code:
            exit_code = this_code

        if json_output:
            sys.stdout.write(json.dumps(
                {"event": "result", "exit_code": this_code, **result.to_dict()},
                ensure_ascii=False) + "\n")
            sys.stdout.flush()

    sys.exit(exit_code)


def _classify_exit(result, requested_strategies, strict: bool) -> int:
    """Map a single ExtractionResult to a stable CLI exit code."""
    if result.status == "blocked":
        return 4
    if result.status == "error":
        msg = (result.error_message or "").lower()
        if "quality" in msg:
            return 2
        if "preflight" in msg:
            return 3
        return 1
    if strict and requested_strategies:
        used = set(result.features_used)
        missing = [s for s in requested_strategies if s not in used]
        if missing:
            return 5
    return 0


# ── inspect ───────────────────────────────────────────────────────────────────

@main.command()
@click.argument("pdf", type=click.Path(exists=True))
@click.option("--pages", "page_range", default=None, metavar="N-M",
              help="Restrict profiling to page range.")
@click.option("--json", "json_output", is_flag=True, default=False,
              help="Emit NDJSON event stream.")
def inspect(pdf: str, page_range: str | None, json_output: bool) -> None:
    """Profile a PDF without extracting content.

    Shows page count, scanned/text breakdown, language, suggested strategies.
    """
    from ..app.use_cases import InspectUseCase

    emitter = _JsonEmitter() if json_output else _RichEmitter()
    use_case = InspectUseCase(on_event=emitter)

    parsed_range = _parse_page_range(page_range)
    try:
        result = use_case.execute(pdf, parsed_range)
    except ValueError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)

    if json_output:
        sys.stdout.write(json.dumps({"event": "result", **result.to_dict()},
                                    ensure_ascii=False) + "\n")
    elif _has_rich():
        _print_inspect_panel(result)


# ── capabilities ──────────────────────────────────────────────────────────────

@main.command()
@click.option("--json", "json_output", is_flag=True, default=False,
              help="Emit NDJSON event stream.")
def capabilities(json_output: bool) -> None:
    """Inventory all available system tools and Python packages."""
    from ..app.use_cases import CapabilitiesUseCase
    from ..app.ports import noop_emitter

    # Collect report silently then render all at once for a cleaner table
    use_case = CapabilitiesUseCase(on_event=noop_emitter)
    report = use_case.execute()

    if json_output:
        sys.stdout.write(json.dumps(report.to_dict(), ensure_ascii=False) + "\n")
        return

    _print_capabilities(report)


# ── strategies ────────────────────────────────────────────────────────────────

@main.group()
def strategies() -> None:
    """List and inspect extraction strategies."""


@strategies.command("list")
@click.option("--tier", default=None,
              help="Filter by tier: text, ocr, tables, images, fonts, layout, correct")
@click.option("--json", "json_output", is_flag=True, default=False)
def strategies_list(tier: str | None, json_output: bool) -> None:
    """List all registered strategies."""
    from ..core.registry import registry

    all_meta = registry.list_all()
    failures = registry.discovery_failures()
    if tier:
        all_meta = [m for m in all_meta if m.tier == tier]

    if json_output:
        data = [
            {"name": m.name, "tier": m.tier, "description": m.description,
             "priority": m.priority, "is_heavy": m.is_heavy,
             "requires_python": m.requires_python,
             "requires_system": m.requires_system}
            for m in all_meta
        ]
        sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")
        return

    if not _has_rich():
        for m in all_meta:
            print(f"[{m.tier}] {m.name:35s}  {m.description}")
        return

    from rich.table import Table
    from rich.console import Console

    con = Console()
    tbl = Table(title="Extraction Strategies", show_lines=False)
    tbl.add_column("Tier",        style="cyan",    no_wrap=True, width=10)
    tbl.add_column("Name",        style="bold",    no_wrap=True, width=28)
    tbl.add_column("Description",                  min_width=30)
    tbl.add_column("Priority",    justify="right", width=8)
    tbl.add_column("Heavy",       justify="center",width=6)
    tbl.add_column("Requires",                     min_width=16)

    for m in sorted(all_meta, key=lambda x: (x.tier, x.priority)):
        reqs = ", ".join(m.requires_python + m.requires_system)
        tbl.add_row(
            m.tier, m.name, m.description,
            str(m.priority),
            "[yellow]GPU[/]" if m.is_gpu_optional else
            ("[red]yes[/]" if m.is_heavy else ""),
            f"[dim]{reqs}[/]" if reqs else "",
        )
    con.print(tbl)
    if failures:
        con.print()
        con.print(
            f"[yellow]Discovery warnings:[/] {len(failures)} feature module(s) were skipped during registry scan."
        )
        for failure in failures[:5]:
            con.print(
                f"  [dim]- {failure.module} ({failure.error_type}): {failure.message}[/]"
            )
        if len(failures) > 5:
            con.print(f"  [dim]- ... {len(failures) - 5} more[/]")


@strategies.command("info")
@click.argument("name")
@click.option("--json", "json_output", is_flag=True, default=False)
def strategies_info(name: str, json_output: bool) -> None:
    """Show details for a single strategy by name."""
    from ..core.registry import registry

    meta = registry.get(name)
    if meta is None:
        click.echo(f"Strategy '{name}' not found.", err=True)
        sys.exit(1)

    data = {
        "name": meta.name, "tier": meta.tier,
        "description": meta.description,
        "module": meta.module,
        "priority": meta.priority,
        "is_heavy": meta.is_heavy,
        "is_gpu_optional": meta.is_gpu_optional,
        "requires_python": meta.requires_python,
        "requires_system": meta.requires_system,
        "config": meta.config,
    }

    if json_output:
        sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")
        return

    if _has_rich():
        from rich.console import Console
        from rich.panel import Panel
        from rich.pretty import Pretty
        con = Console()
        con.print(Panel(Pretty(data), title=f"[bold]{name}[/]", expand=False))
    else:
        for k, v in data.items():
            print(f"{k:20s}: {v}")


# ── serve (FastAPI / uvicorn) ────────────────────────────────────────────────

@main.command()
@click.option("--host", default="0.0.0.0", show_default=True,
              help="Bind address.")
@click.option("--port", default=8080, show_default=True, type=int,
              envvar="PORT",
              help="Port to listen on. Also reads $PORT env var (Cloud Run).")
@click.option("--reload", is_flag=True, default=False,
              help="Enable hot-reload (development only).")
def serve(host: str, port: int, reload: bool) -> None:
    """Start the FastAPI REST + SSE server.

    \b
    Local:        python -m pdf_extractor serve
    Custom port:  python -m pdf_extractor serve --port 9000
    Dev reload:   python -m pdf_extractor serve --reload
    Cloud Run:    PORT env var is read automatically.

    API docs available at /docs once the server is running.
    """
    from .api import run_server
    # Display user-friendly URL (localhost if listening on 0.0.0.0)
    display_host = "localhost" if host == "0.0.0.0" else host
    click.echo(f"🚀 PDF Extractor API started")
    click.echo(f"   Web: http://{display_host}:{port}")
    click.echo(f"   Docs: http://{display_host}:{port}/docs")
    run_server(host=host, port=port, reload=reload)


# ── warmup / readiness ───────────────────────────────────────────────────────

@main.command()
@click.option("--languages", "-l", default="es,en", show_default=True,
              help="Comma-separated language codes for OCR model pre-download.")
@click.option("--skip-on-error", is_flag=True, default=False,
              help="Don't fail if a download step errors (recommended for "
                   "Docker build — missing egress shouldn't break the image).")
@click.option("--quiet", "-q", is_flag=True, default=False,
              help="Print one line per step instead of a Rich panel.")
def warmup(languages: str, skip_on_error: bool, quiet: bool) -> None:
    """Pre-download models and JARs so the first request is fast.

    Run at build time:
        RUN python -m pdf_extractor warmup --skip-on-error --quiet

    Or manually before serving:
        python -m pdf_extractor warmup
    """
    from ..app.readiness import run_full_warmup

    langs = tuple(s.strip() for s in languages.split(",") if s.strip())
    failed: list[str] = []

    def _on_step(label: str, ok: bool, err: str | None) -> None:
        marker = "✓" if ok else "✕"
        click.echo(f"  {marker} {label}" + (f"  — {err}" if err and not quiet else ""))
        if not ok:
            failed.append(label)

    click.echo(f"Warming up backends (languages={','.join(langs)})…")
    ok = run_full_warmup(languages=langs, skip_on_error=skip_on_error, on_step=_on_step)
    if ok:
        click.echo("Warmup OK." if not failed else f"Warmup completed with skipped: {failed}")
        sys.exit(0)
    click.echo(f"Warmup FAILED: {failed}", err=True)
    sys.exit(1)


@main.command()
@click.option("--json", "as_json", is_flag=True, default=False,
              help="Emit JSON instead of a human-readable table.")
def readiness(as_json: bool) -> None:
    """Show which backends are installed and initialized."""
    from ..app.readiness import collect_readiness

    report = collect_readiness()
    if as_json:
        click.echo(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
        return

    click.echo(f"All ready: {report.all_ready}")
    click.echo("-" * 78)
    click.echo(f"{'NAME':<28} {'INSTALLED':>10} {'INIT':>6}  HINT/ERROR")
    click.echo("-" * 78)
    for b in report.backends:
        hint = b.last_error or b.init_hint or b.install_hint or ""
        click.echo(f"{b.name:<28} {str(b.installed):>10} {str(b.initialized):>6}  {hint}")


# ── cache ─────────────────────────────────────────────────────────────────────

@main.group()
def cache() -> None:
    """Cache management."""


@cache.command("info")
def cache_info() -> None:
    """Show cache location and size."""
    p = Path.home() / ".cache" / "pdf-extractor"
    if not p.exists():
        click.echo("Cache directory does not exist (no files cached yet).")
        return
    files = list(p.rglob("*"))
    total = sum(f.stat().st_size for f in files if f.is_file())
    click.echo(f"Location : {p}")
    click.echo(f"Entries  : {len(files)}")
    click.echo(f"Size     : {total / 1024 / 1024:.2f} MB")


@cache.command("clear")
@click.confirmation_option(prompt="Delete all cached extractions?")
def cache_clear() -> None:
    """Delete all cached extractions."""
    import shutil as _shutil
    p = Path.home() / ".cache" / "pdf-extractor"
    if p.exists():
        _shutil.rmtree(p)
        click.echo(f"Cache cleared: {p}")
    else:
        click.echo("Cache is already empty.")


# ── helpers ───────────────────────────────────────────────────────────────────

def _parse_page_range(page_range: str | None) -> tuple[int, int] | None:
    if not page_range:
        return None
    try:
        parts = page_range.split("-")
        if len(parts) == 2:
            return (int(parts[0]), int(parts[1]))
        if len(parts) == 1:
            n = int(parts[0])
            return (n, n)
    except ValueError:
        pass
    raise click.BadParameter(f"Page range must be N or N-M, got: {page_range!r}",
                             param_hint="--pages")


def _print_inspect_panel(result: Any) -> None:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    con = Console()
    tbl = Table(show_header=False, box=None, padding=(0, 2))
    d = result.to_dict()
    labels = {
        "page_count": "Pages",
        "file_size_mb": "Size (MB)",
        "is_scanned": "Scanned",
        "scanned_pages": "Scanned pages",
        "text_native_pages": "Text pages",
        "table_pages": "Table pages",
        "has_images": "Has images",
        "dominant_language": "Language",
        "is_encrypted": "Encrypted",
    }
    for key, label in labels.items():
        val = d.get(key, "")
        if isinstance(val, bool):
            val = "[green]yes[/]" if val else "[dim]no[/]"
        else:
            val = str(val)
        tbl.add_row(f"[dim]{label}[/]", val)

    strategies = result.suggested_strategies
    strategy_txt = "[cyan]" + ", ".join(strategies) + "[/]" if strategies else "[dim]none[/]"
    tbl.add_row("[dim]Suggested[/]", strategy_txt)

    meta = result.metadata
    if meta:
        title_val = meta.get("title") or meta.get("Title") or ""
        author_val = meta.get("author") or meta.get("Author") or ""
        if title_val:
            tbl.add_row("[dim]Title[/]", title_val[:80])
        if author_val:
            tbl.add_row("[dim]Author[/]", author_val[:80])

    con.print(Panel(tbl, title=f"[bold]{Path(result.pdf_path).name}[/]", expand=False))


def _print_capabilities(report: Any) -> None:
    if not _has_rich():
        for t in report.system_tools:
            mark = "✓" if t.available else "✗"
            print(f"  {mark} {t.name:20s}  {t.version or ''}")
        for t in report.python_packages:
            mark = "✓" if t.available else "✗"
            print(f"  {mark} {t.name:20s}  {t.version or ''}")
        if getattr(report, "strategy_discovery_failures", None):
            print("\nStrategy discovery failures:")
            for failure in report.strategy_discovery_failures:
                print(
                    f"  - {failure['module']} ({failure['error_type']}): {failure['message']}"
                )
        return

    from rich.console import Console
    from rich.table import Table

    con = Console()

    def _tool_table(title: str, tools: list) -> Table:
        tbl = Table(title=title, show_lines=False, expand=False)
        tbl.add_column("",       width=3, justify="center")
        tbl.add_column("Name",   style="bold", min_width=20)
        tbl.add_column("Version/Note", min_width=30)
        for t in tools:
            mark = "[green]✓[/]" if t.available else "[red]✗[/]"
            note = t.version or t.note or ""
            name_cell = t.name if t.available else f"[dim]{t.name}[/]"
            tbl.add_row(mark, name_cell, f"[dim]{note}[/]")
        return tbl

    con.print(_tool_table("System Tools", report.system_tools))
    con.print()
    con.print(_tool_table("Python Packages", report.python_packages))

    if report.strategies:
        con.print()
        stbl = Table(title="Registered Strategies", show_lines=False)
        stbl.add_column("Tier",  style="cyan",  width=10)
        stbl.add_column("Name",  style="bold",  min_width=25)
        stbl.add_column("Description",           min_width=30)
        for s in sorted(report.strategies, key=lambda x: (x.tier, x.priority)):
            stbl.add_row(s.tier, s.name, s.description)
        con.print(stbl)

    if report.strategy_discovery_failures:
        con.print()
        con.print(
            f"[yellow]Strategy discovery failures:[/] {len(report.strategy_discovery_failures)}"
        )
        for failure in report.strategy_discovery_failures[:5]:
            con.print(
                f"  [dim]- {failure['module']} ({failure['error_type']}): {failure['message']}[/]"
            )
        if len(report.strategy_discovery_failures) > 5:
            con.print(
                f"  [dim]- ... {len(report.strategy_discovery_failures) - 5} more[/]"
            )
