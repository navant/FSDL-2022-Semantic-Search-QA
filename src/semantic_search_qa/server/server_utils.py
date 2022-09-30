from typing import Any

from jina import DocumentArray
from jina.logging.logger import JinaLogger


def log_exec_basics(executor_name: str, logger: JinaLogger, docs: DocumentArray, kwargs: dict[str, Any]):
    logger.info(f"Exec [{executor_name}] Number of docs received: {len(docs)}")
    logger.info(f"Kwargs: {kwargs}")
    for i, d in enumerate(docs):
        logger.info(f"Doc {i} ({d.id}) text:\n{d.text}")
