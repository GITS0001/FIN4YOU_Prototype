import pandas as pd

df = pd.read_csv('data/prototype/financial_events.csv')
df['event_date'] = pd.to_datetime(df['event_date'])

print(f"Total Transactions: {len(df)}")
print(f"Unique Users: {df['user_id'].nunique()}")
print(f"Date Range: {df['event_date'].min().date()} to {df['event_date'].max().date()}")

for user, user_df in df.groupby('user_id'):
    print(f"\nUser: {user}")
    print(f"  Transactions: {len(user_df)}")
    print(f"  Date Range: {user_df['event_date'].min().date()} to {user_df['event_date'].max().date()}")
    print(f"  Months of data: {len(user_df['event_date'].dt.to_period('M').unique())}")
