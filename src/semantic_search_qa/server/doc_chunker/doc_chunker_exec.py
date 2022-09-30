from importlib_metadata import SelectableGroups
from jina import Document, DocumentArray, Executor, requests

from semantic_search_qa.server.server_utils import log_exec_basics
from semantic_search_qa.utils import chunk_text


class DocChunkerExecutor(Executor):
    def __init__(self, chunk_len: int, do_overlap: bool, overlap_char_len: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_len = chunk_len
        self.do_overlap = do_overlap
        self.overlap_char_len = overlap_char_len
        self.logger.info(f"Chunk size: {self.chunk_len}")
        self.logger.info(f"Do Overlap? {self.do_overlap} - Overlap size: {self.overlap_char_len}")

    @requests  # (on="/doc_chunker")
    async def chunk_doc_text(self, docs: DocumentArray, **kwargs):
        """
        This processes each of the documents received. Each of the documents contains text, which is going to
        be decomposed in chunks (wrapped also as Documents) and stored in the "chunks" attr of the original
        Document.
        This will be probably used as the 1st step in the Doc Processing Pipeline
        """
        log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        try:
            chunk_len = int(kwargs["parameters"]["chunk_len"])
        except KeyError:
            chunk_len = self.chunk_len
            self.logger.warning(f"Couldn't extract chunk_len from Document parameters. Using defaulf of {chunk_len}")

        try:
            self.overlap_char_len = int(kwargs["parameters"]["overlap_char_len"])
        except KeyError:
            self.logger.warning(f"Couldn't extract chunk_len from Document parameters. Using defaulf of {chunk_len}")

        for d in docs:
            self.logger.info("\n" + 100 * "=" + "\n" + f"Processing Document {d.id}\n" + 100 * "=")
            chunks = chunk_text(
                d.text, chunk_len=chunk_len, do_overlap=self.do_overlap, overlap_size=self.overlap_char_len
            )
            for chunk in chunks:
                self.logger.debug(f"Adding new Document chunk to {d.id}\n" + 100 * "-" + "\n" + f"{chunk}\n")
                new_chunk = Document(text=chunk)
                self.logger.debug(
                    f"(Before adding it as chunk) Doc id {d.id} vs New Doc parent id {new_chunk.parent_id}"
                )  # Parent id should be empty here
                d.chunks.append(new_chunk)
                self.logger.debug(
                    f"(After adding it as chunk) Doc id {d.id} vs New Doc parent id {new_chunk.parent_id}"
                )  # Parent id should have been filled!

        self.logger.info(f"Chunks\n{docs.summary()}")
