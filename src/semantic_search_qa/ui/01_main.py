import csv
from io import StringIO
from typing import Optional

import pandas as pd
import streamlit as st
from jina import Client, Document


def clear_text():
    st.session_state["text"] = ""
    st.session_state["text_disabled"] = False


def extract_content(uploaded_file: Optional[st.runtime.uploaded_file_manager.UploadedFile]):
    if uploaded_file:
        # To convert to a string based IO:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        return stringio.read()
    else:
        return ""


def send_qa_request(content: str, query: str, host: str, port: int, endpoint: str = "/qa", n_of_results: int = 5):
    if content == "":
        st.warning("There's no text to send! Add a document or write/copy your text!")
        return
    st.write(f"N Results: {n_of_results}")
    client = Client(host=host, port=port)
    params = {"query": query, "n_of_results": n_of_results}
    st.session_state["results"] = client.post(endpoint, Document(content=content), parameters=params)
    clear_text()
    st.session_state["feedback_sent"] = False
    st.session_state["text_disabled"] = True


def save_feedback(file: str, text: str, query: str, best_predicted_answer: str, user_preferred_answer: str):
    with open(file, "a") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow([text, query, best_predicted_answer, user_preferred_answer])
    st.session_state["feedback_sent"] = True
    st.session_state["text_disabled"] = False


st.set_page_config(page_title="Semantic Question Answering (WIP)", page_icon="🎈", layout="wide")

st.title("Semantic Question Answering (WIP)")

with st.expander("ℹ️ - About", expanded=False):

    st.write(
        """     
-   A semantic QA for Finance articles done as part of the FSDL Course
-   More details TBD
-   Take a look at [streamlit-jina and this article](https://blog.streamlit.io/streamlit-jina-neural-search/)
	    """
    )

    st.markdown("")

st.header("## 📌 Upload a document or paste content")

c1, c2 = st.columns([2, 4])
with c1:
    uploaded_file = st.file_uploader("Pick a file")

    if uploaded_file is not None:
        st.session_state["text"] = extract_content(uploaded_file)
    else:
        st.session_state["text"] = ""

with c2:
    try:
        content = st.session_state["text"]
        content_disabled = st.session_state["text_disabled"]
    except KeyError:
        content = ""
        content_disabled = False

    text_content = st.text_area(
        "Content (max 500 words)", content, height=510, key="text_content", disabled=content_disabled
    )

with st.form("my-form"):
    c1, c2 = st.columns([4, 2])
    with c1:
        query = st.text_input("Query", "Who's increasing the rates?")
        n_of_results = st.slider("Number of Results", min_value=1, max_value=10, value=5)

    with c2:
        host = st.text_input("Host", "0.0.0.0")
        port = st.text_input("Port", 54321)

    req_args = {"content": text_content, "query": query, "host": host, "port": port, "n_of_results": n_of_results}

    submit_btn = st.form_submit_button(label="Fire!", on_click=send_qa_request, kwargs=req_args)

try:
    if st.session_state["feedback_sent"]:
        st.stop()
except KeyError:
    st.stop()

st.header("Results")

docs = st.session_state.results
for i, doc in enumerate(docs):
    st.markdown(f"### Answer {i}")
    st.info(f"{doc.text}")

st.markdown("## Feedback")


c1, c2 = st.columns([2, 2])

with c1:
    feedback_file = st.text_input("File to save feedback", "/tmp/feedback.tsv")
    user_best_answer = st.selectbox(
        "What do you think it's the best answer?", [str(i) for i in range(0, len(docs))] + ["Not Provided"]
    )
    with st.form("feedback-form"):
        feedback_data = {
            "file": feedback_file,
            "text": text_content,
            "query": query,
            "best_predicted_answer": docs[0].text,
            "user_preferred_answer": docs[int(user_best_answer)].text
            if user_best_answer != "Not Provided"
            else "Not Provided",
        }
        feedback_submit_btn = st.form_submit_button("Improve output!", on_click=save_feedback, kwargs=feedback_data)

with c2:
    st.markdown("### Current feedback")
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
