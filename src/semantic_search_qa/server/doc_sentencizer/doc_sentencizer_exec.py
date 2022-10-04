from jina import Document, DocumentArray, Executor, requests

#from semantic_search_qa.server.server_utils import log_exec_basics


class DocSentencizerExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sentencizer = Executor.from_hub("jinahub://SpacySentencizer", install_requirements=True)

    @requests  # (on="/doc_sentencizer")
    async def sentencize_text_chunks(self, docs: DocumentArray, **kwargs):
        """
        Sentencizes a DocumentArray.

        This assumes that the input documents in the DocumentArray doesn't have nested chunks.
        """
        #log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        self.sentencizer.segment(docs, parameters={})

        for d in docs:
            self.logger.info(f"Sentensized document\n{d.summary()}")
