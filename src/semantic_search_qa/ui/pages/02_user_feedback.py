import pandas as pd
import streamlit as st

st.markdown("## Feedback")

feedback_file = st.text_input("Feedback file", "/tmp/feedback.tsv")
st.markdown("### Current User feedback")
try:
    df = pd.read_csv(
        feedback_file,
        sep="\t",
        header=None,
        names=[
            "text",
            "query",
            "best_predicted_answer",
            "best_predicted_answer_score",
            "best_predicted_answer_chunk",
            "user_preferred_answer",
            "user_preferred_answer_score",
            "user_preferred_answer_chunk",
        ],
    )
    st.dataframe(df)
except FileNotFoundError:
    st.error(f"File not found: {feedback_file}")
