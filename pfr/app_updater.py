""" 
"""
import time
import re

# App services & repositories
from requests import Request

from updater.boot import logger
from updater.boot import update_article_queue
from updater.boot import article_repository
from updater.boot import vector_store

from langchain.text_splitter import SpacyTextSplitter

#----------------------
# LAUNCH APP
#----------------------

if __name__ == "__main__":
    
    logger.info("=== Start Updater main loop ===")

    text_splitter = SpacyTextSplitter(
          chunk_size = 200,
          chunk_overlap  = 20
        )

    while True :
        popped_article = update_article_queue.pop_task_update_article()

        # If no article is present in the queue, we wait a few seconds
        # then we jump to the next loop
        if popped_article is None:
            time.sleep(1)
            continue

        try:
            logger.info(f"Popped article : {popped_article.id}")

            # Insert into KG
            article_repository.insert_article(popped_article)
        except RuntimeError as e:
                logger.error(
                    "Failed to insert an article in the KG : %s.",
                    e,
                    exc_info=True
                )

        try:
            # Vectorisation
            texts = text_splitter.create_documents([popped_article.description])
            vector_store.add_documents(texts)
        except RuntimeError as e:
                logger.error(
                    "Failed to vectorize an article abstract : %s.",
                    e,
                    exc_info=True
                )
