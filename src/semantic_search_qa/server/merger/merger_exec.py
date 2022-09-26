from jina import Document, DocumentArray, Executor, requests

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
        log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        # TODO Do this here or in the ranker? Maybe here to give this exec a a purpose...
        limit_result_idx = int(kwargs["parameters"]["n_of_results"])
        for i, d in enumerate(docs):
            self.logger.info(f"Limiting doc {i} from {len(docs[i].chunks)} results to {limit_result_idx}")
            d.chunks = d.chunks[:limit_result_idx]
