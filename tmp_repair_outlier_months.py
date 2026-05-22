from pathlib import Path

import pandas as pd

processed_path = Path('data/processed/imported_voter_data.csv')
backup_path = Path('data/processed/imported_voter_data.before_outlier_repair.csv')

bad_months = {
    (2024, 8),
    (2024, 9),
    (2024, 10),
    (2024, 11),
    (2024, 12),
    (2025, 1),
    (2025, 4),
    (2026, 1),
}

df = pd.read_csv(processed_path)
backup_path.write_bytes(processed_path.read_bytes())

all_months = sorted({(int(y), int(m)) for y, m in df[['year', 'month']].to_records(index=False)})
month_index = {ym: idx for idx, ym in enumerate(all_months)}

rows = []
for county in sorted(df['county'].unique()):
    for party in sorted(df['party'].unique()):
        sub = df[(df['county'] == county) & (df['party'] == party)][['year', 'month', 'registered']].copy()
        values = {(int(r.year), int(r.month)): float(r.registered) for r in sub.itertuples(index=False)}

        for ym in bad_months:
            if ym not in month_index:
                continue

            # Find nearest non-bad previous month with a value.
            prev_ym = None
            for i in range(month_index[ym] - 1, -1, -1):
                cand = all_months[i]
                if cand in bad_months:
                    continue
                if cand in values:
                    prev_ym = cand
                    break

            # Find nearest non-bad next month with a value.
            next_ym = None
            for i in range(month_index[ym] + 1, len(all_months)):
                cand = all_months[i]
                if cand in bad_months:
                    continue
                if cand in values:
                    next_ym = cand
                    break

            if prev_ym is None and next_ym is None:
                continue
            if prev_ym is None:
                repaired = values[next_ym]
            elif next_ym is None:
                repaired = values[prev_ym]
            else:
                p_idx = month_index[prev_ym]
                t_idx = month_index[ym]
                n_idx = month_index[next_ym]
                p_val = values[prev_ym]
                n_val = values[next_ym]
                frac = (t_idx - p_idx) / (n_idx - p_idx)
                repaired = p_val + frac * (n_val - p_val)

            rows.append(
                {
                    'year': ym[0],
                    'month': ym[1],
                    'county': county,
                    'party': party,
                    'registered': int(round(max(repaired, 0))),
                    'source_url': f'repaired://statewide_outlier_interpolation/{ym[0]}_{ym[1]:02d}',
                }
            )

repair_df = pd.DataFrame(rows)
if repair_df.empty:
    raise RuntimeError('No repaired rows generated; aborting')

mask = df[['year', 'month']].apply(lambda r: (int(r['year']), int(r['month'])) in bad_months, axis=1)
clean = df[~mask].copy()
merged = pd.concat([clean, repair_df], ignore_index=True)
merged = merged.drop_duplicates(subset=['year', 'month', 'county', 'party'], keep='last')
merged = merged.sort_values(['year', 'month', 'county', 'party']).reset_index(drop=True)

merged.to_csv(processed_path, index=False)

monthly = merged.groupby(['year', 'month'], as_index=False)['registered'].sum().sort_values(['year', 'month'])
print('repaired_months', sorted(list(bad_months)))
print(monthly.to_string(index=False))

h = merged[merged['county'].str.upper() == 'HOWARD'].groupby(['year', 'month'], as_index=False)['registered'].sum().sort_values(['year', 'month'])
print('\nHoward trend after repair:')
print(h.to_string(index=False))
