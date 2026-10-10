import pandas as pd
import numpy as np

df = pd.read_csv('data/prototype/financial_events.csv')
df = df.dropna(subset=['amount']).copy()
df['event_date'] = pd.to_datetime(df['event_date'])

# For each user, let's look at full completed months only:
print("Full completed month expenses per user:")
for u, grp in df[df['direction'] == 'debit'].groupby('user_id'):
    m_exp = grp.groupby(grp['event_date'].dt.to_period('M'))['amount'].sum()
    # middle months (excluding first and last partial months)
    middle = m_exp.iloc[1:-1]
    print(f"{u}: Complete months ({len(middle)}): {[round(x, 1) for x in middle.values]}")
    mean_val = np.mean(middle)
    std_val = np.std(middle)
    cv = std_val / mean_val if mean_val > 0 else 0
    print(f"   Mean={mean_val:.1f}, Std={std_val:.1f}, Coeff of Variation={cv:.3f}")
