from docarray.score import NamedScore
from jina import Document, DocumentArray, Executor, requests
from jina.logging.logger import JinaLogger
from transformers.pipelines import pipeline

model = "ProsusAI/finbert"


# def log_exec_basics(executor_name: str, logger: JinaLogger, docs: DocumentArray, kwargs: dict[str, Any]):
#  logger.info(f"Exec [{executor_name}] Number of docs received: {len(docs)}")
#  logger.info(f"Kwargs: {kwargs}")
#  for i, text_content in enumerate(docs.texts):
#     logger.info(f"Doc {i} text:\n{text_content}")


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
        #   log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        for d in docs:
            d.modality = "classifier"
            for c in d.chunks:
                cls_result = self.cls_pipeline(c.text, truncation=True)
                self.logger.info(cls_result)
                c.scores["cls_score"] = NamedScore(value=cls_result[0]["score"], description="classification score")
                c.tags["sentiment"] = cls_result[0]
