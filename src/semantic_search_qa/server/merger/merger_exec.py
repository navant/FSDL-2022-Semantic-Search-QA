from jina import Document, DocumentArray, Executor, requests
from jina.logging.logger import JinaLogger
from numpy import append

# def log_exec_basics(executor_name: str, logger: JinaLogger, docs: DocumentArray, kwargs: dict[str, Any]):
#    logger.info(f"Exec [{executor_name}] Number of docs received: {len(docs)}")
#    logger.info(f"Kwargs: {kwargs}")
#   for i, text_content in enumerate(docs.texts):
#        logger.info(f"Doc {i} text:\n{text_content}")


class MergerExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @requests
    async def merge_results_and_trim_chunks_returned(self, docs: DocumentArray, **kwargs):
        """
        This executor merges the two parallel tasks and trims the number of returned chunks to the limited
        value specified.
        """
        assert len(docs) == 2  # 2 docs received, the qa and the classifier documents

        # log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        self.logger.info(100 * "_" + " Merger " + 100 * "_")

        # log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        qa_doc, cls_doc = (docs[0], docs[1]) if docs[0].modality == "qa" else (docs[1], docs[0])

        new_doc = Document(text=qa_doc.text)
        new_doc.modality = "merged"
        new_doc.chunks = DocumentArray([qa_doc, cls_doc])
        self.logger.info(new_doc.summary())

        return DocumentArray(new_doc)
