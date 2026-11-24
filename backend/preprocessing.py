import pandas as pd

from sklearn.impute import SimpleImputer


def load_diabetes_dataset():

    dataset_path = "datasets/diabetes.csv"

    df = pd.read_csv(dataset_path)

    return df


def preprocess_diabetes_dataset():

    df = load_diabetes_dataset()

    # Columns containing invalid zero measurements
    invalid_zero_columns = [
        "Glucose",
        "BloodPressure",
        "SkinThickness",
        "Insulin",
        "BMI"
    ]

    # Replace invalid zeros with NaN
    for column in invalid_zero_columns:
        df[column] = df[column].replace(0, float("nan"))

    # Impute missing measurements using median values
    imputer = SimpleImputer(strategy="median")

    df[invalid_zero_columns] = imputer.fit_transform(
        df[invalid_zero_columns]
    )

    return df


if __name__ == "__main__":

    processed_df = preprocess_diabetes_dataset()

    print("Dataset preprocessing completed!")

    print("\nDataset Shape:")
    print(processed_df.shape)

    print("\nMissing Values:")
    print(processed_df.isnull().sum())

    print("\nProcessed Dataset:")
    print(processed_df.head())