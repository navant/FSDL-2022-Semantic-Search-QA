from jina import Document, DocumentArray, Executor, requests

# from semantic_search_qa.server.server_utils import log_exec_basics
# from semantic_search_qa.utils import remove_special_chars


def remove_special_chars(text):
    """
    Remove newlines and tabs.

    Don't want to remove punctuation or case because it can convey sentiment or other contextual information.
    """
    text = text.split()
    text = " ".join(text)

    return text


class DocCleanerExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @requests  # (on="/doc_cleaner")
    async def clean_doc(self, docs: DocumentArray, **kwargs):
        """
        Cleans documents

        This assumes that the input documents in the DocumentArray doesn't have nested chunks.
        """
        # log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        for d in docs:
            d.text = remove_special_chars(d.text)
            self.logger.info(f"Cleaned text:\n{d.text}")
