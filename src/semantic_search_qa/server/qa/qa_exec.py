from typing import Any, Dict
from docarray.score import NamedScore
from jina import DocumentArray, Executor, requests
from transformers.pipelines import pipeline
from jina.logging.logger import JinaLogger


# def log_exec_basics(executor_name: str, logger: JinaLogger, docs: DocumentArray, kwargs: dict[str, Any]):
#    logger.info(f"Exec [{executor_name}] Number of docs received: {len(docs)}")
#    logger.info(f"Kwargs: {kwargs}")
#    for i, text_content in enumerate(docs.texts):
#        logger.info(f"Doc {i} text:\n{text_content}")



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

    @requests  # (on="/qa")
    async def add_text(self, docs: DocumentArray, **kwargs):
     #   log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        query = kwargs["parameters"]["query"]
        self.logger.info(f"Query: {query}")
        for d in docs:
            d.modality = "qa"
            for c in d.chunks:
                answer = self.qa_pipeline({"question": query, "context": c.text})
                self.logger.info(answer)
                c.scores["qa_score"] = NamedScore(value=answer["score"], description="score")
                c.tags["qa"] = answer
