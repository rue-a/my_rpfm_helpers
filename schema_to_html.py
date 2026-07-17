#!/usr/bin/env python3
"""
Converts a WH3 RPFM schema (schema_wh3.ron) into a searchable HTML lookup page.

Usage:
    python3 schema_to_html.py [schema.ron] [output.html]

Defaults:
    schema.ron  → ../rpfm-schemas/schema_wh3.ron
    output.html → docs.html
"""

import re
import sys
import html as html_module
from pathlib import Path

try:
    import yaml as _yaml

    def _load_yaml(path: Path) -> dict:
        with path.open(encoding="utf-8") as f:
            return _yaml.safe_load(f) or {}
except ImportError:

    def _load_yaml(path: Path) -> dict:  # type: ignore[misc]
        raise SystemExit(
            "PyYAML is required for notes.yaml support: pip install pyyaml"
        )


def load_notes(path: Path) -> dict:
    """Load optional table/column notes from a YAML file."""
    if not path.exists():
        return {}
    return _load_yaml(path)


# ---------------------------------------------------------------------------
# RON parser
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r"//[^\n]*"  # line comment
    r'|"(?:[^"\\]|\\.)*"'  # double-quoted string
    r"|[-+]?\d+\.\d+(?:[eE][-+]?\d+)?"  # float
    r"|[-+]?\d+"  # integer
    r"|[A-Za-z_][A-Za-z0-9_]*"  # identifier / keyword
    r"|[(){}\[\],:]"  # punctuation
)


class _Tokenizer:
    __slots__ = ("tokens", "pos")

    def __init__(self, text: str):
        self.tokens = [t for t in _TOKEN_RE.findall(text) if not t.startswith("//")]
        self.pos = 0

    # ------------------------------------------------------------------
    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected: str | None = None) -> str:
        t = self.tokens[self.pos]
        if expected is not None and t != expected:
            ctx = self.tokens[max(0, self.pos - 3) : self.pos + 3]
            raise SyntaxError(f"Expected {expected!r}, got {t!r}. Context: {ctx}")
        self.pos += 1
        return t

    # ------------------------------------------------------------------
    def parse_value(self):
        t = self.peek()
        if t is None:
            raise SyntaxError("Unexpected end of input")
        if t == "(":
            return self._parse_struct()
        if t == "[":
            return self._parse_list()
        if t == "{":
            return self._parse_map()
        if t.startswith('"'):
            self.pos += 1
            # Unescape common sequences
            inner = t[1:-1]
            inner = (
                inner.replace('\\"', '"')
                .replace("\\\\", "\\")
                .replace("\\n", "\n")
                .replace("\\t", "\t")
                .replace("\\r", "\r")
            )
            return inner
        if t == "true":
            self.pos += 1
            return True
        if t == "false":
            self.pos += 1
            return False
        if t == "None":
            self.pos += 1
            return None
        if t == "Some":
            self.pos += 1
            self.consume("(")
            v = self.parse_value()
            self.consume(")")
            return v
        # Float / int literal
        if re.match(r"^[-+]?\d+\.\d", t):
            self.pos += 1
            return float(t)
        if re.match(r"^[-+]?\d+$", t):
            self.pos += 1
            return int(t)
        # Identifier: bare enum variant, or variant with payload
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", t):
            name = self.consume()
            if self.peek() == "(":
                self.consume("(")
                fields = self._parse_named_fields()
                self.consume(")")
                return {"__variant": name, **fields}
            return name  # bare variant
        raise SyntaxError(f"Unexpected token: {t!r}")

    def _parse_struct(self):
        self.consume("(")
        fields = self._parse_named_fields()
        self.consume(")")
        return fields

    def _parse_named_fields(self) -> dict:
        result: dict = {}
        idx = 0
        while self.peek() not in (")", None):
            # Named field: identifier followed by ":"
            tok = self.peek()
            if (
                tok
                and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", tok)
                and self.pos + 1 < len(self.tokens)
                and self.tokens[self.pos + 1] == ":"
            ):
                name = self.consume()
                self.consume(":")
                result[name] = self.parse_value()
            else:
                result[str(idx)] = self.parse_value()
                idx += 1
            if self.peek() == ",":
                self.consume(",")
        return result

    def _parse_list(self) -> list:
        self.consume("[")
        items: list = []
        while self.peek() != "]" and self.peek() is not None:
            items.append(self.parse_value())
            if self.peek() == ",":
                self.consume(",")
        self.consume("]")
        return items

    def _parse_map(self) -> dict:
        self.consume("{")
        result: dict = {}
        while self.peek() != "}" and self.peek() is not None:
            key = self.parse_value()
            self.consume(":")
            value = self.parse_value()
            result[key] = value
            if self.peek() == ",":
                self.consume(",")
        self.consume("}")
        return result


def parse_ron(text: str):
    tok = _Tokenizer(text)
    return tok.parse_value()


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------


def field_type_str(ft) -> str:
    """Convert a parsed field_type value to a readable string."""
    if isinstance(ft, str):
        return ft
    if isinstance(ft, dict):
        variant = ft.get("__variant", "?")
        # SequenceU16/SequenceU32 carry a nested definition - just show the type
        return variant
    return str(ft)


def reference_str(ref) -> str:
    """Format is_reference: Some(("table", "column")) → table.column"""
    if ref is None:
        return ""
    if isinstance(ref, dict):
        # parsed as {"0": "table_name", "1": "col_name"}
        parts = [ref.get("0", "?"), ref.get("1", "?")]
        return "_tables.".join(parts) if parts[0] else parts[1]
    if isinstance(ref, (list, tuple)):
        return f"{ref[0]}_tables.{ref[1]}"
    return str(ref)


def lookup_str(lookup) -> str:
    if lookup is None:
        return ""
    if isinstance(lookup, list):
        return ", ".join(str(x) for x in lookup)
    return str(lookup)


def enum_values_str(ev: dict) -> str:
    if not ev:
        return ""
    pairs = sorted(
        (int(k) if isinstance(k, (int, str)) else k, v) for k, v in ev.items()
    )
    return "; ".join(f"{k}={v}" for k, v in pairs)


def get_latest_definition(defs: list) -> dict:
    """Return the definition with the highest version number."""
    return max(defs, key=lambda d: d.get("version", 0))


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------


def e(s: str) -> str:
    """HTML-escape a value."""
    return html_module.escape(str(s))


def render_note(text: str) -> str:
    """HTML-escape note text, rendering `backtick` spans as <code>."""
    parts = re.split(r"`([^`]+)`", text)
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 0:
            out.append(e(part))
        else:
            out.append(f"<code>{e(part)}</code>")
    return "".join(out)


def render_back_refs(refs: list) -> str:
    if not refs:
        return ""
    items = sorted(set(refs))  # sort and deduplicate
    parts = []
    for i, item in enumerate(items):
        src_table, src_col = item
        parts.append(
            f'<a class="tag tag-ref ref-link" data-goto="{e(src_table)}" href="?q={e(src_table)}">'
            f"{e(src_table)}</a>"
            f'<span class="back-ref-col">[{e(src_col)}]{", " if i < len(items) - 1 else ""}</span>'
        )
    return (
        '<div class="back-refs">'
        '<span class="back-refs-label">Referenced by:</span>'
        + "".join(parts)
        + "</div>"
    )


def render_field_row(field: dict, note: str = "") -> str:
    name = field.get("name", "?")
    ft = field_type_str(field.get("field_type", ""))
    is_key = field.get("is_key", False)
    desc = field.get("description", "")
    default = field.get("default_value", None)
    ref = reference_str(field.get("is_reference"))
    lookup = lookup_str(field.get("lookup"))
    ev = enum_values_str(field.get("enum_values", {}))

    # Build search string for JS filtering
    search_blob = " ".join(filter(None, [name, ft, desc, ref, ev])).lower()

    key_attr = 'data-key="1"' if is_key else ""
    key_badge = '<span class="tag tag-key">KEY</span> ' if is_key else ""
    if ref:
        # ref format: "some_table_tables.column" — make the table part a link
        dot = ref.find(".")
        ref_table = ref[:dot] if dot != -1 else ref
        ref_col = ref[dot + 1 :] if dot != -1 else ""
        ref_cell = (
            f'<a class="tag tag-ref ref-link" data-goto="{e(ref_table)}" href="?q={e(ref_table)}">'
            f"{e(ref_table)}</a>"
            f'<span style="color:var(--text-dim)">[{e(ref_col)}]</span>'
        )
        if lookup:
            ref_cell += f'<br><span style="font-size:0.7rem;color:#868e96">lookup: {e(lookup)}</span>'
    else:
        ref_cell = ""
    default_cell = (
        f'<span class="col-default">{e(default)}</span>' if default is not None else ""
    )
    enum_cell = f'<div class="col-enum">{e(ev)}</div>' if ev else ""
    desc_cell = f'<span class="col-desc">{e(desc)}</span>' if desc else ""
    note_cell = f'<span class="col-note">{render_note(note)}</span>' if note else ""

    return (
        f'<tr class="field-row" {key_attr} data-search="{e(search_blob)}">'
        f'<td class="col-name">{key_badge}<code>{e(name)}</code></td>'
        f"<td>{desc_cell}{note_cell}{enum_cell}</td>"
        f"<td>{ref_cell}</td>"
        f"<td>{default_cell}</td>"
        f'<td><span class="tag-type">{e(ft)}</span></td>'
        f"</tr>"
    )


def render_table_section(
    table_name: str,
    defs: list,
    notes: dict | None = None,
    back_refs: dict | None = None,
) -> str:
    latest = get_latest_definition(defs)
    version = latest.get("version", 0)
    fields = latest.get("fields", [])
    loc_fields = latest.get("localised_fields", [])
    all_fields = fields + loc_fields
    table_notes = (notes or {}).get(table_name, {})
    back_ref_html = render_back_refs((back_refs or {}).get(table_name, []))

    rows = "\n".join(
        render_field_row(f, table_notes.get(f.get("name", ""), "")) for f in all_fields
    )
    n_versions = len(defs)
    version_note = f"v{version}" + (
        f" ({n_versions} versions)" if n_versions > 1 else ""
    )

    return f"""
<section class="table-section" id="{e(table_name)}" data-name="{e(table_name)}">
  <div class="table-header">
    <a class="table-name" data-goto="{e(table_name)}" href="?q={e(table_name)}">{e(table_name)}</a>
    <span class="table-meta">{e(version_note)} &middot; {len(all_fields)} columns</span>
  </div>
  {back_ref_html}
  <table class="fields">
    <thead>
      <tr>
        <th>Name</th><th>Description / Enum values</th><th>Reference</th><th>Default</th><th>Type</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
</section>"""


def generate_html(schema: dict, notes: dict | None = None) -> str:
    definitions: dict = schema.get("definitions", {})
    table_names = sorted(definitions.keys())

    # Build reverse reference map: referenced_table -> [(source_table, source_col), ...]
    back_refs: dict = {}
    for tname, defs in definitions.items():
        latest = get_latest_definition(defs)
        all_fields = latest.get("fields", []) + latest.get("localised_fields", [])
        for f in all_fields:
            ref = reference_str(f.get("is_reference"))
            if ref:
                dot = ref.find(".")
                ref_table = ref[:dot] if dot != -1 else ref
                back_refs.setdefault(ref_table, []).append((tname, f.get("name", "?")))

    sidebar_links = "\n".join(
        f'<a href="#{e(n)}" data-name="{e(n)}">{e(n)}</a>' for n in table_names
    )
    sections = "\n".join(
        render_table_section(n, definitions[n], notes, back_refs) for n in table_names
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WH3 Schema Lookup</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<nav id="sidebar">
  <div id="sidebar-search">
    <input id="sidebar-search-input" type="search" placeholder="Filter tables…" autocomplete="off">
  </div>
  <div id="sidebar-count"></div>
  <div id="table-list">
    {sidebar_links}
  </div>
</nav>

<main id="main">
  <div id="topbar">
    <h1>WH3 Schema Lookup</h1>
    <input id="main-search" type="search" placeholder="Search columns, types, descriptions…" autocomplete="off">
    <label id="filter-keys-only">
      <input type="checkbox" id="keys-only-checkbox"> Keys only
    </label>
    <button id="btn-show-all"></button>
  </div>
  {sections}
</main>

<script src="app.js"></script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    here = Path(__file__).parent
    default_schema = here.parent / "rpfm-schemas" / "schema_wh3.ron"
    default_out = here / "docs"

    schema_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_schema
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else default_out

    print(f"Reading {schema_path} \u2026", flush=True)
    text = schema_path.read_text(encoding="utf-8")

    print("Parsing RON \u2026", flush=True)
    schema = parse_ron(text)

    notes_path = here / "notes.yaml"
    notes = load_notes(notes_path)
    if notes:
        print(f"Loaded notes from {notes_path}", flush=True)

    print("Generating files \u2026", flush=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "index.html").write_text(generate_html(schema, notes), encoding="utf-8")

    definitions = schema.get("definitions", {})
    print(f"Written {out_dir}/index.html  ({len(definitions)} tables)")


if __name__ == "__main__":
    main()
