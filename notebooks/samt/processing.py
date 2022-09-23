# Note: This is probably already deprecated since it looks like other team members have already got a better pipeline going.

# Putting together the jina exploration code in jina_exploration.ipynb.



from docarray import Document, DocumentArray
from jina import Flow, Executor, requests


DATA_DIR = "../../notebooks/data/"

docs = DocumentArray.from_files(DATA_DIR + "*.pdf", recursive=True)
for doc in docs:
    doc.load_uri_to_blob()


class TextChunkMerger(Executor):
    """
    Applies Sentencizing to a chunk if and only if it is a text chunk.
    Then flattens the sentencization to level 1 chunks.
    i.e.
       [text_chunk_A, text_chunk_B, ... ] -> [[A1, A2, A3, ...], [B1, B2, ...], ...]
                                          -> [A1, A2, A3, ..., B1, B2, ...]
    """

    @requests(on="/index")  # <---- WHAT DOES THIS DO?
    def sentencize_text_chunks(self, docs, **kwargs):
        for doc in docs:  # level 0 document
            chunks_lvl_1 = DocumentArray()  # level 0 is original Document
            for chunk in doc.chunks:
                if chunk.mime_type == "text/plain":
                    chunks_lvl_1.append(chunk)

                # Break chunk into sentences
                sentencizer = Executor.from_hub("jinahub://Sentencizer")
                sentencizer.segment(chunks_lvl_1, parameters={})

            # Extend level 1 chunk DocumentArray with the sentences
            for lvl_1_chunk in chunks_lvl_1:
                doc.chunks.extend(lvl_1_chunk.chunks) 
            

class ImageNormalizer(Executor):
    """
    Normalizes images and resizes them to 64x64 to be fed into a neural network.
    """
    @requests(on="/index")
    def normalize_chunks(self, docs, **kwargs):
        for doc in docs:
            for chunk in doc.chunks:
                if chunk.blob:
                    chunk.convert_blob_to_image_tensor()

                if hasattr(chunk, "tensor") and chunk.tensor is not None:
                    chunk.convert_image_tensor_to_uri()
                    chunk.tags["image_datauri"] = chunk.uri
                    chunk.tensor = chunk.tensor.astype(np.uint8)
                    chunk.set_image_tensor_shape((64, 64))
                    chunk.set_image_tensor_normalization()



    
flow = (
    Flow()
    .add(uses="jinahub+sandbox://PDFSegmenter", install_requirements=True, name="segmenter")
    .add(uses=TextChunkMerger, name="text_chunk_merger")
    .add(uses=ImageNormalizer, name="image_normalizer")
        .add(
        uses="jinahub+sandbox://CLIPEncoder",
        name="encoder",
        uses_with={"traversal_paths": "@c"},
    )
    .add(
        uses="jinahub://SimpleIndexer",
        install_requirements=True,
        name="indexer",
        uses_with={"traversal_right": "@c"},
    )
)


with flow:
    indexed_docs = flow.index(docs)


