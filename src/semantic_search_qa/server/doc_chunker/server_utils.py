from typing import Any

from jina import DocumentArray
from jina.logging.logger import JinaLogger


def log_exec_basics(executor_name: str, logger: JinaLogger, docs: DocumentArray, kwargs: dict[str, Any]):
    logger.info(f"Exec [{executor_name}] Number of docs received: {len(docs)}")
    logger.info(f"Kwargs: {kwargs}")
    for i, text_content in enumerate(docs.texts):
        logger.info(f"Doc {i} text:\n{text_content}")
