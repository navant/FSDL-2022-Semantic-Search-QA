from jina import Document, DocumentArray, Executor, Flow, requests

from semantic_search_qa.server.server_utils import log_exec_basics


class QueryGeneratorExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.n_questions_per_sentence = 1
        self.query_gen = Executor.from_hub(
            "jinahub://Doc2QueryExecutor",
            uses_with={"num_questions": self.n_questions_per_sentence, "traversal_paths": "@r"},
            install_requirements=True,
        )

    @requests
    async def generate_queries(self, docs: DocumentArray, **kwargs):
        """
        Generate sample queries from text chunks.

        docs: Input array of documents.

        Input assumptions:
        - docs[i] is document 'i'.
        - docs[i].chunks[j] is sentence 'j' of document 'i' (after sentencizing).

        The function modifies the input by adding chunks to docs[i].chunks[j], such that
        docs[i].chunks[j].chunks[k].text is the 'k'th query text for sentence 'j' of document 'i'.
        """
        log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        n_of_results = int(kwargs["parameters"]["n_of_results"])

        for d in docs:
            d.modality = "querygen"
            self.query_gen.doc2query(d.chunks[:n_of_results])

            # Transform into new document with chunks
            # The .text attribute of each chunk holds the query.
            d.chunks = [c.chunks[k] for k in range(self.n_questions_per_sentence) for c in d.chunks[:n_of_results]]

            # Add a question mark to the end of each query
            for chunk in d.chunks:
                chunk.text += "?"
