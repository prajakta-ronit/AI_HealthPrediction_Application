import streamlit as st

from frontend.dashboard import dashboard

from database.db import initialize_database


st.set_page_config(
    page_title="AI Health Prediction Application",
    page_icon="🩺",
    layout="wide"
)

MODEL_CANDIDATES = ["gemini-3.5-flash-lite"]


def main():

    initialize_database()
    dashboard()


if __name__ == "__main__":

    main()