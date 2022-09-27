from docarray.score import NamedScore
from jina import Document, DocumentArray, Executor, requests
from transformers.pipelines import pipeline

from semantic_search_qa.server.server_utils import log_exec_basics

model = "ProsusAI/finbert"


class ClassifierExecutor(Executor):
    def __init__(self, device: str = "cpu", *args, **kwargs):
        """The Classifier executor running on a CPU or a GPU

        :param device: The pytorch device that the model is on, e.g. 'cpu', 'cuda', 'cuda:1'
        """
        super().__init__(*args, **kwargs)
        self.logger.info(f"Creating HF pipeline for the Classifer from model {model}")
        self.cls_pipeline = pipeline("text-classification", model=model)

    @requests
    async def classify(self, docs: DocumentArray, **kwargs):
        """
        This executor wraps a ML model to classifies the sentiment of the text passed.
        """
        log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        for d in docs:
            for c in d.chunks:
                cls_result = self.cls_pipeline(c.text)
                self.logger.info(cls_result)
                c.scores["cls_score"] = NamedScore(value=cls_result[0]["score"], description="classification score")
                c.tags["sentiment"] = cls_result[0]
