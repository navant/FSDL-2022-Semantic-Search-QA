from typing import Any, Dict

from docarray.score import NamedScore
from jina import DocumentArray, Executor, requests
from transformers.pipelines import pipeline

from semantic_search_qa.server.server_utils import log_exec_basics

param_top_k_ranker = 3
model = "anablasi/qa_financial_v2"


class QAExecutor(Executor):
    def __init__(self, device: str = "cpu", *args, **kwargs):
        """The QA executor running on a CPU or a GPU

        :param device: The pytorch device that the model is on, e.g. 'cpu', 'cuda', 'cuda:1'
        """
        super().__init__(*args, **kwargs)
        self.logger.info(f"Creating HF pipeline for QA from model {model}")
        self.qa_pipeline = pipeline("question-answering", model=model)

    # TODO This should be done in the ranker based on
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

        query = kwargs["parameters"]["query"]
        self.logger.info(f"Query: {query}")
        limit_result_idx = int(kwargs["parameters"]["n_of_results"])  # TODO This should be done in the ranker
        self.logger.info(f"--------------------------- Returning only {limit_result_idx} results")
        for d in docs:
            for c in d.chunks:
                answer = self.qa_pipeline({"question": query, "context": c.text})
                self.logger.info(answer)
                c.scores["score"] = NamedScore(value=answer["score"], description="score")
                c.tags = answer
            d.chunks = d.chunks[:limit_result_idx]  # TODO This should be done in the ranker
