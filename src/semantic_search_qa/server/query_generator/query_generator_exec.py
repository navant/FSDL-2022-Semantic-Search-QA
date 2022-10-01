from jina import Flow, DocumentArray, Document, Executor, requests

from semantic_search_qa.server.server_utils import log_exec_basics

class QueryGeneratorExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.query_gen = Executor.from_hub("jinahub://Doc2QueryExecutor",
                                           uses_with={'num_questions':3,
                                                      'traversal_paths':'@r'},
                                           install_requirements=True)

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
        
        for d in docs:               
            d.modality = "querygen"
            self.query_gen.doc2query(d.chunks)
            
