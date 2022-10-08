from jina import Document, DocumentArray, Executor, Flow, requests

from semantic_search_qa.server.server_utils import log_exec_basics

import random

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

        # Only anticipating 1 doc for now
        for d in docs:
            d.modality = "querygen"

            n_of_results = min(len(d.chunks), int(kwargs["parameters"]["n_of_results"]))

            # Return n_of_results random chunks, sampling without replacement.
            sampled_chunks = DocumentArray(random.sample(d.chunks, k=n_of_results))
            
            self.query_gen.doc2query(sampled_chunks)

            # Replace document chunks with the subset that has queries attached.
            d.chunks = [c.chunks[k] for k in range(self.n_questions_per_sentence) for c in sampled_chunks]

            # Postprocessing queries to be nicer.
            for chunk in d.chunks:
                # Add a question mark to the end of each query
                if chunk.text[-1] != "?":
                    chunk.text += "?"

                # Capitalize question
                chunk.text = chunk.text.capitalize()
