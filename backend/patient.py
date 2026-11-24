import streamlit as st
import pandas as pd
import re
import math 

from datetime import datetime, date
from backend.ai_health_api import generate_health_remarks

from database.db import (
    add_patient,
    get_all_patients,
    update_patient,
    delete_patient,
    is_patient_name_duplicate
)


def _safe_text(value):
    if value is None:
        return ""
    return str(value)


def _safe_float(value, default=0.0):
    if value is None or value == "":
        return float(default)
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def validate_patient_data(
    full_name,
    dob,
    email,
    glucose,
    haemoglobin,
    cholesterol
):

    errors = []

    # Full Name validation
    if not full_name.strip():
        errors.append("Full Name is required.")

    elif len(full_name.strip()) < 2:
        errors.append("Full Name must contain at least 2 characters.")

    # Date of Birth validation
    try:
        if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", dob):
            raise ValueError

        dob_date = datetime.strptime(
            dob, "%d/%m/%Y"
        ).date()

        if dob_date > date.today():
            errors.append("Date of Birth cannot be in the future.")

    except ValueError:
        errors.append(
            "Enter a valid Date of Birth in DD/MM/YYYY format."
        )

    # Email validation
    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    if not re.fullmatch(email_pattern, email.strip()):
        errors.append("Enter a valid email address.")

    # Numeric validation
    values = {
        "Glucose": (glucose, 1000),
        "Haemoglobin": (haemoglobin, 30),
        "Cholesterol": (cholesterol, 1000)
    }

    for name, (value, maximum) in values.items():

        if not isinstance(value, (int, float)):
            errors.append(f"{name} must be numeric.")

        elif not math.isfinite(value):
            errors.append(f"{name} must be a finite number.")

        elif value <= 0 or value > maximum:
            errors.append(
                f"{name} must be greater than 0 and "
                f"not exceed {maximum}."
            )

    return errors


def patient_registration():

    tab1, tab2 = st.tabs(["New Patient Registration", "Patient Records"])

    # CREATE PATIENT
    with tab1:

        st.subheader("New Patient Registration")

        with st.form("patient_registration_form"):

            full_name = st.text_input("Full Name")

            date_of_birth = st.text_input(
                "Date of Birth (DD/MM/YYYY)",
                placeholder="DD/MM/YYYY"
            )

            email = st.text_input("Email Address")

            col1, col2, col3 = st.columns(3)

            with col1:
                glucose = st.number_input(
                    "Glucose (mg/dL)", min_value=0.0
                )

            with col2:
                haemoglobin = st.number_input(
                    "Haemoglobin (g/dL)", min_value=0.0
                )

            with col3:
                cholesterol = st.number_input(
                    "Cholesterol (mg/dL)", min_value=0.0
                )

            submitted = st.form_submit_button(
                "Register Patient",
                use_container_width=True
            )

            if submitted:

                errors = validate_patient_data(
                    full_name,
                    date_of_birth,
                    email,
                    glucose,
                    haemoglobin,
                    cholesterol
                )

                if errors:
                    for error in errors:
                        st.error(error)

                else:
                    if is_patient_name_duplicate(full_name):
                        st.error("Patient already registered.")
                    else:
                        try:
                            with st.spinner("Generating AI health remarks..."):
                                try:
                                    remarks = generate_health_remarks(
                                        date_of_birth=date_of_birth,
                                        glucose=glucose,
                                        haemoglobin=haemoglobin,
                                        cholesterol=cholesterol
                                    )

                                except Exception as ai_error:
                                    remarks = "AI analysis unavailable. Please retry."
                                    st.warning(f"AI analysis failed: {ai_error}")

                            patient_id = add_patient(
                                full_name.strip(),
                                date_of_birth,
                                email.strip().lower(),
                                glucose,
                                haemoglobin,
                                cholesterol,
                                remarks
                            )

                            if patient_id is None:
                                st.error("Patient already registered.")
                            else:
                                st.success(
                                    f"Patient registered successfully! ID: {patient_id}"
                                )

                                if not remarks.startswith("AI analysis unavailable"):
                                    st.info("AI health remarks generated successfully.")

                        except Exception as e:
                            if "UNIQUE constraint failed" in str(e):
                                st.error("Email already registered.")
                            else:
                                st.error(f"Registration failed: {e}")

    # READ, UPDATE AND DELETE
    with tab2:

        st.subheader("Patient Records")

        patients = get_all_patients()

        if not patients:

            st.info("No patient records available.")

        else:

            search = st.text_input(
                "Search by name or email"
            )

            search_text = _safe_text(search).lower()

            filtered_patients = [
                p for p in patients
                if search_text in _safe_text(p.get("full_name")).lower()
                or search_text in _safe_text(p.get("email")).lower()
            ]

            if filtered_patients:

                display_data = pd.DataFrame([
                    {
                        "Test": p.get("id"),
                        "Full Name": _safe_text(p.get("full_name")),
                        "DOB": _safe_text(p.get("date_of_birth")),
                        "Email": _safe_text(p.get("email")),
                        "Glucose": p.get("glucose"),
                        "Haemoglobin": p.get("haemoglobin"),
                        "Cholesterol": p.get("cholesterol"),
                        "Remarks": _safe_text(p.get("remarks"))
                    }
                    for p in filtered_patients
                ])

                st.dataframe(
                    display_data,
                    use_container_width=True,
                    hide_index=True
                )

                patient_options = {
                    f"{_safe_text(p.get('full_name'))} (ID: {p.get('id')})": p
                    for p in filtered_patients
                }

                selected = st.selectbox(
                    "Select Patient to Manage",
                    list(patient_options.keys())
                )

                patient = patient_options[selected]

                st.divider()

                edit_tab, delete_tab = st.tabs([
                    "Edit Patient",
                    "Delete Patient"
                ])

                # UPDATE
                with edit_tab:

                    st.subheader("Update Patient Details")

                    with st.form("edit_patient_form"):

                        name = st.text_input(
                            "Full Name",
                            value=_safe_text(patient.get("full_name"))
                        )

                        dob = st.text_input(
                            "Date of Birth",
                            value=_safe_text(patient.get("date_of_birth"))
                        )

                        patient_email = st.text_input(
                            "Email Address",
                            value=_safe_text(patient.get("email"))
                        )

                        c1, c2, c3 = st.columns(3)

                        with c1:
                            glucose = st.number_input(
                                "Glucose (mg/dL)",
                                min_value=0.0,
                                value=_safe_float(patient.get("glucose"))
                            )

                        with c2:
                            haemoglobin = st.number_input(
                                "Haemoglobin (g/dL)",
                                min_value=0.0,
                                value=_safe_float(patient.get("haemoglobin"))
                            )

                        with c3:
                            cholesterol = st.number_input(
                                "Cholesterol (mg/dL)",
                                min_value=0.0,
                                value=_safe_float(patient.get("cholesterol"))
                            )

                        update_button = st.form_submit_button(
                            "Save Changes",
                            use_container_width=True
                        )

                        if update_button:

                            errors = validate_patient_data(
                                name,
                                dob,
                                patient_email,
                                glucose,
                                haemoglobin,
                                cholesterol
                            )

                            if errors:

                                for error in errors:
                                    st.error(error)

                            else:
                                if is_patient_name_duplicate(
                                    name,
                                    exclude_patient_id=patient.get("id")
                                ):
                                    st.error("Patient already registered.")
                                else:
                                    try:
                                        with st.spinner("Regenerating AI health remarks..."):
                                            try:
                                                remarks = generate_health_remarks(
                                                    date_of_birth=dob,
                                                    glucose=glucose,
                                                    haemoglobin=haemoglobin,
                                                    cholesterol=cholesterol
                                                )

                                            except Exception as ai_error:
                                                remarks = "AI analysis unavailable. Please retry."
                                                st.warning(f"AI analysis failed: {ai_error}")

                                        updated = update_patient(
                                            patient.get("id"),
                                            name.strip(),
                                            dob,
                                            patient_email.strip().lower(),
                                            glucose,
                                            haemoglobin,
                                            cholesterol,
                                            remarks
                                        )

                                        if updated:
                                            st.success("Patient updated successfully!")

                                            if not remarks.startswith("AI analysis unavailable"):
                                                st.info("AI health remarks regenerated successfully.")
                                        else:
                                            st.error("Patient already registered.")

                                        st.rerun()
                                    except Exception as e:
                                        if "UNIQUE constraint failed" in str(e):
                                            st.error("Email already belongs to another patient.")
                                        else:
                                            st.error(f"Update failed: {e}")

                # DELETE
                with delete_tab:

                    st.subheader("Delete Patient Record")

                    st.warning(
                        f"You are about to delete "
                        f"{_safe_text(patient.get('full_name'))}'s record."
                    )

                    confirm = st.checkbox(
                        "I confirm that I want to delete this record.",
                        key=f"confirm_delete_{patient.get('id')}"
                    )

                    if st.button(
                        "Delete Patient",
                        disabled=not confirm,
                        type="primary"
                    ):

                        deleted = delete_patient(patient.get("id"))

                        if deleted:
                            st.success(
                                "Patient deleted successfully. Patient IDs have been reordered."
                            )
                            st.rerun()

            else:

                st.info("No matching patient records found.")