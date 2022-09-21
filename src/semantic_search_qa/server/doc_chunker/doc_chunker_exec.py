import os

from jina import Document, DocumentArray, Executor, requests
from jina.logging.logger import JinaLogger

from semantic_search_qa.server.server_utils import log_exec_basics
from semantic_search_qa.utils import chunk_text


class DocChunkerExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = JinaLogger("doc_chunker_logger")
        self.log_path = os.path.join(self.workspace, "doc_chunker_log.txt")

    @requests(on="/doc_chunker")
    async def chunk_doc_text(self, docs: DocumentArray, **kwargs):
        """
        This processes each of the documents received. Each of the documents contains text, which is going to
        be decomposed in chunks (wrapped also as Documents) and stored in the "chunks" attr of the original
        Document.
        This will be probably used as the 1st step in the Doc Processing Pipeline
        """
        log_exec_basics(self.metas.name, self.logger, docs, kwargs)

        try:
            # TODO: Add chunk_len in to the parameters!
            chunk_len = int(kwargs["parameters"]["chunk_len"])
        except KeyError:
            self.logger.warning("Couldn't extract chunk_len from Document parameters. Using default of 100")
            chunk_len = 100

        for d in docs:
            self.logger.info("\n" + 100 * "=" + "\n" + f"Processing Document {d.id}\n" + 100 * "=")
            chunks = chunk_text(d.text, chunk_len=chunk_len)
            for chunk in chunks:
                self.logger.info(f"Adding new Document chunk to {d.id}\n" + 100 * "-" + "\n" + f"{chunk}\n")
                new_chunk = Document(text=chunk)
                self.logger.debug(
                    f"(Before adding it as chunk) Doc id {d.id} vs New Doc parent id {new_chunk.parent_id}"
                )  # Parent id should be empty here
                d.chunks.append(new_chunk)
                self.logger.debug(
                    f"(After adding it as chunk) Doc id {d.id} vs New Doc parent id {new_chunk.parent_id}"
                )  # Parent id should have been filled!
