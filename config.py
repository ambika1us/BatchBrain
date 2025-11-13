import streamlit as st

MONGO_URI = st.secrets["MONGO_URI"]
DB_NAME = "quiz_db"
COLLECTION_NAME = "questions"
SCORE_COLLECTION = "quiz_scores"
