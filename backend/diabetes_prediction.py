import os
import joblib
import pandas as pd


# Locate the trained model
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "diabetes_prediction_model.pkl"
)


def load_diabetes_model():
    """Load the trained diabetes prediction model."""

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Diabetes prediction model not found. "
            "Please run backend/model_training.py first."
        )

    return joblib.load(MODEL_PATH)


def predict_diabetes_risk(patient_data):
    """
    Predict diabetes risk using the trained ML model.

    Required features:
    Pregnancies, Glucose, BloodPressure, SkinThickness,
    Insulin, BMI, DiabetesPedigreeFunction, Age
    """

    required_features = [
        "Pregnancies",
        "Glucose",
        "BloodPressure",
        "SkinThickness",
        "Insulin",
        "BMI",
        "DiabetesPedigreeFunction",
        "Age"
    ]

    # Validate input
    missing_features = [
        feature for feature in required_features
        if feature not in patient_data
    ]

    if missing_features:
        raise ValueError(
            f"Missing input features: {missing_features}"
        )

    # Prepare input data in the correct feature order
    input_df = pd.DataFrame(
        [[patient_data[feature] for feature in required_features]],
        columns=required_features
    )

    # Validate numeric values
    if input_df.isnull().any().any():
        raise ValueError("All input values are required.")

    if not all(
        pd.api.types.is_numeric_dtype(input_df[column])
        for column in input_df.columns
    ):
        raise ValueError("All input values must be numeric.")

    if not all(
        input_df[column].map(
            lambda value: pd.notna(value) and abs(value) != float("inf")
        ).all()
        for column in input_df.columns
    ):
        raise ValueError("Input values must be finite numbers.")

    if (input_df < 0).any().any():
        raise ValueError("Input values cannot be negative.")

    # Load model
    model = load_diabetes_model()

    # Generate prediction
    prediction = int(model.predict(input_df)[0])

    probability = float(
        model.predict_proba(input_df)[0][1]
    )

    result = {
        "prediction": prediction,
        "risk_probability": round(probability * 100, 2),
        "risk_category": (
            "Higher model-estimated risk"
            if prediction == 1
            else "Lower model-estimated risk"
        )
    }

    return result