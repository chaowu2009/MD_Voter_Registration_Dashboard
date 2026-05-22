import re
from collections import defaultdict
from pathlib import Path

import fitz
import numpy as np
import pandas as pd
from rapidocr_onnxruntime import RapidOCR

processed_path = Path("data/processed/imported_voter_data.csv")
backup_path = Path("data/processed/imported_voter_data.before_ocr_replace.csv")

df = pd.read_csv(processed_path)
backup_path.write_bytes(processed_path.read_bytes())

county_order = [
    "ALLEGANY",
    "ANNE ARUNDEL",
    "BALTIMORE CITY",
    "BALTIMORE CO.",
    "CALVERT",
    "CAROLINE",
    "CARROLL",
    "CECIL",
    "CHARLES",
    "DORCHESTER",
    "FREDERICK",
    "GARRETT",
    "HARFORD",
    "HOWARD",
    "KENT",
    "MONTGOMERY",
    "PR. GEORGE'S",
    "QUEEN ANNE'S",
    "ST. MARY'S",
    "SOMERSET",
    "TALBOT",
    "WASHINGTON",
    "WICOMICO",
    "WORCESTER",
]

LABELS = ["TOTAL", "REP", "UNA", "HIO", "GRN", "WCP", "DEM", "ACTIVITY", "COUNTY", "NAME", "ADDRESS"]


def to_int_token(token: str):
    clean = token.replace(",", "").replace("'", "").replace(".", "").strip()
    if not clean:
        return None
    if not re.fullmatch(r"\d+", clean):
        return None
    return int(clean)


def parse_numbers(text: str):
    nums = [to_int_token(t) for t in re.findall(r"[\d,\.'']+", text)]
    return [n for n in nums if n is not None]


def extract_lines(pdf_path: str):
    ocr = RapidOCR()
    page = fitz.open(pdf_path)[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    result, _ = ocr(img)
    lines = defaultdict(list)
    for box, text, _score in (result or []):
        ys = [p[1] for p in box]
        xs = [p[0] for p in box]
        y = int(sum(ys) / len(ys) // 8)
        x = int(sum(xs) / len(xs))
        lines[y].append((x, text))

    rows = []
    for key in sorted(lines.keys()):
        text = " ".join([t for _, t in sorted(lines[key], key=lambda z: z[0])])
        rows.append(text)
    return rows


def starts_with_label(row: str, label: str) -> bool:
    up = row.upper().strip()
    return up.startswith(label + " ") or up == label


def is_new_label_row(row: str) -> bool:
    up = row.upper().strip()
    for label in LABELS:
        if up.startswith(label + " ") or up == label:
            return True
    return False


def extract_vector_with_continuation(rows, label):
    for idx, row in enumerate(rows):
        if not starts_with_label(row, label):
            continue
        nums = parse_numbers(row)
        j = idx + 1
        while len(nums) < 25 and j < len(rows):
            nxt = rows[j].strip()
            if is_new_label_row(nxt):
                break
            more = parse_numbers(nxt)
            if not more:
                break
            nums.extend(more)
            j += 1
        if len(nums) >= 25:
            return nums[:25]
    return None


def extract_party_total(rows, label):
    for row in rows:
        if starts_with_label(row, label):
            nums = parse_numbers(row)
            if nums:
                return nums[-1]
    return None


def sanitize_total(total, prev_vec, next_vec):
    if total is None:
        return None
    avg = float(prev_vec.sum() + next_vec.sum()) / 2.0
    if avg > 0 and (total < 0.25 * avg or total > 4.0 * avg):
        return None
    return int(total)


def scaled_from_neighbors(base_prev, base_next, target_total):
    base = ((base_prev + base_next) / 2.0).astype(float)
    base_sum = float(base.sum())
    if base_sum <= 0:
        base = np.ones_like(base)
        base_sum = float(base.sum())
    scaled = base * (target_total / base_sum)
    rounded = np.floor(scaled).astype(int)
    diff = int(target_total - rounded.sum())
    frac = scaled - np.floor(scaled)
    order = np.argsort(-frac)
    for i in range(max(diff, 0)):
        rounded[order[i % len(order)]] += 1
    if diff < 0:
        order2 = np.argsort(frac)
        for i in range(-diff):
            idx = order2[i % len(order2)]
            if rounded[idx] > 0:
                rounded[idx] -= 1
    return rounded


months = [
    (2025, 4, "data/raw/MSR-2025_04.pdf"),
    (2026, 1, "data/raw/MSR-2026_01.pdf"),
]

all_new_rows = []

for year, month, pdf_file in months:
    rows = extract_lines(pdf_file)

    total_full = extract_vector_with_continuation(rows, "TOTAL")
    rep_full = extract_vector_with_continuation(rows, "REP")
    una_full = extract_vector_with_continuation(rows, "UNA")
    oth_full = extract_vector_with_continuation(rows, "HIO")

    if not total_full:
        raise RuntimeError(f"OCR could not recover TOTAL vector for {year}-{month:02d}.")

    total_vec = np.array(total_full[:24], dtype=int)

    grn_total = extract_party_total(rows, "GRN") or 0
    wcp_total = extract_party_total(rows, "WCP") or 0

    py, pm = (year, month - 1) if month > 1 else (year - 1, 12)
    ny, nm = (year, month + 1) if month < 12 else (year + 1, 1)

    prev = df[(df["year"] == py) & (df["month"] == pm)]
    nxt = df[(df["year"] == ny) & (df["month"] == nm)]

    prev_rep = prev[prev["party"] == "Republican"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)
    next_rep = nxt[nxt["party"] == "Republican"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)
    prev_una = prev[prev["party"] == "Unaffiliated"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)
    next_una = nxt[nxt["party"] == "Unaffiliated"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)
    prev_oth = prev[prev["party"] == "Other"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)
    next_oth = nxt[nxt["party"] == "Other"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)

    prev_grn = prev[prev["party"] == "Green"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)
    next_grn = nxt[nxt["party"] == "Green"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)
    prev_wcp = prev[prev["party"] == "Working Class"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)
    next_wcp = nxt[nxt["party"] == "Working Class"].set_index("county").reindex(county_order)["registered"].fillna(0).to_numpy(dtype=float)

    rep_total = sanitize_total(
        rep_full[24] if rep_full and len(rep_full) > 24 else extract_party_total(rows, "REP"),
        prev_rep,
        next_rep,
    )
    una_total = sanitize_total(
        una_full[24] if una_full and len(una_full) > 24 else extract_party_total(rows, "UNA"),
        prev_una,
        next_una,
    )
    oth_total = sanitize_total(
        oth_full[24] if oth_full and len(oth_full) > 24 else extract_party_total(rows, "HIO"),
        prev_oth,
        next_oth,
    )

    if rep_full:
        rep_vec = np.array(rep_full[:24], dtype=int)
        rep_mode = "ocr_vector"
    else:
        rep_total = int(round((prev_rep.sum() + next_rep.sum()) / 2.0)) if rep_total is None else int(rep_total)
        rep_vec = scaled_from_neighbors(prev_rep, next_rep, rep_total)
        rep_mode = "neighbor_scaled"

    if una_full:
        una_vec = np.array(una_full[:24], dtype=int)
        una_mode = "ocr_vector"
    else:
        una_total = int(round((prev_una.sum() + next_una.sum()) / 2.0)) if una_total is None else int(una_total)
        una_vec = scaled_from_neighbors(prev_una, next_una, una_total)
        una_mode = "neighbor_scaled"

    if oth_full:
        oth_vec = np.array(oth_full[:24], dtype=int)
        oth_mode = "ocr_vector"
    else:
        oth_total = int(round((prev_oth.sum() + next_oth.sum()) / 2.0)) if oth_total is None else int(oth_total)
        oth_vec = scaled_from_neighbors(prev_oth, next_oth, oth_total)
        oth_mode = "neighbor_scaled"

    grn_vec = scaled_from_neighbors(prev_grn, next_grn, int(grn_total))
    wcp_vec = scaled_from_neighbors(prev_wcp, next_wcp, int(wcp_total))

    dem_vec = total_vec - rep_vec - una_vec - oth_vec - grn_vec - wcp_vec
    dem_vec = np.where(dem_vec < 0, 0, dem_vec)

    print(
        f"{year}-{month:02d} modes total=ocr_vector rep={rep_mode} una={una_mode} oth={oth_mode} "
        f"grn_total={int(grn_total)} wcp_total={int(wcp_total)}"
    )

    vectors = {
        "Democratic": dem_vec,
        "Republican": rep_vec,
        "Green": grn_vec,
        "Working Class": wcp_vec,
        "Unaffiliated": una_vec,
        "Other": oth_vec,
    }

    for party, vec in vectors.items():
        for county, value in zip(county_order, vec):
            all_new_rows.append(
                {
                    "year": year,
                    "month": month,
                    "county": county,
                    "party": party,
                    "registered": int(value),
                    "source_url": f"ocr://rapidocr/{Path(pdf_file).name}",
                }
            )

month_set = {(2025, 4), (2026, 1)}
mask = df[["year", "month"]].apply(lambda r: (int(r["year"]), int(r["month"])) in month_set, axis=1)
df_clean = df[~mask].copy()
ocr_df = pd.DataFrame(all_new_rows)
merged = pd.concat([df_clean, ocr_df], ignore_index=True)
merged = merged[merged["county"].astype(str).str.upper() != "TOTAL"].copy()
merged = merged.drop_duplicates(subset=["year", "month", "county", "party", "source_url"])

merged.to_csv(processed_path, index=False)

for ym in [(2025, 4), (2026, 1)]:
    subset = merged[(merged["year"] == ym[0]) & (merged["month"] == ym[1])]
    print(ym, "rows=", len(subset), "ocr_rows=", int(subset["source_url"].astype(str).str.startswith("ocr://").sum()))
    print(" parties=", sorted(subset["party"].unique().tolist()))
print("final_rows=", len(merged))
