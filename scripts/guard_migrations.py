#!/usr/bin/env python3
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSIONS = ROOT / 'backend' / 'db' / 'migrations' / 'versions'

CREATE_INDEX_RE = re.compile(r"(CREATE\s+)(UNIQUE\s+)?(INDEX\s+)(?!IF\s+NOT\s+EXISTS)([A-Za-z0-9_\"]+)\s+ON\s+", re.IGNORECASE)
DROP_INDEX_RE = re.compile(r"DROP\s+INDEX\s+(?!IF\s+EXISTS)", re.IGNORECASE)
DROP_FUNCTION_RE = re.compile(r"DROP\s+FUNCTION\s+(?!IF\s+EXISTS)", re.IGNORECASE)
DROP_TRIGGER_RE = re.compile(r"DROP\s+TRIGGER\s+(?!IF\s+EXISTS)", re.IGNORECASE)

# Replace op.drop_index('name', ...) with op.execute('DROP INDEX IF EXISTS name')
OP_DROP_INDEX_RE = re.compile(r"op\.drop_index\(\s*['\"]([A-Za-z0-9_]+)['\"][^\)]*\)\s*")

# Map known column renames
RENAMES = {
    # table -> { old_col: new_col }
    'availabilities': {
        'seller_id': 'seller_partner_id',
    },
    'requirements': {
        'buyer_id': 'buyer_partner_id',
    },
}


def rewrite_sql_guards(text: str) -> str:
    # CREATE INDEX -> CREATE [UNIQUE] INDEX IF NOT EXISTS
    text = CREATE_INDEX_RE.sub(lambda m: f"{m.group(1)}{m.group(2) or ''}{m.group(3)}IF NOT EXISTS {m.group(4)} ON ", text)
    # DROP INDEX -> DROP INDEX IF EXISTS
    text = DROP_INDEX_RE.sub("DROP INDEX IF EXISTS ", text)
    # DROP FUNCTION -> DROP FUNCTION IF EXISTS
    text = DROP_FUNCTION_RE.sub("DROP FUNCTION IF EXISTS ", text)
    # DROP TRIGGER -> DROP TRIGGER IF EXISTS
    text = DROP_TRIGGER_RE.sub("DROP TRIGGER IF EXISTS ", text)
    return text


def rewrite_op_drop_index(text: str) -> str:
    def _repl(m: re.Match) -> str:
        name = m.group(1)
        return f"op.execute('DROP INDEX IF EXISTS {name}')\n"
    return OP_DROP_INDEX_RE.sub(_repl, text)


def rewrite_mismatched_columns(text: str) -> str:
    # Replace in SQL CREATE INDEX ... ON <table> (...)
    for table, mapping in RENAMES.items():
        # Find blocks of "ON table ( ... )"
        pattern = re.compile(rf"(ON\s+{table}\s*\()([^\)]*)(\))", re.IGNORECASE)
        def _replace_cols(m: re.Match) -> str:
            inner = m.group(2)
            for old, new in mapping.items():
                inner = re.sub(rf"\b{old}\b", new, inner)
            return m.group(1) + inner + m.group(3)
        text = pattern.sub(_replace_cols, text)
    return text


def process_file(path: Path) -> bool:
    src = path.read_text(encoding='utf-8', errors='ignore')
    orig = src
    src = rewrite_op_drop_index(src)
    src = rewrite_sql_guards(src)
    src = rewrite_mismatched_columns(src)
    if src != orig:
        path.write_text(src, encoding='utf-8')
        return True
    return False


def main():
    changed = []
    for py in sorted(VERSIONS.glob('*.py')):
        if process_file(py):
            changed.append(py.name)
    if changed:
        print(f"Updated {len(changed)} migration files:")
        for name in changed:
            print(f"  - {name}")
    else:
        print("No changes needed.")

if __name__ == '__main__':
    main()
