import pandas as pd
import numpy as np
import json
import re
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report, log_loss
from sklearn.dummy import DummyClassifier
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Load dataset
df = pd.read_csv('data/prototype/financial_events.csv')
print(f"Total raw events: {len(df)}")

# Filter out rows with missing category or target
df = df.dropna(subset=['category', 'description']).copy()
df['event_date'] = pd.to_datetime(df['event_date'])
df = df.sort_values('event_date').reset_index(drop=True)

print(f"Usable events: {len(df)}")
print(f"Number of classes: {df['category'].nunique()}")

# 1. BASELINE: Majority Class
dummy = DummyClassifier(strategy='most_frequent')
dummy.fit(df[['description']], df['category'])
dummy_preds = dummy.predict(df[['description']])
dummy_acc = accuracy_score(df['category'], dummy_preds)
p, r, dummy_f1, _ = precision_recall_fscore_support(df['category'], dummy_preds, average='macro', zero_division=0)
print(f"\n[Baseline 1 - Majority Class] Accuracy: {dummy_acc:.4f}, Macro F1: {dummy_f1:.4f}")

# 2. BASELINE: Keyword Rule-Based
keyword_rules = {
    'rent': ['rent', 'landlord', 'housing rent', 'apartment'],
    'utilities': ['utility', 'water', 'electricity', 'power', 'municipal'],
    'groceries': ['grocer', 'pantry', 'fresh food', 'market purchase', 'supermarket'],
    'transport': ['commuter', 'ride-hailing', 'metro', 'bus', 'fuel', 'taxi', 'fare'],
    'dining': ['bakery', 'snacks', 'lunch', 'takeaway', 'quick-service', 'coffee', 'meal', 'food delivery'],
    'salary': ['salary', 'payroll', 'net salary', 'arrears'],
    'debt_repayment': ['loan', 'instalment', 'debt'],
    'education': ['training', 'tuition', 'school fee', 'course'],
    'shopping': ['merchant', 'card charge', 'card purchase', 'card authorization'],
    'cloud_storage': ['storage', 'backup'],
    'music_subscription': ['music', 'audio streaming'],
    'streaming': ['streaming', 'video streaming'],
    'delivery_membership': ['delivery service', 'delivery plan', 'food delivery membership'],
    'gym': ['gym', 'fitness'],
    'healthcare': ['clinic', 'pharmacy', 'therapy', 'diagnostic'],
    'housing': ['repair', 'building maintenance'],
    'insurance': ['insurance', 'policy'],
    'entertainment': ['cinema', 'tickets', 'entertainment', 'games', 'recreation'],
    'family_support': ['dependent care']
}

def rule_predict(desc):
    desc_l = str(desc).lower()
    for cat, kws in keyword_rules.items():
        for kw in kws:
            if kw in desc_l:
                return cat
    return 'groceries' # fallback

rule_preds = df['description'].apply(rule_predict)
rule_acc = accuracy_score(df['category'], rule_preds)
p, r, rule_f1, _ = precision_recall_fscore_support(df['category'], rule_preds, average='macro', zero_division=0)
print(f"[Baseline 2 - Keyword Heuristic] Accuracy: {rule_acc:.4f}, Macro F1: {rule_f1:.4f}")

# 3. CHRONOLOGICAL HOLDOUT SPLIT (first 75% train, last 25% test)
split_idx = int(len(df) * 0.75)
train_df = df.iloc[:split_idx].copy()
test_df = df.iloc[split_idx:].copy()

print(f"\nChronological Split: Train={len(train_df)} ({train_df['event_date'].min().date()} to {train_df['event_date'].max().date()}), Test={len(test_df)} ({test_df['event_date'].min().date()} to {test_df['event_date'].max().date()})")

# Feature pipeline
tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=1000, lowercase=True)

models = {
    'MultinomialNB': MultinomialNB(alpha=0.1),
    'LogisticRegression': LogisticRegression(max_iter=1000, C=5.0, random_state=42),
    'LinearSVC_Calibrated': CalibratedClassifierCV(estimator=SGDClassifier(loss='hinge', random_state=42), cv=3),
    'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
    'SGD_LogLoss': SGDClassifier(loss='log_loss', random_state=42, max_iter=1000)
}

results = []
for name, model in models.items():
    pipe = Pipeline([
        ('tfidf', tfidf),
        ('clf', model)
    ])
    
    pipe.fit(train_df['description'], train_df['category'])
    test_preds = pipe.predict(test_df['description'])
    acc = accuracy_score(test_df['category'], test_preds)
    p, r, f1, _ = precision_recall_fscore_support(test_df['category'], test_preds, average='macro', zero_division=0)
    
    results.append({
        'Model': name,
        'Test_Accuracy': round(acc, 4),
        'Macro_Precision': round(p, 4),
        'Macro_Recall': round(r, 4),
        'Macro_F1': round(f1, 4)
    })

print("\n=== CHRONOLOGICAL HOLDOUT RESULTS ===")
res_df = pd.DataFrame(results)
print(res_df.to_string(index=False))

# 4. 5-FOLD STRATIFIED CROSS-VALIDATION
print("\n=== 5-FOLD STRATIFIED CROSS-VALIDATION (LOGISTIC REGRESSION) ===")
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_accs = []
cv_f1s = []

X = df['description']
y = df['category']

for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
    X_tr, y_tr = X.iloc[train_idx], y.iloc[train_idx]
    X_val, y_val = X.iloc[val_idx], y.iloc[val_idx]
    
    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
        ('clf', LogisticRegression(max_iter=1000, C=5.0, random_state=42))
    ])
    pipe.fit(X_tr, y_tr)
    v_preds = pipe.predict(X_val)
    acc = accuracy_score(y_val, v_preds)
    _, _, f1, _ = precision_recall_fscore_support(y_val, v_preds, average='macro', zero_division=0)
    cv_accs.append(acc)
    cv_f1s.append(f1)
    print(f"  Fold {fold+1}: Acc = {acc:.4f}, Macro F1 = {f1:.4f}")

print(f"Mean CV Accuracy: {np.mean(cv_accs):.4f} (+/- {np.std(cv_accs):.4f})")
print(f"Mean CV Macro F1: {np.mean(cv_f1s):.4f} (+/- {np.std(cv_f1s):.4f})")

# Per-class classification report for Best Model
best_pipe = Pipeline([
    ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=1000)),
    ('clf', LogisticRegression(max_iter=1000, C=5.0, random_state=42))
])
best_pipe.fit(train_df['description'], train_df['category'])
test_preds = best_pipe.predict(test_df['description'])
print("\n=== DETAILED CLASSIFICATION REPORT (CHRONOLOGICAL TEST SET) ===")
print(classification_report(test_df['category'], test_preds, zero_division=0))
