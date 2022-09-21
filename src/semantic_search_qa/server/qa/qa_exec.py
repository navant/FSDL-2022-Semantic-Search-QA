from typing import Any, Dict

from jina import Document, DocumentArray, Executor, requests
from transformers.pipelines import pipeline
from typing_extensions import Self

from semantic_search_qa.server.server_utils import log_exec_basics

# model = "deepset/minilm-uncased-squad2")
# model = "deepset/roberta-base-squad2")

param_top_k_ranker = 3


class QAExecutor(Executor):
    def __init__(self, device: str = "cpu", *args, **kwargs):
        """The QA executor running on a CPU or a GPU

        :param device: The pytorch device that the model is on, e.g. 'cpu', 'cuda', 'cuda:1'
        """
        super().__init__(*args, **kwargs)
        # self.qa_pipeline = pipeline("question-answering", model = "anablasi/qa_financial_v2")

    def qa_ranker(self, query, paragraphs, top_k_ranker):
        ans = []
        for doc in paragraphs:
            answer: Dict[str, Any] = self.qa_pipeline({"question": query, "context": doc})
            answer["doc"] = doc
            ans.append(answer)
        return sorted(ans, key=lambda x: x["score"], reverse=True)[:top_k_ranker]

    @requests  # (on="/qa")
    async def add_text(self, docs: DocumentArray, **kwargs):
        log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        kwargs["docs_matrix"][0]
        limit_result_idx = int(kwargs["parameters"]["n_of_results"])
        print(f"--------------------------- Returning only {limit_result_idx} results")

        # result_docs = DocumentArray()
        for d in docs:
            for c in d.chunks:
                c.text = "[Processed on the qa side!]\n" + c.text
            d.chunks = d.chunks[:limit_result_idx]
