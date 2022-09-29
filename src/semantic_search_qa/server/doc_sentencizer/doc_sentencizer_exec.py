from jina import Document, DocumentArray, Executor, requests

#from semantic_search_qa.server.server_utils import log_exec_basics


class DocSentencizerExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean_text(self, text):
        """
        Basically just remove newlines and tabs.

        Don't want to remove punctuation or case because it can convey sentiment or other contextual information.
        """
        text = text.split()
        text = " ".join(text)

        return text

    @requests(on="/doc_sentencizer")
    async def sentencize_text_chunks(self, docs: DocumentArray, **kwargs):
        """
        Sentencizes a DocumentArray.

        This assumes that the input documents in the DocumentArray doesn't have nested chunks.
        """
        #log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        for d in docs:
            d.text = self.clean_text(d.text)

        sentencizer = Executor.from_hub("jinahub://SpacySentencizer", install_requirements=True)
        sentencizer.segment(docs, parameters={})

        self.logger.info(f"number of docs: {len(docs)}")
        for d in docs:
            self.logger.info(f"Number of chunks after sentencizing:  {len(d.chunks)}.")
            self.logger.info(f"Sentences: {[c.text for c in d.chunks]}")
