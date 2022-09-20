from jina import DocumentArray, Executor, requests

class QAExecutor(Executor):
    @requests(on='/qa')
    async def add_text(self, docs: DocumentArray, **kwargs):
        print(f"Number of docs received: {len(docs)}")
        print(docs.texts)
        print(kwargs)
        input_docs = kwargs['docs_matrix'][0]
        print(input_docs[0])
        for d in input_docs:
            # TODO Call the pipeline
            d.text = 'This is the output of the alg'
