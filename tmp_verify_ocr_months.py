import pandas as pd

df = pd.read_csv('data/processed/imported_voter_data.csv')
for ym in [(2025, 4), (2026, 1)]:
    subset = df[(df['year'] == ym[0]) & (df['month'] == ym[1])]
    print('ym', ym, 'rows', len(subset))
    print('  ocr_rows', int(subset['source_url'].astype(str).str.startswith('ocr://').sum()))
    print('  imputed_rows', int(subset['source_url'].astype(str).str.startswith('imputed://').sum()))
    print('  sources', subset['source_url'].drop_duplicates().tolist()[:5])

print('month_count', len(df[['year', 'month']].drop_duplicates()))
