import csv
from io import StringIO
from time import sleep
from typing import Optional

import streamlit as st
from jina import Client, Document

from semantic_search_qa.ui.ui_utils import EXAMPLE_DOC
from semantic_search_qa.utils import pdf2text

example_doc = EXAMPLE_DOC  # or just do """"""


def clear_text():
    st.session_state["text"] = example_doc
    st.session_state["text_disabled"] = False


def extract_content(uploaded_file: Optional[st.runtime.uploaded_file_manager.UploadedFile]):
    if uploaded_file:
        file_details = {"Filename": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.markdown("### File Details")
        st.write(file_details)
        if uploaded_file.type == "text/plain":
            # To convert to a string based IO:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            return stringio.read()
        elif uploaded_file.type == "application/pdf":
            return pdf2text(uploaded_file)
        else:
            st.write(f"Format {uploaded_file.type} not supported! Only text or pdf formats are supported!")
            return ""
    else:
        return ""


def send_qa_request(raw_doc_text: str, query: str, backend: str, host: str, port: int, endpoint: str = "/qa", n_of_results: int = 5):
    if raw_doc_text == "":
        st.warning("There's no text to send! Add a document or write/copy your text!")
        return
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> b90006b (    e https://username@github.com/username/repository.gt)
    if host == '0.0.0.0':
       client = Client(host=host, port=port)
    else:
        client = Client(host=backend)
<<<<<<< HEAD
=======
    #client = Client(host=host, port=port)
    client = Client(host='grpcs://006ea4c540.wolf.jina.ai')
>>>>>>> 657b145 (    e https://username@github.com/username/repository.gt)
=======
>>>>>>> b90006b (    e https://username@github.com/username/repository.gt)
    params = {"query": query, "n_of_results": n_of_results}
    # We send a single Document for now. TODO: Explore the posibiltiy of sending a DocumentArray with more docs
    st.session_state["results"] = client.post(endpoint, Document(text=raw_doc_text), parameters=params)
    clear_text()
    st.session_state["feedback_sent"] = False
    st.session_state["text_disabled"] = True


def save_feedback(file: str, text: str, query: str, best_predicted_answer: str, user_preferred_answer: str):
    with open(file, "a") as f:
        writer = csv.writer(f, delimiter="\t", lineterminator="\n")
        writer.writerow([text, query, best_predicted_answer, user_preferred_answer])


st.set_page_config(page_title="Semantic Question Answering (WIP)", page_icon="🎈", layout="wide")

st.title("Semantic Question Answering (WIP)")

with st.sidebar:

<<<<<<< HEAD
<<<<<<< HEAD
    st.title("Client Request Params -Enter either Backend or Host ip")
    client_params = {"backend": st.text_input("backend","grpcs://006ea4c540.wolf.jina.ai"),"host": st.text_input("Host", ""), "port": st.text_input("Port", 54321)}
=======
    st.title("Client Request Params")

    client_params = {"host": st.text_input("Host", "0.0.0.0"), "port": st.text_input("Port", 54321)}
    
>>>>>>> 657b145 (    e https://username@github.com/username/repository.gt)
=======
    st.title("Client Request Params -Enter either Backend or Host ip")
    client_params = {"backend": st.text_input("backend","grpcs://006ea4c540.wolf.jina.ai"),"host": st.text_input("Host", ""), "port": st.text_input("Port", 54321)}
>>>>>>> b90006b (    e https://username@github.com/username/repository.gt)
    st.markdown("## Current config:")
    st.json(client_params)

with st.expander("ℹ️ - About", expanded=False):

    st.write(
        """     
-   A semantic QA for Finance articles done as part of the FSDL Course
-   More details TBD
-   Take a look at [streamlit-jina and this article](https://blog.streamlit.io/streamlit-jina-neural-search/)
	    """
    )

    st.markdown("")

st.header("## 📌 Write/Paste content or Upload a document")

c1, c2 = st.columns([4, 2])
with c1:
    try:
        content = st.session_state["text"]
        content_disabled = st.session_state["text_disabled"]
    except KeyError:
        content = example_doc
        content_disabled = False
    text_content_placeholder = st.empty()
    text_content = text_content_placeholder.text_area(
        "Content (max 500 words)", content, height=510, disabled=content_disabled, key="k1"
    )
with c2:
    uploaded_file = st.file_uploader("Pick a file", disabled=content_disabled)
    if uploaded_file is not None:
        st.session_state["text"] = extract_content(uploaded_file)
        text_content = text_content_placeholder.text_area(
            "Content (max 500 words)", st.session_state["text"], height=510, disabled=content_disabled, key="k2"
        )
    else:
        st.session_state["text"] = example_doc


with st.form("main-form", clear_on_submit=True):
    query = st.text_input("Query", "Who's increasing the rates?")
    n_of_results = st.slider("Number of Results", min_value=1, max_value=10, value=5)

    submit_btn = st.form_submit_button(label="Fire!")
    if submit_btn:
        req_args = {
            "raw_doc_text": text_content,
            "query": query,
            "backend":client_params["backend"],
            "host": client_params["host"],
            "port": client_params["port"],
            "endpoint": "/doc_cleaner",  # TODO Improve this entry point to have a better name
            "n_of_results": n_of_results,
        }
        send_qa_request(**req_args)


try:
    if st.session_state["feedback_sent"]:
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

        with st.form("feedback-form", clear_on_submit=True):
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
                    "file": feedback_file,
                    "text": text_content,
                    "query": query,
                    "best_predicted_answer": qa_doc.chunks[0].tags["qa"]["answer"],
                    "user_preferred_answer": qa_doc.chunks[int(user_best_answer)].tags["qa"]["answer"]
                    if user_best_answer != "Not Provided"
                    else "Not Provided",
                }
                save_feedback(**feedback_data)
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
