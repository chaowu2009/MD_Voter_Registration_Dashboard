from pathlib import Path
import pandas as pd

path = Path('data/processed/imported_voter_data.csv')
df = pd.read_csv(path)

print('rows', len(df))
print('cols', df.columns.tolist())

required = ['year', 'month', 'county', 'party', 'registered', 'source_url']
print('has_required_cols', all(c in df.columns for c in required))

na_counts = df[required].isna().sum()
print('na_counts', na_counts.to_dict())

# duplicates on business key (source_url excluded)
dup = df.duplicated(subset=['year', 'month', 'county', 'party'], keep=False)
print('duplicate_key_rows', int(dup.sum()))

# month coverage
months = df[['year', 'month']].drop_duplicates().sort_values(['year', 'month'])
print('month_count', len(months))
print('month_min', tuple(months.iloc[0].tolist()))
print('month_max', tuple(months.iloc[-1].tolist()))

# expected dense range between min and max
all_months = []
y, m = int(months.iloc[0]['year']), int(months.iloc[0]['month'])
end_y, end_m = int(months.iloc[-1]['year']), int(months.iloc[-1]['month'])
while (y, m) <= (end_y, end_m):
    all_months.append((y, m))
    m += 1
    if m == 13:
        m = 1
        y += 1
have = set((int(a), int(b)) for a, b in months[['year', 'month']].to_records(index=False))
missing = [x for x in all_months if x not in have]
print('missing_months_between_min_max', missing)

# shape checks per month
shape = df.groupby(['year', 'month']).size().reset_index(name='rows')
print('rows_per_month_unique', sorted(shape['rows'].unique().tolist()))
print('rows_per_month_min', int(shape['rows'].min()))
print('rows_per_month_max', int(shape['rows'].max()))

# expected parties and county count
parties = sorted(df['party'].dropna().unique().tolist())
print('parties', parties)
county_counts = df.groupby(['year', 'month'])['county'].nunique()
party_counts = df.groupby(['year', 'month'])['party'].nunique()
print('county_counts_unique', sorted(county_counts.unique().tolist()))
print('party_counts_unique', sorted(party_counts.unique().tolist()))

# total county row should be absent
has_total_county = (df['county'].astype(str).str.upper() == 'TOTAL').any()
print('has_total_county_row', bool(has_total_county))

# numeric checks
neg = (pd.to_numeric(df['registered'], errors='coerce') < 0).sum()
non_numeric = pd.to_numeric(df['registered'], errors='coerce').isna().sum()
print('negative_registered_rows', int(neg))
print('non_numeric_registered_rows', int(non_numeric))

# OCR replacement checks for two months
for ym in [(2025, 4), (2026, 1)]:
    s = df[(df['year'] == ym[0]) & (df['month'] == ym[1])]
    ocr = int(s['source_url'].astype(str).str.startswith('ocr://').sum())
    imp = int(s['source_url'].astype(str).str.startswith('imputed://').sum())
    print(f'month_{ym[0]}_{ym[1]:02d}_rows', len(s))
    print(f'month_{ym[0]}_{ym[1]:02d}_ocr_rows', ocr)
    print(f'month_{ym[0]}_{ym[1]:02d}_imputed_rows', imp)
