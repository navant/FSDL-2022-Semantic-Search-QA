from jina import DocumentArray, Executor, requests

# from semantic_search_qa.server.server_utils import log_exec_basics

param_top_k_ranker = 3
# model = "anablasi/qa_financial_v2"


class RankerExecutor(Executor):
    def __init__(self, device: str = "cpu", *args, **kwargs):
        """The Ranking executor running on a CPU or a GPU

        :param device: The pytorch device that the model is on, e.g. 'cpu', 'cuda', 'cuda:1'
        """
        super().__init__(*args, **kwargs)

    @requests  # (on="/qa")
    async def add_text(self, docs: DocumentArray, **kwargs):
        # log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        limit_result_idx = int(kwargs["parameters"]["n_of_results"])  # TODO This should be done in the ranker
        self.logger.info(f"--------------------------- Returning only {limit_result_idx} results")

        for d in docs:
            d.chunks = sorted(d.chunks, key=lambda c: c.scores["qa_score"].value, reverse=True)[:limit_result_idx]
