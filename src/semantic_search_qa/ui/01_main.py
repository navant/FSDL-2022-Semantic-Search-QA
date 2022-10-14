import csv
import os
from io import StringIO
from pathlib import Path
from time import sleep
from typing import Optional

import pandas as pd
import streamlit as st
import whylogs as why
from jina import Client, Document

from semantic_search_qa.ui.ui_utils import EXAMPLE_DOC
from semantic_search_qa.utils import pdf2text

current_doc = """""" if "text" not in st.session_state else st.session_state["text"]
current_query = """""" if "query_text" not in st.session_state else st.session_state["query_text"]


def clear_text():
    st.session_state["text"] = """"""
    st.session_state["query_text"] = """"""
    st.session_state["selectbox_query"] = """"""


def extract_content(uploaded_file: Optional[st.runtime.uploaded_file_manager.UploadedFile]):
    if uploaded_file:
        file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.markdown("### Uploaded File Details")
        st.write(file_details)
        if uploaded_file.type == "text/plain":
            # To convert to a string based IO:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            return (stringio.read(),)
        elif uploaded_file.type == "application/pdf":
            return pdf2text(uploaded_file)
        else:
            st.write(f"Format {uploaded_file.type} not supported! Only text or pdf formats are supported!")
            return ""
    else:
        return ""


def load_content(file: str):
    st.session_state["text"] = pdf2text(file)
    st.session_state["query_text"] = file.split("#")[1].split(".")[0]


def send_qa_request(
    raw_doc_text: str, query: str, backend: str, host: str, port: int, endpoint: str = "/qa", n_of_results: int = 5
):
    if raw_doc_text == "" or query == "":
        st.warning("There's no text or query to send! Add a document or write/copy your text and query!")
        return
    if not host:
        client = Client(host=backend)
        print("sending backend request to jina cloud")
    else:
        client = Client(host=host, port=port)
        print("sending backend request to local")

    params = {"query": query, "n_of_results": n_of_results}
    # We send a single Document for now. TODO: Explore the posibiltiy of sending a DocumentArray with more docs
    st.session_state["results"] = client.post(
        endpoint, Document(text=raw_doc_text, tags={"button": "fire"}), parameters=params
    )
    st.session_state["feedback_sent"] = False


def send_querygen_request(
    raw_doc_text: str, host: str, port: int, backend: str, endpoint: str = "/qa", n_of_results: int = 10
):
    """
    Send a querygen type request.
    In this context, n_of_results is the number of queries to return.
    The queries are just taken from the first 10 sentences of text.
    """

    if raw_doc_text == "":
        st.warning("There's no text to send! Add a document or write/copy your text!")
        return
    if not host:
        client = Client(host=backend)
        print("sending backend request to jina cloud")
    else:
        client = Client(host=host, port=port)
        print("sending backend request to local")

    # We can filter documents through the flow by their tag, but we still have to pass in "valid-looking"
    # parameters or the flow will crash.
    params = {"query": "", "n_of_results": n_of_results}

    # We send a single Document for now. TODO: Explore the posibiltiy of sending a DocumentArray with more docs
    st.session_state["generated_queries"] = client.post(
        endpoint, Document(text=raw_doc_text, tags={"button": "generate_queries_button"}), parameters=params
    )


def save_feedback(file: str, feedback_dict: dict):
    with open(file, "a") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow(list(feedback_dict.values()))


def log_feedback(feedback_dict: dict):

    df = pd.DataFrame([feedback_dict])

    # Rename model outputs to contain the word "output" so that "whylabs" logs it as an output.
    df.rename(
        columns={
            "best_predicted_answer": "best_predicted_output",
            "best_predicted_answer_score": "best_predicted_output_score",
            "best_predicted_answer_chunk": "best_predicted_output_chunk",
        },
        inplace=True,
    )

    # Log some derived quantities
    df["text_length"] = len(df["text"])
    df["best_predicted_output_length"] = len(df["best_predicted_output"])
    df["user_preferred_answer_length"] = len(df["user_preferred_answer"])

    os.environ["WHYLABS_DEFAULT_ORG_ID"] = "org-5a67EP"  # ORG-ID is case sensistive
    os.environ["WHYLABS_API_KEY"] = ""
    os.environ[
        "WHYLABS_DEFAULT_DATASET_ID"
    ] = "model-6"  # The selected model project "qa_model  (model-6)" is "model-6"

    results = why.log(pandas=df)

    performance_results = why.log_classification_metrics(
        df,
        target_column="user_preferred_answer",
        prediction_column="best_predicted_output",
        score_column="best_predicted_output_score",
    )

    results.writer("whylabs").write()
    performance_results.writer("whylabs").write()


st.set_page_config(page_title="Semantic Searcher", page_icon="🎈", layout="wide")

st.title("Semantic Search and Sentiment Analysis for Financial Domain")

with st.sidebar:
    with st.expander("ℹ️ - Backend config", expanded=False):
        st.text("Enter Backend  details:")
        st.text("if Host is empty send to backend")
        client_params = {
            "backend": st.text_input("backend", "grpcs://c724f56b46.wolf.jina.ai"),
            "host": st.text_input("Host", ""),
            "port": st.text_input("Port", 54321),
        }
        st.markdown("## Current config:")
        st.json(client_params)

with st.expander("ℹ️ - About", expanded=False):

    st.write(
        """
-   A semantic QA for Finance articles done as part of the FSDL Course
-   Take a look at [streamlit-jina and this article](https://blog.streamlit.io/streamlit-jina-neural-search/)
    """
    )

    st.markdown("")

st.header("## 📌 Write/Paste content or Upload a document")

c1, c2 = st.columns([4, 2])
with c1:
    try:
        content = st.session_state["text"]
    except KeyError:
        content = current_doc
    text_content_placeholder = st.empty()
    text_content = text_content_placeholder.text_area("Content (max 500 words)", content, height=510, key="k1")
with c2:
    uploaded_file = st.file_uploader("Pick a file...")
    if uploaded_file is not None:
        st.session_state["text"] = extract_content(uploaded_file)

        text_content = text_content_placeholder.text_area(
            "Content (max 500 words)", st.session_state["text"], height=510, key="k2"
        )
    else:
        st.session_state["text"] = current_doc

    st.write("...or select one of these examples available:")

    pathlist = Path("./src/semantic_search_qa/ui/example_docs").glob("**/*.pdf")
    for path in pathlist:
        path_in_str = str(path.name)
        load_btn = st.button(str(path.name), on_click=load_content, args=(str(path),))
        if load_btn:
            if "results" in st.session_state:
                st.session_state.pop("results")
            st.experimental_rerun()
    st.write("⚠️ Remove the picked file above if necessary")


generate_queries_btn = st.button(label="Generate Sample Queries")

if generate_queries_btn:

    querygen_req_args = {
        "raw_doc_text": st.session_state["text"],
        "host": client_params["host"],
        "port": client_params["port"],
        "backend": client_params["backend"],
    }
    send_querygen_request(**querygen_req_args)


if "generated_queries" in st.session_state:
    queries = []
    for d in st.session_state.generated_queries:
        for c in d.chunks:
            queries.append(c.text)

    st.session_state["selectbox_query"] = st.selectbox(
        "Sample queries",
        options=queries,
    )

with st.form("main-form", clear_on_submit=True):

    if "query_text" not in st.session_state:
        st.session_state["query_text"] = current_query
    elif "selectbox_query" in st.session_state:
        st.session_state["query_text"] = st.session_state["selectbox_query"]

    query = st.text_input("Your Query", st.session_state["query_text"])

    n_of_results = st.slider("Number of Results for QA", min_value=1, max_value=10, value=5)

    submit_btn = st.form_submit_button(label="Fire!")
    if submit_btn:
        req_args = {
            "raw_doc_text": text_content,
            "query": query,
            "backend": client_params["backend"],
            "host": client_params["host"],
            "port": client_params["port"],
            "endpoint": "/doc_cleaner",  # TODO Improve this entry point to have a better name
            "n_of_results": n_of_results,
        }
        send_qa_request(**req_args)

    clear_btn = st.form_submit_button(label="Clear!", on_click=clear_text)
    if clear_btn:
        if "results" in st.session_state:
            st.session_state.pop("results")
        if "generated_queries" in st.session_state:
            st.session_state.pop("generated_queries")
        st.experimental_rerun()


try:
    if st.session_state["feedback_sent"] or len(st.session_state["results"]) == 0:
        st.stop()
except KeyError:
    st.stop()

docs = st.session_state.results
st.header(f"Results (Responses/docs received {len(docs)})")

st.markdown(f"")

for i, doc in enumerate(docs):

    st.markdown(f"### Document {i}")

    qa_doc = doc.chunks[0]
    cls_doc = doc.chunks[1]

    qa_tab, cls_tab = st.tabs(["Question/Answer", "Classification"])
    with qa_tab:
        best_qa_response = qa_doc.chunks[0].tags["qa"]["answer"]
        best_qa_score = qa_doc.chunks[0].scores["qa_score"].value
        st.markdown(f"### Query: {query}")
        st.markdown(
            f"#### Best response: <span style='font-family:sans-serif; color:Green;'>{best_qa_response} (Score {best_qa_score:.5f})</span>",
            unsafe_allow_html=True,
        )
        for j, c in enumerate(qa_doc.chunks):
            st.markdown(f"### Chunk {j}")
            c1, c2 = st.columns(2)
            with c1:
                # QA part
                st.markdown(f"##### QA Score: {c.scores['qa_score'].value:.5f}")
                start = int(c.tags["qa"]["start"])
                end = int(c.tags["qa"]["end"])
                start_text = c.text[:start]
                target_text = c.text[start:end]
                end_text = c.text[end:]
                st.markdown(
                    f"{start_text} <mark><span style='font-family:sans-serif; color:Green;'>{target_text}</span></mark> {end_text}",
                    unsafe_allow_html=True,
                )
            with c2:
                st.write("**QA results details**")
                st.json(f"{c.tags['qa']}")

        st.markdown("## QA Feedback")

        # Put this into session state to get it inside form
        n_of_qa_results = len(st.session_state.results[0].chunks[0].chunks)
        st.session_state.n_of_qa_results = n_of_qa_results

        with st.form("feedback-form", clear_on_submit=False):
            feedback_file = st.text_input("File to save feedback", "/tmp/feedback.tsv")
            user_best_answer = st.selectbox(
                "If you don't like the first answer, what do you think it's the best one?",
                [str(i) for i in range(0, st.session_state.n_of_qa_results)] + ["Not Provided"],
            )

            c1, c2 = st.columns([1, 1])
            with c1:
                feedback_submit_btn = st.form_submit_button("Improve output!")
            with c2:
                nah_btn = st.form_submit_button("Nah!")

            if feedback_submit_btn:
                feedback_data = {
                    "text": st.session_state["text"],
                    "query": st.session_state["query_text"],
                    "best_predicted_answer": qa_doc.chunks[0].tags["qa"]["answer"],
                    "best_predicted_answer_score": qa_doc.chunks[0].scores["qa_score"].value,
                    "best_predicted_answer_chunk": qa_doc.chunks[0].text,
                    "user_preferred_answer": qa_doc.chunks[int(user_best_answer)].tags["qa"]["answer"]
                    if user_best_answer != "Not Provided"
                    else "Not Provided",
                    "user_preferred_answer_score": qa_doc.chunks[int(user_best_answer)].scores["qa_score"].value
                    if user_best_answer != "Not Provided"
                    else 0,
                    "user_preferred_answer_chunk": qa_doc.chunks[int(user_best_answer)].text
                    if user_best_answer != "Not Provided"
                    else "Not Provided",
                }
                save_feedback(feedback_file, feedback_data)
                log_feedback(feedback_data)
                st.session_state["feedback_sent"] = True
                st.success(f"Feedback sent!")
                sleep(1)
                clear_text()
                st.experimental_rerun()
            if nah_btn:
                st.session_state["feedback_sent"] = True
                clear_text()
                st.experimental_rerun()

    with cls_tab:
        pos_sent, neg_sent = 0, 0
        sentence = ""
        for j, c in enumerate(cls_doc.chunks):
            doc_sentiment = c.tags["sentiment"]
            if doc_sentiment["label"] == "positive":
                color = "#ACD1AF"  # Soft Green
                pos_sent += 1
            elif doc_sentiment["label"] == "neutral":
                color = "#FEF6D1"  # Soft Blonde/Yellow
            else:
                color = "#F8998D"  # Soft Red
                neg_sent += 1
            sentence += f"<mark><span style='font-family:sans-serif; background-color:{color};'>{c.text}</span></mark>"

        # Overall sentiment: https://help.alpha-sense.com/en/articles/4919714-how-we-calculate-sentiment
        # TODO: More can be done on this
        overall_sent = (pos_sent - neg_sent) / len(cls_doc.chunks)
        st.markdown(f"## Overall Document Sentiment Score: {overall_sent:.5f}")
        st.markdown(f"#### Pos/Neg/Total Sentences: {pos_sent}/{neg_sent}/{len(cls_doc.chunks)}")
        st.markdown(
            sentence,
            unsafe_allow_html=True,
        )

        st.markdown(f"## Document Details")
        for j, c in enumerate(cls_doc.chunks):
            st.markdown(f"### Sentence {j}")
            c1, c2 = st.columns(2)
            with c1:
                # Sentiment classifier part
                st.markdown(f"##### CLS Score: {c.scores['cls_score'].value:.5f}")
                sentiment_str = "N/A"
                try:
                    doc_sentiment = c.tags["sentiment"]
                    if doc_sentiment["label"] == "positive":
                        st.success(c.text)
                    elif doc_sentiment["label"] == "neutral":
                        st.warning(c.text)
                    else:
                        st.error(c.text)
                except KeyError:
                    st.warning("Couldn't retrieve sentiment for this document :-(")
            with c2:
                st.write("**Classifier results details**")
                st.json(f"{c.tags['sentiment']}")
