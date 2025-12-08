#!/usr/bin/env python3
import os
import re
import ast
from typing import Dict, List, Set, Tuple

BASE = os.path.dirname(os.path.dirname(__file__))
VERSIONS_DIR = os.path.join(BASE, 'backend', 'db', 'migrations', 'versions')

TableColumns = Dict[str, Set[str]]
Issue = Tuple[str, int, str]


def extract_columns_from_create_table(py_src: str) -> TableColumns:
    """Parse simple op.create_table blocks to map table -> columns.
    This is a best-effort static analysis for typical patterns.
    """
    tables: TableColumns = {}

    # Heuristic regex: op.create_table('table', ... sa.Column('col', ...), ...)
    table_blocks = re.finditer(
        r"op\.create_table\(\s*['\"]([A-Za-z0-9_]+)['\"]\s*,(.*?)\)\s*\n",
        py_src,
        flags=re.DOTALL,
    )
    for m in table_blocks:
        table = m.group(1)
        args = m.group(2)
        cols: Set[str] = set()
        for colm in re.finditer(r"sa\.Column\(\s*['\"]([A-Za-z0-9_]+)['\"]", args):
            cols.add(colm.group(1))
        if cols:
            tables.setdefault(table, set()).update(cols)
    return tables


def extract_index_columns(py_src: str) -> List[Tuple[str, int, str, str, List[str]]]:
    """Find CREATE INDEX statements and op.create_index calls.
    Returns tuples: (file, line, kind, table, cols)
    """
    results: List[Tuple[str, int, str, str, List[str]]] = []
    lines = py_src.splitlines()

    # SQL CREATE INDEX ... ON table (a, b, c)
    for i, line in enumerate(lines, 1):
        if 'CREATE INDEX' in line or 'CREATE UNIQUE INDEX' in line:
            # collect until a closing parenthesis of column list
            block = [line]
            j = i
            while j < len(lines) and ')' not in lines[j]:
                j += 1
                if j < len(lines):
                    block.append(lines[j])
            block_text = '\n'.join(block)
            m = re.search(r"ON\s+([A-Za-z0-9_]+)\s*\(([^\)]*)\)", block_text)
            if m:
                table = m.group(1)
                cols_part = m.group(2)
                # rough split by commas and strip casts / functions
                raw_cols = [c.strip() for c in cols_part.split(',')]
                cols = []
                for rc in raw_cols:
                    # remove function wrappers like DATE(col), COALESCE(col, ...), LOWER(col)
                    rc2 = re.sub(r"[A-Z_]+\((.*?)\)", r"\1", rc)
                    # strip casts ::
                    rc2 = rc2.split('::')[0].strip().strip("'\"")
                    # keep only bare identifiers
                    rc2 = re.sub(r"[^A-Za-z0-9_]", "", rc2)
                    if rc2:
                        cols.append(rc2)
                results.append(("sql", i, table, table, cols))

    # op.create_index('name', 'table', ['a','b'])
    for m in re.finditer(r"op\.create_index\((.*?)\)\s*\n", py_src, flags=re.DOTALL):
        args = m.group(1)
        # try to eval a minimal dict/tuple structure
        # format: 'name', 'table', ['a','b']
        try:
            # Wrap into tuple parentheses if missing
            txt = '(' + args + ')'
            parsed = ast.parse(txt, mode='eval')
            if isinstance(parsed.body, ast.Tuple) and len(parsed.body.elts) >= 3:
                name_node, table_node, cols_node = parsed.body.elts[:3]
                table = None
                cols: List[str] = []
                if isinstance(table_node, ast.Constant) and isinstance(table_node.value, str):
                    table = table_node.value
                if isinstance(cols_node, (ast.List, ast.Tuple)):
                    for elt in cols_node.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            cols.append(elt.value)
                if table and cols:
                    # line number is approximate
                    results.append(("create_index", 0, table, table, cols))
        except Exception:
            pass

    return results


def lint_versions() -> Tuple[TableColumns, List[Issue]]:
    all_tables: TableColumns = {}
    files = [f for f in os.listdir(VERSIONS_DIR) if f.endswith('.py')]

    # First pass: collect table columns from create_table in all files
    file_sources: Dict[str, str] = {}
    for f in files:
        path = os.path.join(VERSIONS_DIR, f)
        with open(path, 'r', encoding='utf-8', errors='ignore') as fh:
            src = fh.read()
            file_sources[f] = src
            cols = extract_columns_from_create_table(src)
            for t, cset in cols.items():
                all_tables.setdefault(t, set()).update(cset)

    # Second pass: validate indexes reference existing columns
    issues: List[Issue] = []
    for f, src in file_sources.items():
        idx_list = extract_index_columns(src)
        for kind, line, table, _tbl2, cols in idx_list:
            known = all_tables.get(table, set())
            missing = [c for c in cols if c not in known]
            if missing:
                issues.append((f, line, f"Index on {table} references missing columns: {missing}"))

    return all_tables, issues


def main():
    tables, issues = lint_versions()
    print(f"Tables discovered: {len(tables)}")
    for t, cols in sorted(tables.items()):
        print(f"  - {t}: {len(cols)} cols")
    print()
    if issues:
        print(f"Found {len(issues)} issues:\n")
        for f, line, msg in issues:
            where = f"{f}:{line}" if line else f
            print(f"- {where} -> {msg}")
    else:
        print("No index/schema mismatches detected.")

if __name__ == '__main__':
    main()
