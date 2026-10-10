import pandas as pd

df = pd.read_csv('data/prototype/financial_events.csv')
print("=== CATEGORY DISTRIBUTION ===")
print(df['category'].value_counts())

print("\n=== EVENT TYPE BY CATEGORY ===")
print(pd.crosstab(df['category'], df['event_type']))

print("\n=== DIRECTION BY CATEGORY ===")
print(pd.crosstab(df['category'], df['direction']))

print("\n=== SAMPLE DESCRIPTIONS PER CATEGORY ===")
for cat, grp in df.groupby('category'):
    sample_descs = grp['description'].drop_duplicates().head(5).tolist()
    print(f"{cat} ({len(grp)} txns): {sample_descs}")

print("\n=== INCOME DESCRIPTIONS ===")
income_df = df[df['direction'] == 'credit']
print(income_df[['user_id', 'event_type', 'category', 'description', 'amount', 'event_date']].head(20))
