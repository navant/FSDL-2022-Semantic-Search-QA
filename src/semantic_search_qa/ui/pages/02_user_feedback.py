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
        names=["text", "query", "best_predicted_answer", "user_preferred_answer"],
    )
    st.dataframe(df)
except FileNotFoundError:
    st.error(f"File not found: {feedback_file}")
