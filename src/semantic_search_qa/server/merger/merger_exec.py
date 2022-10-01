from jina import Document, DocumentArray, Executor, requests
from numpy import append

from semantic_search_qa.server.server_utils import log_exec_basics


class MergerExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @requests
    async def merge_results_and_trim_chunks_returned(self, docs: DocumentArray, **kwargs):
        """
        This executor merges the two parallel tasks and trims the number of returned chunks to the limited
        value specified.
        """
        assert len(docs) == 3  # 2 docs received, the qa and the classifier documents

        log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        self.logger.info(100 * "_" + " Merger " + 100 * "_")

        # qa_doc, cls_doc = (docs[0], docs[1]) if docs[0].modality == "qa" else (docs[1], docs[0])
        qa_doc = [d for d in docs if d.modality == "qa"]
        cls_doc = [d for d in docs if d.modality == "cls"]
        querygen_doc = [d for d in docs if d.modality == "querygen"]

        

        new_doc = Document(text=qa_doc.text)
        new_doc.modality = "merged"
        new_doc.chunks = DocumentArray([qa_doc, cls_doc, querygen_doc])
        self.logger.info(new_doc.summary())

        return DocumentArray(new_doc)
