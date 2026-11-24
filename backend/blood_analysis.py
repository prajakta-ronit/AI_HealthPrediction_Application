import pandas as pd


SUPPORTED_PARAMETERS = {
    "hemoglobin": "Hemoglobin",
    "hb": "Hemoglobin",
    "rbc": "RBC",
    "wbc": "WBC",
    "platelets": "Platelets",
    "platelet count": "Platelets",
    "glucose": "Glucose",
    "blood glucose": "Glucose",
    "hba1c": "HbA1c",
    "cholesterol": "Cholesterol",
    "total cholesterol": "Cholesterol",
    "hdl": "HDL",
    "ldl": "LDL",
    "triglycerides": "Triglycerides",
    "creatinine": "Creatinine",
    "urea": "Urea",
    "sgot": "SGOT",
    "ast": "SGOT",
    "sgpt": "SGPT",
    "alt": "SGPT"
}


def process_blood_report(df):

    df = df.copy()

    # Normalize column names

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Column aliases

    column_mapping = {

        "parameter": [
            "parameter",
            "test",
            "test_name",
            "parameter_name",
            "blood_test",
            "test_parameter"
        ],

        "value": [
            "value",
            "result",
            "test_result",
            "observed_value",
            "reading"
        ],

        "unit": [
            "unit",
            "units",
            "measurement_unit"
        ]

    }

    # Identify available columns

    rename_columns = {}

    for required, aliases in column_mapping.items():

        for alias in aliases:

            if alias in df.columns:

                rename_columns[alias] = required
                break

    df.rename(
        columns=rename_columns,
        inplace=True
    )

    # Validate columns

    required_columns = [
        "parameter",
        "value",
        "unit"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            f"Missing columns: {missing_columns}. "
            f"Available columns: {list(df.columns)}. "
            "Expected parameter, value and unit."
        )

    # Clean parameter names

    df["parameter"] = (
        df["parameter"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    df["parameter"] = df["parameter"].map(
        lambda x: SUPPORTED_PARAMETERS.get(
            x, x.title()
        ) if pd.notna(x) else x
    )

    # Convert values to numeric

    df["value"] = pd.to_numeric(
        df["value"],
        errors="coerce"
    )

    # Clean units

    df["unit"] = (
        df["unit"]
        .astype("string")
        .str.strip()
    )

    # Validation

    errors = []

    if df["parameter"].isna().any():

        errors.append("Missing parameter names.")

    if df["value"].isna().any():

        errors.append(
            "Missing or non-numeric test values."
        )

    if (df["value"].dropna() < 0).any():

        errors.append(
            "Negative test values detected."
        )

    if df["unit"].isna().any() or df["unit"].eq("").any():

        errors.append("Missing measurement units.")

    if df["parameter"].duplicated().any():

        errors.append(
            "Duplicate blood parameters detected."
        )

    if errors:

        raise ValueError("\n".join(errors))

    return df