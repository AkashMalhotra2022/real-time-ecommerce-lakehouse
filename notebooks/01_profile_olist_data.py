"""
01_profile_olist_data.py
========================
Profile the raw Olist dataset to turn raw numbers into
concrete data-quality rules for the Bronze -> Silver layer.

Reads all 9 CSVs from data/raw/historical/ and reports, per table:
  - shape (rows x cols) and in-memory size
  - per-column null counts / null %
  - duplicate row counts and duplicate primary-key counts
  - key cardinality (distinct values of id columns)
  - date-column min/max ranges
And across tables:
  - referential-integrity (orphan) checks on the core join graph:
      orders -> customers, order_items -> orders, order_items -> products,
      order_items -> sellers, order_payments -> orders, order_reviews -> orders

Run from the project root:
    python notebooks/01_profile_olist_data.py

No external deps beyond pandas. Output is plain text to stdout so it can be
pasted into notes / used to author the dbt + Spark data-quality expectations.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "historical"

# table name -> (filename, primary-key column or None)
TABLES: dict[str, tuple[str, str | None]] = {
    "customers":            ("olist_customers_dataset.csv",            "customer_id"),
    "geolocation":          ("olist_geolocation_dataset.csv",          None),  # no natural PK
    "order_items":          ("olist_order_items_dataset.csv",          None),  # PK = (order_id, order_item_id)
    "order_payments":       ("olist_order_payments_dataset.csv",       None),  # PK = (order_id, payment_sequential)
    "order_reviews":        ("olist_order_reviews_dataset.csv",        "review_id"),
    "orders":               ("olist_orders_dataset.csv",               "order_id"),
    "products":             ("olist_products_dataset.csv",             "product_id"),
    "sellers":              ("olist_sellers_dataset.csv",              "seller_id"),
    "category_translation": ("product_category_name_translation.csv",  "product_category_name"),
}

# Composite primary keys we want duplicate-checked explicitly.
COMPOSITE_KEYS: dict[str, list[str]] = {
    "order_items":    ["order_id", "order_item_id"],
    "order_payments": ["order_id", "payment_sequential"],
}

# Referential-integrity edges: (child_table, child_col) -> (parent_table, parent_col)
FK_EDGES: list[tuple[str, str, str, str]] = [
    ("orders",          "customer_id", "customers", "customer_id"),
    ("order_items",     "order_id",    "orders",    "order_id"),
    ("order_items",     "product_id",  "products",  "product_id"),
    ("order_items",     "seller_id",   "sellers",   "seller_id"),
    ("order_payments",  "order_id",    "orders",    "order_id"),
    ("order_reviews",   "order_id",    "orders",    "order_id"),
]


def _hr(char: str = "-", width: int = 78) -> str:
    return char * width


def load_tables() -> dict[str, pd.DataFrame]:
    """Load every configured CSV; fail loudly if a file is missing."""
    if not DATA_DIR.exists():
        raise SystemExit(f"Data directory not found: {DATA_DIR}")

    frames: dict[str, pd.DataFrame] = {}
    missing: list[str] = []
    for name, (fname, _pk) in TABLES.items():
        path = DATA_DIR / fname
        if not path.exists():
            missing.append(fname)
            continue
        frames[name] = pd.read_csv(path, low_memory=False)
    if missing:
        raise SystemExit(
            "Missing expected CSV(s) in data/raw/historical/:\n  - "
            + "\n  - ".join(missing)
        )
    return frames


def profile_table(name: str, df: pd.DataFrame) -> None:
    fname, pk = TABLES[name]
    print(_hr("="))
    print(f"TABLE: {name}   ({fname})")
    print(_hr("="))

    rows, cols = df.shape
    mem_mb = df.memory_usage(deep=True).sum() / 1024**2
    print(f"shape        : {rows:,} rows x {cols} cols   (~{mem_mb:.1f} MB in memory)")

    # Duplicate full rows
    dup_rows = int(df.duplicated().sum())
    print(f"duplicate rows: {dup_rows:,}")

    # Primary-key duplicates
    if pk and pk in df.columns:
        pk_dupes = int(df.duplicated(subset=[pk]).sum())
        nunique = df[pk].nunique(dropna=True)
        print(f"PK '{pk}': distinct={nunique:,}, duplicate-key rows={pk_dupes:,}")
    if name in COMPOSITE_KEYS:
        keys = COMPOSITE_KEYS[name]
        if all(k in df.columns for k in keys):
            comp_dupes = int(df.duplicated(subset=keys).sum())
            print(f"composite PK {tuple(keys)}: duplicate-key rows={comp_dupes:,}")

    # Per-column null report
    print("\ncolumn".ljust(40) + "dtype".ljust(14) + "nulls".rjust(12) + "null%".rjust(9))
    print(_hr())
    n = len(df)
    for col in df.columns:
        nulls = int(df[col].isna().sum())
        pct = (nulls / n * 100) if n else 0.0
        print(
            f"{col[:38]:<40}{str(df[col].dtype):<14}{nulls:>12,}{pct:>8.2f}%"
        )

    # Date ranges for any column that looks like a timestamp
    date_cols = [c for c in df.columns if "date" in c.lower() or "timestamp" in c.lower()]
    if date_cols:
        print("\ndate ranges:")
        for c in date_cols:
            parsed = pd.to_datetime(df[c], errors="coerce")
            valid = parsed.dropna()
            if valid.empty:
                print(f"  {c}: no parseable dates")
            else:
                print(f"  {c}: {valid.min()}  ->  {valid.max()}  "
                      f"(unparseable: {int(parsed.isna().sum()) - int(df[c].isna().sum()):,})")
    print()


def check_referential_integrity(frames: dict[str, pd.DataFrame]) -> None:
    print(_hr("="))
    print("REFERENTIAL INTEGRITY  (orphan child rows whose key is absent in parent)")
    print(_hr("="))
    for child_t, child_c, parent_t, parent_c in FK_EDGES:
        if child_t not in frames or parent_t not in frames:
            continue
        child = frames[child_t]
        parent = frames[parent_t]
        if child_c not in child.columns or parent_c not in parent.columns:
            print(f"  {child_t}.{child_c} -> {parent_t}.{parent_c}: column missing, skipped")
            continue
        parent_keys = set(parent[parent_c].dropna().unique())
        child_keys = child[child_c]
        orphans = child_keys[~child_keys.isin(parent_keys)]
        n_orphans = int(orphans.notna().sum())
        pct = (n_orphans / len(child) * 100) if len(child) else 0.0
        flag = "  OK" if n_orphans == 0 else "  <-- orphans"
        print(f"  {child_t}.{child_c} -> {parent_t}.{parent_c}: "
              f"{n_orphans:,} orphans ({pct:.3f}%){flag}")
    print()


def main() -> None:
    print(_hr("#"))
    print("# OLIST DATA PROFILE")
    print(f"# source: {DATA_DIR}")
    print(_hr("#"))
    print()

    frames = load_tables()

    for name in TABLES:
        profile_table(name, frames[name])

    check_referential_integrity(frames)

    print(_hr("#"))
    print("# Profiling complete. Use the null%, duplicate, and orphan figures above")
    print("# to author Silver-layer data-quality expectations (dbt tests / Spark checks).")
    print(_hr("#"))


if __name__ == "__main__":
    main()
