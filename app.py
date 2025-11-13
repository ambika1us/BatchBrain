import streamlit as st
from pymongo import MongoClient
from config import MONGO_URI, DB_NAME, COLLECTION_NAME,SCORE_COLLECTION
import datetime

import random

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# Load and shuffle 15 random questions
if "quiz_questions" not in st.session_state:
    all_questions = list(collection.find({}, {"_id": 0}))
    st.session_state.quiz_questions = random.sample(all_questions, 15)
    st.session_state.answers = [None] * 15
    st.session_state.submitted = False

st.title("🧠 Data Communication Quiz")
st.markdown("Answer all 15 questions and submit at the end.")
# Collect user identity
if "user_info" not in st.session_state:
    st.session_state.user_info = {"name": "", "email": ""}

st.session_state.user_info["name"] = st.text_input("Enter your name", value=st.session_state.user_info["name"])
st.session_state.user_info["email"] = st.text_input("Enter your email", value=st.session_state.user_info["email"])

for i, q in enumerate(st.session_state.quiz_questions):
    st.subheader(f"Q{i+1}: {q['question']}")

    # Determine the index of the previously selected answer (if any)
    index = (
        q["options"].index(st.session_state.answers[i])
        if st.session_state.answers[i] in q["options"]
        else 0
    )

    # Display the radio button and store the selected answer
    selected = st.radio(
        f"Choose your answer for Q{i + 1}",
        q["options"],
        index=index,
        key=f"q{i}"
    )

    st.session_state.answers[i] = selected


# Submit button
if not st.session_state.submitted:
    if st.button("Submit Quiz"):
        st.session_state.submitted = True
        st.rerun()

# Show results
if st.session_state.submitted:
    score = 0
    st.subheader("📊 Results")
    for i, q in enumerate(st.session_state.quiz_questions):
        correct_index = q["answer"][0]
        correct_option = q["options"][correct_index]
        user_answer = st.session_state.answers[i]
        is_correct = user_answer == correct_option

        st.markdown(f"**Q{i+1}: {q['question']}**")
        st.markdown(f"- Your answer: `{user_answer}`")
        st.markdown(f"- Correct answer: `{correct_option}`")
        if is_correct:
            st.success("✅ Correct")
            score += 1
        else:
            st.error("❌ Incorrect")
            st.info(f"Explanation: {q['explanation']}")

    st.success(f"🎉 Your final score: {score} / 15")

    if st.button("Restart Quiz"):
        del st.session_state.quiz_questions
        del st.session_state.answers
        del st.session_state.submitted
        st.rerun()

    # Log score to MongoDB
    score_data = {
        "timestamp": datetime.datetime.utcnow(),
        "name": st.session_state.user_info["name"],
        "email": st.session_state.user_info["email"],
        "score": score,
        "total": len(st.session_state.quiz_questions),
        "answers": st.session_state.answers,
        "questions": [q["question"] for q in st.session_state.quiz_questions]
    }

    if not st.session_state.submitted:
        if st.button("Submit Quiz"):
            if not st.session_state.user_info["name"] or not st.session_state.user_info["email"]:
                st.warning("Please enter both name and email before submitting.")
            else:
                st.session_state.submitted = True
                st.rerun()

    db[SCORE_COLLECTION].insert_one(score_data)
    st.success("✅ Your score has been logged to the database.")
