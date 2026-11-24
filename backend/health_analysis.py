import pandas as pd


# General adult reference ranges.
# Actual ranges may vary by laboratory, age, sex and clinical context.

REFERENCE_RANGES = {
    "Hemoglobin": {
        "Male": (13.5, 17.5),
        "Female": (12.0, 15.5)
    },
    "RBC": {
        "Male": (4.5, 5.9),
        "Female": (4.1, 5.1)
    },
    "WBC": (4000, 11000),
    "Platelets": (150000, 450000),
    "HbA1c": (0, 5.6),
    "Cholesterol": (0, 199),
    "HDL": (40, 999),
    "LDL": (0, 99),
    "Triglycerides": (0, 149),
    "Creatinine": {
        "Male": (0.7, 1.3),
        "Female": (0.6, 1.1)
    }
}


def analyze_blood_report(df, gender):

    results = []

    for _, row in df.iterrows():

        parameter = row["parameter"]
        value = float(row["value"])
        unit = row["unit"]

        if parameter not in REFERENCE_RANGES:
            status = "Needs Review"
            explanation = "No configured reference range is available."

        else:
            reference = REFERENCE_RANGES[parameter]

            if isinstance(reference, dict):
                reference = reference.get(gender)

            if reference is None:
                status = "Needs Review"
                explanation = "A suitable reference range is unavailable."

            else:
                low, high = reference

                if value < low:
                    status = "Low"
                    explanation = (
                        f"{parameter} is below the configured "
                        f"reference range of {low}-{high}."
                    )

                elif value > high:
                    status = "High"
                    explanation = (
                        f"{parameter} is above the configured "
                        f"reference range of {low}-{high}."
                    )

                else:
                    status = "Normal"
                    explanation = (
                        f"{parameter} is within the configured "
                        f"reference range of {low}-{high}."
                    )

        results.append({
            "Parameter": parameter,
            "Value": value,
            "Unit": unit,
            "Status": status,
            "Explanation": explanation
        })

    return pd.DataFrame(results)