from jina import Document, DocumentArray, Executor, requests
from numpy import append

# from semantic_search_qa.server.server_utils import log_exec_basics


class MergerExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @requests
    async def merge_results_and_trim_chunks_returned(self, docs: DocumentArray, **kwargs):
        """
        This executor merges the two parallel tasks and trims the number of returned chunks to the limited
        value specified.
        """

        #       log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        self.logger.info(100 * "_" + " Merger " + 100 * "_")

        self.logger.info(docs[0].tags["button"])

        if docs[0].tags["button"] == "fire":
            assert len(docs) == 2  # 2 docs received, the qa and the classifier documents
            qa_doc, cls_doc = (docs[0], docs[1]) if docs[0].modality == "qa" else (docs[1], docs[0])

            new_doc = Document(text=qa_doc.text)
            new_doc.modality = "merged"
            new_doc.chunks = DocumentArray([qa_doc, cls_doc])

            self.logger.info(new_doc.summary())
            return DocumentArray(new_doc)

        elif docs[0].tags["button"] == "upload":
            assert len(docs) == 1
            for c in docs[0].chunks:
                self.logger.info(c.text)
            return docs
