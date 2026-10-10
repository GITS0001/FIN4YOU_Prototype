import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

df = pd.read_csv('data/prototype/financial_events.csv').dropna(subset=['category', 'description']).copy()
df['event_date'] = pd.to_datetime(df['event_date'])
df = df.sort_values('event_date').reset_index(drop=True)
df['log_amount'] = np.log1p(df['amount'].fillna(0))

# Chronological split
split_idx = int(len(df) * 0.75)
train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

preprocessor = ColumnTransformer(
    transformers=[
        ('text', TfidfVectorizer(ngram_range=(1, 2), max_features=1000), 'description'),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['direction', 'event_type'])
    ]
)

pipe = Pipeline([
    ('prep', preprocessor),
    ('clf', LogisticRegression(max_iter=1000, C=5.0, random_state=42))
])

pipe.fit(train_df[['description', 'direction', 'event_type']], train_df['category'])
preds = pipe.predict(test_df[['description', 'direction', 'event_type']])

acc = accuracy_score(test_df['category'], preds)
p, r, f1, _ = precision_recall_fscore_support(test_df['category'], preds, average='macro', zero_division=0)
print(f"Multi-feature (Text + Direction + EventType) Chronological Holdout:")
print(f"Accuracy: {acc:.4f}, Macro Precision: {p:.4f}, Macro Recall: {r:.4f}, Macro F1: {f1:.4f}")
