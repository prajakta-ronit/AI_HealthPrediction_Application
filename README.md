# AI Health Prediction Application

A Streamlit application for managing patient information, reviewing blood reports, estimating diabetes risk with machine learning, and providing AI-generated health information. It is intended for educational and preliminary screening use, not clinical diagnosis.

## Features

- Patient registration and local record management using SQLite.
- Blood report upload and analysis, with downloadable reports.
- Diabetes risk estimates from a scikit-learn model trained on the Pima Indians Diabetes dataset.
- Gemini-generated explanations of selected laboratory values.
- A conversational health information assistant with language selection.

## Requirements

- Python and pip.
- A Gemini API key for AI remarks and the chat assistant. The other app features use the bundled model and do not require a Gemini key.

## Setup (Windows PowerShell)

From the project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set your key:

```dotenv
GEMINI_API_KEY=your_actual_gemini_api_key
```

Keep `.env` private; it is excluded by `.gitignore`.

## Run the application

```powershell
streamlit run app.py
```

Streamlit will print a local URL to open in your browser. The app creates its SQLite database at `database/ai_health_prediction.db` when it starts.

## Train the diabetes model

A trained model is included at `models/diabetes_prediction_model.pkl`. To retrain it using `datasets/diabetes.csv`:

```powershell
python backend/model_training.py
```

The training script compares logistic regression and random forest pipelines and saves the one with the higher ROC-AUC score to the `models` directory.

## Privacy and medical limitations

- Patient records are stored in the local SQLite database. Protect the computer and database file; do not use real patient information in an unsecured or public deployment.
- When using Gemini features, relevant laboratory values, patient context, chat history, and questions are sent to Google's Gemini API. Review Google's applicable privacy terms and obtain appropriate consent before using sensitive information.
- AI output and model predictions can be incomplete or incorrect. They are not diagnoses or treatment recommendations. Consult a qualified healthcare professional for medical decisions.
- The diabetes model is based on a specific dataset and may not generalize to other populations. It has not been established here as a clinically validated tool.

## Project structure

```text
app.py                  Streamlit application entry point
backend/                Health analysis, prediction, AI, and report logic
database/               SQLite database operations
datasets/               Diabetes training dataset
frontend/               Streamlit dashboard
models/                 Trained diabetes prediction model
assets/                 Dashboard styling
```
