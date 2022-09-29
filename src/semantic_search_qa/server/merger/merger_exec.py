from jina import Document, DocumentArray, Executor, requests
from numpy import append
from typing import Any,Dict
from jina.logging.logger import JinaLogger


# def log_exec_basics(executor_name: str, logger: JinaLogger, docs: DocumentArray, kwargs: dict[str, Any]):
#    logger.info(f"Exec [{executor_name}] Number of docs received: {len(docs)}")
#    logger.info(f"Kwargs: {kwargs}")
#    for i, text_content in enumerate(docs.texts):
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
    #   log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        qa_doc = docs[0]
        cls_doc = docs[1]

        new_doc = Document(text=qa_doc.text)
        new_chunks = DocumentArray()  # type: ignore
        for qa_c, cls_c in zip(qa_doc.chunks, cls_doc.chunks):
            new_chunk = qa_c
            new_chunk.tags["sentiment"] = cls_c.tags["sentiment"]
            new_chunk.scores["cls_score"] = cls_c.scores["cls_score"]
            new_chunks.append(new_chunk)
        new_doc.chunks = new_chunks

        new_da = DocumentArray(new_doc)
        self.logger.info(new_da[0].summary())

        # TODO Do this here or in the ranker? Maybe here to give this exec a a purpose...
        limit_result_idx = int(kwargs["parameters"]["n_of_results"])
        for i, d in enumerate(new_da):
            self.logger.info(f"Limiting doc {i} from {len(docs[i].chunks)} results to {limit_result_idx}")
            d.chunks = d.chunks[:limit_result_idx]

        return new_da
