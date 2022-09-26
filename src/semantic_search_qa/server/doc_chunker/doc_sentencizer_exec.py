from jina import Document, DocumentArray, Executor, requests

from semantic_search.qa.server.server_utils import log_exec_basics


class DocSentencizerExecutor(Executor):

    @requests(on="/doc_sentencizer")
    def sentencize_text_chunks(self, docs: DocumentArray, **kwargs):
        """
        Sentencize then flattens chunks.
        1. Sentencizing:
           - Applies "Spacy Sentencizer" to split doc chunks into sentences *iff* it is a 'text/plain' chunk.

               chunks = [text_chunk_A,  text_chunk_B,  ... ]
               ->       [[A1, A2, ...], [B1, B2, ...], ...]

        2. Flattening:
           - Flattens the sentencization to level 1 chunks.

               chunks = [[A1, A2, ...], [B1, B2, ...], ...]
               ->       [A1, A2, ...,   B1, B2, ...]
        """
        for doc in docs:  # level 0 document
            chunks_lvl_1 = DocumentArray()  # level 0 is original Document
            for chunk in doc.chunks:
                if chunk.mime_type == "text/plain":
                    chunks_lvl_1.append(chunk)

                # Break chunk into sentences
                sentencizer = Executor.from_hub("jinahub://SpacySentencizer")
                sentencizer.segment(chunks_lvl_1, parameters={})

            # Extend level 1 chunk DocumentArray with the sentences
            for lvl_1_chunk in chunks_lvl_1:
                doc.chunks.extend(lvl_1_chunk.chunks) 
