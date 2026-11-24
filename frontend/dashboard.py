from backend.health_analysis import analyze_blood_report
from backend.blood_analysis import process_blood_report
from backend.ai_health_api import ask_health_assistant
from backend.diabetes_prediction import predict_diabetes_risk
from backend.report_generator import generate_medical_report
from database.db import (
    get_all_patients,
    save_blood_report
)
from backend.patient import patient_registration
import streamlit as st
import pandas as pd
import plotly.express as px
import os


def load_css():

    css_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "assets",
        "style.css"
    )

    if os.path.exists(css_path):

        with open(css_path) as f:

            st.html(
                f"<style>{f.read()}</style>",
            )


def dashboard():

    load_css()

    # --------------------------------
    # TOP NAVIGATION
    # --------------------------------

    col1, col2 = st.columns([2, 3])

    with col1:

        st.html(
            """
            <h2 style="color:#087F8C;">
                🩺 AI Health Prediction Application
            </h2>
            <p style="color:#718096;">
                Intelligent Healthcare Platform
            </p>
            """
        )

    with col2:

        st.html(
            """
            <div style="text-align:right;padding-top:15px;">
                <span style="color:#087F8C;font-weight:600;">
                    ● AI SYSTEM ONLINE
                </span>
                &nbsp;&nbsp;&nbsp;
                <span style="color:#718096;">
                    Healthcare Analytics
                </span>
            </div>
            """
        )

    st.divider()

    # --------------------------------
    # NAVIGATION MENU
    # --------------------------------

    if "selected_page" not in st.session_state:
        st.session_state.selected_page = "Dashboard"

    if "quick_page" in st.session_state:
        st.session_state.selected_page = st.session_state.pop("quick_page")

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Patients",
            "Upload Report",
            "Health Analysis",
            "AI Assistant",
            "Diabetes Prediction",
            "Reports"
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="selected_page"
    )

    st.divider()

    # Ensure this is available even when no patient is selected.
    patient_context = None

    # --------------------------------
    # DASHBOARD PAGE
    # --------------------------------

    if page == "Dashboard":

        st.html(
            """
            <div class="welcome-card">

                <h2>Welcome to AI Health Prediction Application 👋</h2>

                <p>
                Your intelligent healthcare companion.
                Analyze blood reports, understand health
                parameters and explore AI-powered health insights.
                </p>

            </div>
            """
        )

        st.subheader("Dashboard Overview")

        st.write(
            "Monitor your patient records and health analysis."
        )

        # STATISTICS

        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

        patients = get_all_patients()

        total_patients = len(patients)

        def calculate_average(patients, column):
            values = []

            for patient in patients:
                value = patient.get(column)

                if value is not None and value != "":
                    try:
                        values.append(float(value))
                    except (ValueError, TypeError):
                        continue

            if values:
                return sum(values) / len(values)

            return 0

        avg_glucose = calculate_average(patients, "glucose")
        avg_haemoglobin = calculate_average(patients, "haemoglobin")
        avg_cholesterol = calculate_average(patients, "cholesterol")

        metrics = [
            ("Total Patients", str(total_patients), "👥"),
            ("Avg. Glucose", f"{avg_glucose:.1f} mg/dL", "🩸"),
            ("Avg. Haemoglobin", f"{avg_haemoglobin:.1f} g/dL", "🧪"),
            ("Avg. Cholesterol", f"{avg_cholesterol:.1f} mg/dL", "❤️")
        ]

        for col, metric in zip(
            [metric_col1, metric_col2, metric_col3, metric_col4],
            metrics
        ):
            with col:
                st.html(
                    f"""
                    <div class="dashboard-card">

                        <div class="card-title">
                            {metric[2]} {metric[0]}
                        </div>

                        <div class="card-value">
                            {metric[1]}
                        </div>

                    </div>
                    """
                )

                st.write("")

        # MAIN CONTENT

        left, right = st.columns([2, 1])

        with left:

            st.subheader("Health Monitoring")

            st.html(
                """
                <div class="dashboard-card">

                    <h3>Blood Report Analytics</h3>

                    <p style="color:#718096;">
                    Upload patient blood test results to
                    visualize and analyze important health
                    parameters.
                    </p>

                    <ul style="color:#526777;line-height:2;">

                        <li>Blood Glucose Analysis</li>
                        <li>Hemoglobin Monitoring</li>
                        <li>Cholesterol Analysis</li>
                        <li>Kidney Function Assessment</li>
                        <li>Liver Function Assessment</li>

                    </ul>

                </div>
                """
            )

        st.subheader("Quick Actions")

        c1, c2, c3 = st.columns(3)

        with c1:

            if st.button(
                "➕ Register Patient",
                use_container_width=True
            ):

                st.session_state.quick_page = "Patients"
                st.rerun()

        with c2:

            if st.button(
                "📤 Upload Blood Report",
                use_container_width=True
            ):

                st.session_state.quick_page = "Upload Report"
                st.rerun()

        with c3:

            if st.button(
                "🤖 AI Health Assistant",
                use_container_width=True
            ):

                st.session_state.quick_page = "AI Assistant"
                st.rerun()

    # --------------------------------
    # PATIENTS
    # --------------------------------

    elif page == "Patients":

        patient_registration()

    # --------------------------------
    # UPLOAD REPORT
    # --------------------------------

    elif page == "Upload Report":

        st.title("Blood Report Analysis")

        st.write(
            "Upload and process patient blood test results."
        )

        st.divider()

        patients = get_all_patients()

        if not patients:

            st.warning(
                "Please register a patient before uploading a report."
            )

        else:

            patient_options = {
                f"{p['full_name']} ({p['patient_id']})": p['patient_id']
                for p in patients
            }

            selected_patient = st.selectbox(
                "Select Patient",
                list(patient_options.keys())
            )

            patient_id = patient_options[selected_patient]

            st.subheader("Upload Blood Test Report")

            uploaded_file = st.file_uploader(
                "Choose CSV Blood Report",
                type=["csv"]
            )

            if uploaded_file:

                try:

                    df = pd.read_csv(uploaded_file)

                    st.subheader("Uploaded Report Preview")

                    st.dataframe(
                        df,
                        use_container_width=True
                    )

                    if st.button(
                        "Process Blood Report",
                        use_container_width=True
                    ):

                        processed_df = process_blood_report(df)

                        report_id = save_blood_report(
                            patient_id,
                            uploaded_file.name,
                            processed_df
                        )

                        st.success(
                            "Blood report processed successfully!"
                        )

                        st.write("Report ID:", report_id)

                        st.subheader(
                            "Processed Blood Parameters"
                        )

                        st.dataframe(
                            processed_df,
                            use_container_width=True,
                            hide_index=True
                        )

                        st.metric(
                            "Parameters Processed",
                            len(processed_df)
                        )

                        st.info(
                            "Your blood test data has been "
                            "saved successfully. Medical "
                            "interpretation will be added in "
                            "the next development stages."
                        )

                except Exception as e:

                    st.error(
                        f"Report processing failed: {e}"
                    )

    # --------------------------------
    # HEALTH ANALYSIS
    # --------------------------------

    elif page == "Health Analysis":

        st.title("🩺 Health Analysis")
        st.write("Review and understand patient blood test results.")

        patients = get_all_patients()

        if not patients:
            st.warning("Please register a patient first.")

        else:
            patient_options = {
                f"{p['full_name']} ({p['patient_id']})": p
                for p in patients
            }

            selected_patient = st.selectbox(
                "Select Patient",
                list(patient_options.keys())
            )

            patient = patient_options[selected_patient]

            st.info(
                f"Patient: {patient['full_name']} | "
                f"Age: {patient['age']} | "
                f"Gender: {patient['gender']}"
            )

            st.write(
                "Upload a blood report to perform health analysis."
            )

            uploaded_file = st.file_uploader(
                "Upload Blood Report CSV",
                type=["csv"],
                key="health_analysis_upload"
            )

            if uploaded_file:

                try:
                    df = pd.read_csv(uploaded_file)

                    processed_df = process_blood_report(df)

                    if st.button("Analyze Health Report"):

                        results = analyze_blood_report(
                            processed_df,
                            patient["gender"]
                        )

                        st.subheader("Analysis Results")

                        st.dataframe(
                            results,
                            use_container_width=True,
                            hide_index=True
                        )

                        normal = (results["Status"] == "Normal").sum()
                        low = (results["Status"] == "Low").sum()
                        high = (results["Status"] == "High").sum()
                        review = (
                            results["Status"] == "Needs Review"
                        ).sum()

                        col1, col2, col3, col4 = st.columns(4)

                        col1.metric("Normal", normal)
                        col2.metric("Low", low)
                        col3.metric("High", high)
                        col4.metric("Needs Review", review)

                        st.divider()

                        st.subheader("Health Status Overview")

                        status_data = pd.DataFrame({
                            "Status": [
                                "Normal",
                                "Low",
                                "High",
                                "Needs Review"
                            ],
                            "Count": [
                                normal,
                                low,
                                high,
                                review
                            ]
                        })

                        status_data = status_data[
                            status_data["Count"] > 0
                        ]

                        if not status_data.empty:

                            fig = px.pie(
                                status_data,
                                names="Status",
                                values="Count",
                                hole=0.55,
                                title="Blood Test Status Distribution",
                                color="Status",
                                color_discrete_map={
                                    "Normal": "#16A085",
                                    "Low": "#3498DB",
                                    "High": "#E74C3C",
                                    "Needs Review": "#F39C12"
                                }
                            )

                            fig.update_layout(
                                template="plotly_white",
                                height=400
                            )

                            st.plotly_chart(
                                fig,
                                use_container_width=True
                            )
                        else:
                            st.info("No analysis results available for visualization.")

                        st.warning(
                            "These results are preliminary screening "
                            "indicators, not medical diagnoses. "
                            "Consult a qualified healthcare professional."
                        )

                except Exception as e:
                    st.error(f"Health analysis failed: {e}")

    # --------------------------------
    # AI ASSISTANT
    # --------------------------------


    elif page == "AI Assistant":

        st.title("🤖 AI Health Assistant")

        st.write(
            "Your intelligent assistant for understanding "
            "health information and laboratory results."
        )

        st.divider()
        # LANGUAGE SELECTION

        st.markdown("### 🌐 Choose Response Language")

        language = st.selectbox(
            "Select your preferred language",
            [
                "English",
                "Hindi",
                "Marathi",
                "Spanish",
                "German",
                "French"
            ]
        )
        st.success(f"🌐 AI responses will be generated in {language}.")
        # PATIENT SELECTION

        patients = get_all_patients()

        patient_options = {
            "General Health Questions": None
        }

        for p in patients:
            label = (
                f"{p['full_name']} (ID: {p['id']})"
            )
            patient_options[label] = p

        selected_patient = st.selectbox(
            "Select Patient (Optional)",
            list(patient_options.keys())
        )

        patient = patient_options[selected_patient]

        # PREPARE PATIENT CONTEXT

        patient_context = None

        if patient:

            patient_context = f"""
            Glucose: {patient.get('glucose')} mg/dL
            Haemoglobin: {patient.get('haemoglobin')} g/dL
            Total Cholesterol: {patient.get('cholesterol')} mg/dL
            """
            st.warning(
                    "Privacy Notice: When you ask a question with a patient "
                    "selected, their laboratory values are shared with "
                    "Google Gemini to generate an AI response. "
                    "Do not enter personally identifiable information "
                    "in your questions."
            )
            st.info(
                f"Patient selected: {patient['full_name']}"
            )

        else:

            st.info(
                "You are chatting in General Health Mode."
            )

        st.divider()

        # RESET CHAT WHEN PATIENT CHANGES

        context_id = (
            patient.get("id") if patient else "general"
        )

        if st.session_state.get(
            "assistant_context_id"
        ) != context_id:

            st.session_state.assistant_context_id = context_id
            st.session_state.health_assistant_messages = []

        if "health_assistant_messages" not in st.session_state:
            st.session_state.health_assistant_messages = []


        # CLEAR CHAT BUTTON

        col1, col2 = st.columns([1, 5])

        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.health_assistant_messages = []
                st.rerun()

        # DISPLAY CHAT HISTORY

        if not st.session_state.health_assistant_messages:

            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(
                    """
                    ### 👋 Welcome to AI Health Assistant!

                    I'm here to help you understand health information
                    and laboratory reports in simple language.

                    **You can ask me about:**
                    - 🩸 Blood glucose
                    - 🧪 Haemoglobin
                    - ❤️ Cholesterol
                    - 🥗 General health and wellness

                    Select your preferred language and start chatting!
                    """
                )

        for message in st.session_state.health_assistant_messages:
            with st.chat_message(
                message["role"],
                avatar="🤖" if message["role"] == "assistant" else "👤"
            ):
                st.markdown(message["content"])

        # CHAT INPUT

        st.divider()

        # SUGGESTED QUESTIONS

        st.markdown("### 💡 Suggested Questions")

        suggested_questions = [
            "What does glucose mean?",
            "Why is haemoglobin important?",
            "What is cholesterol?",
            "How can I maintain healthy blood sugar levels?"
        ]

        col1, col2 = st.columns(2)

        selected_question = None

        with col1:
            if st.button(suggested_questions[0], use_container_width=True):
                selected_question = suggested_questions[0]

            if st.button(suggested_questions[1], use_container_width=True):
                selected_question = suggested_questions[1]

        with col2:
            if st.button(suggested_questions[2], use_container_width=True):
                selected_question = suggested_questions[2]

            if st.button(suggested_questions[3], use_container_width=True):
                selected_question = suggested_questions[3]

        st.divider()

        # CHAT INPUT

        question = st.chat_input(
            "Ask your health-related question..."
        )

        if selected_question:
            question = selected_question

        if question:

            st.session_state.health_assistant_messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):

                with st.spinner("Gemini is thinking..."):

                    try:

                        chat_history = (
                            st.session_state.health_assistant_messages[:-1]
                        )

                        answer = ask_health_assistant(
                            question=question,
                            patient_context=patient_context,
                            chat_history=chat_history,
                            language=language
                        )

                        st.markdown(answer)

                        st.session_state.health_assistant_messages.append(
                            {
                                "role": "assistant",
                                "content": answer
                            }
                        )

                    except Exception:

                        error_message = (
                            "I'm unable to process your question "
                            "right now. Please try again later."
                        )

                        st.error(error_message)

                        st.session_state.health_assistant_messages.append(
                            {
                                "role": "assistant",
                                "content": error_message
                            }
                        )

        st.divider()

        st.caption(
            "⚕️ AI-generated responses are for educational "
            "purposes only and are not a substitute for "
            "professional medical advice."
        )


    # --------------------------------
    # DIABETES PREDICTION PAGE
    # --------------------------------

    elif page == "Diabetes Prediction":

        st.title("🩺 Diabetes Risk Prediction")

        st.write(
            "Enter the required health parameters "
            "to generate an educational ML prediction."
        )

        st.warning(
            "This model is trained on the Pima Indians "
            "Diabetes dataset, which represents a limited "
            "population of women aged 21 and above. "
            "It is not suitable for clinical diagnosis."
        )

        with st.form("diabetes_prediction_form"):

            st.subheader("Patient Health Parameters")

            col1, col2 = st.columns(2)

            with col1:

                pregnancies = st.number_input(
                    "Pregnancies",
                    min_value=0,
                    max_value=20,
                    value=2
                )

                glucose = st.number_input(
                    "Glucose (mg/dL)",
                    min_value=1.0,
                    max_value=300.0,
                    value=120.0
                )

                blood_pressure = st.number_input(
                    "Blood Pressure (mmHg)",
                    min_value=1.0,
                    max_value=200.0,
                    value=80.0
                )

                skin_thickness = st.number_input(
                    "Skin Thickness (mm)",
                    min_value=1.0,
                    max_value=100.0,
                    value=25.0
                )

            with col2:

                insulin = st.number_input(
                    "Insulin (mu U/ml)",
                    min_value=1.0,
                    max_value=900.0,
                    value=100.0
                )

                bmi = st.number_input(
                    "BMI",
                    min_value=1.0,
                    max_value=80.0,
                    value=28.5
                )

                diabetes_pedigree = st.number_input(
                    "Diabetes Pedigree Function",
                    min_value=0.0,
                    max_value=3.0,
                    value=0.5
                )

                age = st.number_input(
                    "Age (Years)",
                    min_value=21,
                    max_value=100,
                    value=35
                )

            submitted = st.form_submit_button(
                "Predict Diabetes Risk",
                use_container_width=True
            )

        if submitted:

            patient_data = {
                "Pregnancies": pregnancies,
                "Glucose": glucose,
                "BloodPressure": blood_pressure,
                "SkinThickness": skin_thickness,
                "Insulin": insulin,
                "BMI": bmi,
                "DiabetesPedigreeFunction": diabetes_pedigree,
                "Age": age
            }

            try:

                result = predict_diabetes_risk(patient_data)

                st.divider()

                st.subheader("Prediction Results")

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "Model Prediction",
                        result["risk_category"]
                    )

                with col2:

                    st.metric(
                        "Model Probability",
                        f'{result["risk_probability"]}%'
                    )

                st.progress(
                    result["risk_probability"] / 100
                )

                st.info(
                    "This probability is the model's estimated "
                    "probability for the positive dataset class. "
                    "It is not a calibrated estimate of personal "
                    "diabetes risk."
                )

            except Exception as e:

                st.error(
                    f"Prediction failed: {str(e)}"
                )
    # --------------------------------
    # REPORTS
    # --------------------------------

    elif page == "Reports":

        st.title("📄 Medical Reports")

        st.write(
            "Generate and download individual patient medical reports."
        )

        patients = get_all_patients()

        if not patients:

            st.info("No patient records available. Please register a patient first.")

        else:

            patient_options = {
                f"{patient['full_name']} (ID: {patient['id']})": patient
                for patient in patients
            }

            selected_patient_name = st.selectbox(
                "Select Patient",
                list(patient_options.keys())
            )

            selected_patient = patient_options[selected_patient_name]

            st.divider()

            st.subheader("Patient Details")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Name:**", selected_patient["full_name"])
                st.write("**DOB:**", selected_patient["date_of_birth"])

            with col2:
                st.write("**Email:**", selected_patient["email"])
                st.write("**Glucose:**", selected_patient["glucose"])

            if st.button("Generate Medical Report"):

                try:
                    pdf_buffer = generate_medical_report(selected_patient)

                    st.download_button(
                        label="⬇️ Download Medical Report (PDF)",
                        data=pdf_buffer,
                        file_name=f"Medical_Report_{selected_patient['id']}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Report generation failed: {e}")