import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report
)


# Project paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(
    BASE_DIR, "datasets", "diabetes.csv"
)

MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(MODEL_DIR, exist_ok=True)


# Load dataset
df = pd.read_csv(DATASET_PATH)

# Separate features and target
X = df.drop("Outcome", axis=1)
y = df["Outcome"]


# Replace invalid zero measurements with missing values
invalid_zero_columns = [
    "Glucose",
    "BloodPressure",
    "SkinThickness",
    "Insulin",
    "BMI"
]

for column in invalid_zero_columns:
    X[column] = X[column].replace(0, float("nan"))


# Split dataset before fitting preprocessing steps
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


# Define models
models = {
    "Logistic Regression": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42
        ))
    ]),

    "Random Forest": Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42
        ))
    ])
}


# Train and evaluate models
results = {}

for model_name, model in models.items():

    print(f"\nTraining {model_name}...")

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "Accuracy": accuracy_score(y_test, predictions),
        "Precision": precision_score(
            y_test, predictions, zero_division=0
        ),
        "Recall": recall_score(
            y_test, predictions, zero_division=0
        ),
        "F1 Score": f1_score(
            y_test, predictions, zero_division=0
        ),
        "ROC-AUC": roc_auc_score(y_test, probabilities)
    }

    results[model_name] = metrics

    print(f"\n{model_name} Results:")

    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        predictions,
        zero_division=0
    ))


# Compare models
results_df = pd.DataFrame(results).T

print("\n========== MODEL COMPARISON ==========")
print(results_df.round(4))


# Select model with highest ROC-AUC
best_model_name = results_df["ROC-AUC"].idxmax()

best_model = models[best_model_name]

# Save selected model
model_path = os.path.join(
    MODEL_DIR, "diabetes_prediction_model.pkl"
)

joblib.dump(best_model, model_path)

print("\nBest Model:", best_model_name)
print("Model saved successfully at:", model_path)