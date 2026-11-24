from backend.ai_health_api import generate_health_remarks

try:
    remarks = generate_health_remarks(
        date_of_birth="15/06/1995",
        glucose=95,
        haemoglobin=13.5,
        cholesterol=180
    )

    print("\nGemini AI Response:")
    print("-------------------")
    print(remarks)

except Exception as e:
    print("Gemini API Error:", e)