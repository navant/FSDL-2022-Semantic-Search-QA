from jina import Document, DocumentArray, Executor, requests

from semantic_search_qa.server.server_utils import log_exec_basics


class ClassifierExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @requests
    async def classify(self, docs: DocumentArray, **kwargs):
        """
        This executor wraps a ML model to classifies the sentiment of the text passed.
        """
        log_exec_basics(self.metas.name, self.logger, docs, kwargs)
