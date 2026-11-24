import os
import time
from datetime import datetime, date

from dotenv import load_dotenv

try:
    from google import genai
except ImportError as exc:
    raise ImportError(
        "Gemini SDK is not installed. Install it with: "
        "./venv/Scripts/python -m pip install google-genai"
    ) from exc


# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-3.5-flash-lite",
]
REQUEST_TIMEOUT_MS = 15_000


def calculate_age(date_of_birth):

    dob = datetime.strptime(
        date_of_birth,
        "%d/%m/%Y"
    ).date()

    today = date.today()

    age = today.year - dob.year

    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    return age


def generate_health_remarks(
    date_of_birth,
    glucose,
    haemoglobin,
    cholesterol
):

    if not API_KEY:
        raise ValueError(
            "Gemini API key is missing. "
            "Please configure GEMINI_API_KEY in .env."
        )

    age = calculate_age(date_of_birth)

    client = genai.Client(
        api_key=API_KEY,
        http_options={"timeout": REQUEST_TIMEOUT_MS}
    )

    prompt = f"""
    You are an AI health information assistant.

    Review the following patient laboratory values:

    Age: {age} years
    Glucose: {glucose} mg/dL
    Haemoglobin: {haemoglobin} g/dL
    Total Cholesterol: {cholesterol} mg/dL

    Provide a preliminary health screening explanation.

    Requirements:

    1. Explain what each value may indicate.
    2. Highlight values that may need medical attention.
    3. Mention that glucose interpretation depends on
       whether the sample was fasting or non-fasting.
    4. Do not diagnose diseases.
    5. Do not claim a disease is present.
    6. Do not invent missing medical information.
    7. Explain that laboratory reference ranges vary.
    8. Recommend consultation with a qualified doctor
       for interpretation.

    Return a concise, patient-friendly explanation
    in approximately 100-130 words.
    """

    last_error = None

    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "temperature": 0.2,
                    "max_output_tokens": 300,
                }
            )

            remarks = getattr(response, "text", None)

            if not remarks:
                try:
                    remarks = response.candidates[0].content.parts[0].text
                except Exception:
                    remarks = None

            if not remarks:
                raise ValueError(
                    "The AI service returned an empty response."
                )

            return remarks.strip()

        except Exception as exc:
            last_error = exc
            status_code = getattr(exc, "status_code", None)
            code = getattr(exc, "code", None)
            transient_error = status_code in {404, 429, 500, 503} or code in {404, 429, 500, 503}

            if not transient_error:
                raise

            time.sleep(1)

    raise RuntimeError(
        f"Gemini API request failed across models: {last_error}"
    ) from last_error

def ask_health_assistant(
    question,
    patient_context=None,
    chat_history=None,
    language="English"
):
    if not API_KEY:
        raise ValueError(
            "Gemini API key is missing. "
            "Please configure GEMINI_API_KEY in .env."
        )

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    client = genai.Client(
        api_key=API_KEY,
        http_options={"timeout": REQUEST_TIMEOUT_MS}
    )

    # Prepare conversation history
    history_text = ""

    if chat_history:
        for message in chat_history[-10:]:
            role = message.get("role", "user")
            content = message.get("content", "")

            history_text += (
                f"\n{role.upper()}: {content}"
            )

    # Prepare patient context
    context_text = ""

    if patient_context:
        context_text = f"""
        Patient laboratory information:

        {patient_context}

        Use these values only to explain the
        available laboratory information.
        Do not assume missing medical details.
        """

    prompt = f"""
    You are a friendly AI Health Information Assistant.

    Your responsibility is to explain health and
    laboratory-related information in simple language.

    {context_text}

    Previous conversation:
    {history_text}

    Current question:
    {question}

    Instructions:

    Instructions:
    1. Respond strictly in {language}.
    2. Answer in simple, understandable language.
    3. Explain medical terminology when necessary.
    4. Explain glucose, haemoglobin and cholesterol
       when relevant.
    5. Do not diagnose diseases.
    6. Do not prescribe medicines or treatments.
    7. Do not invent patient information.
    8. Explain uncertainty whenever information is missing.
    9. Recommend consulting a qualified healthcare
   professional for medical concerns.
    10. If the question describes an emergency,
    recommend seeking immediate medical assistance.
    11. Keep responses concise and informative.
    12. Use language that is easy for the patient to understand.

    Remember that you provide health information,
    not professional medical advice.
    """

    last_error = None

    for model_name in MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "temperature": 0.2,
                    "max_output_tokens": 500,
                }
            )

            answer = getattr(response, "text", None)

            if answer and answer.strip():
                return answer.strip()

            raise ValueError(
                "Gemini returned an empty response."
            )

        except Exception as exc:
            last_error = exc

            status_code = getattr(exc, "status_code", None)
            code = getattr(exc, "code", None)

            transient_error = (
                status_code in {404, 429, 500, 503}
                or code in {404, 429, 500, 503}
            )

            if not transient_error:
                raise

            time.sleep(1)

    raise RuntimeError(
        f"Gemini chatbot request failed: {last_error}"
    ) from last_error