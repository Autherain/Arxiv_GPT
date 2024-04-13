"""
"""

from datetime import datetime
from logging import exception
import time

from pydantic import ValidationError

# App services & repositories
from asker.boot import logger
from asker.boot import ontology_qa
from asker.boot import update_article_queue
from asker.boot import params_repository
from asker.boot import vector_store
from asker.boot import config
from asker.boot import chatgpt_vector_graphdb_qa

from shared.models.get_ask_input import GetAskInput

# ----------------------
# LAUNCH APP
# ----------------------

if __name__ == "__main__":
    logger.info("=== Start Asker ===")

    if "TIME_SLEEP_ERROR" not in config:
        logger.critical("TIME_SLEEP_ERROR is not present if .env file config")
        exit(1)

    while True:
        try:
            popped_question = update_article_queue.api_pop_question()
        except Exception as e:
            logger.info("Can't pop question %s !!!", e)
            time.sleep(config["TIME_SLEEP_ERROR"])
            continue

        try:
            # If no article is present in the queue, we wait a few seconds
            # then we jump to the next loop
            if popped_question is None:
                time.sleep(1)
                continue

            logger.info(f"Popped question : {popped_question}")

            try:
                neo4j_similarity_article = vector_store.similarity_search_with_score(
                    query=popped_question.question_content
                )
            except RuntimeError as e:
                logger.error(
                    "Something went wrong when looking for the answer of a question: %s.",
                    e,
                )
                raise RuntimeError from e  # Raise the exception to propagate it

            # logger.info(f"###############{neo4j_similarity_article}###############")

            try:
                question_answer_graphdb = ontology_qa.answer_question(
                    popped_question.question_content
                )

                # logger.info(f"###############{question_answer_graphdb}###############")
                #
            except RuntimeError as e:
                logger.error(
                    "Something went wrong when looking for the answer of a question: %s.",
                    e,
                )
                raise RuntimeError from e  # Raise the exception to propagate it

            try:
                full_answer = chatgpt_vector_graphdb_qa.answer_question(
                    question=popped_question.question_content,
                    vector_answer=str(neo4j_similarity_article),
                    graphdb_answer=question_answer_graphdb,
                )
            except Exception as e:
                logger.error(
                    "Error occurred when processing the question, the answer of graphdb as well as neo4J: %s.",
                    e,
                    exc_info=True,
                )
                raise e  # Raise the exception to propagate it

            # logger.info(f"###############{full_answer}###############")

            try:
                full_popped_question = params_repository.get_key_value_api_ask_question(
                    GetAskInput(token=str(popped_question.token))
                )
            except RuntimeError as e:
                logger.error(
                    "Something went wrong when retrieving the contentvalue of the question %s.",
                    e,
                    exc_info=True,
                )
                raise e  # Raise the exception to propagate it

            try:
                full_popped_question.question_answer = full_answer
                full_popped_question.finish_date = datetime.now()
                full_popped_question.state = "Done"
            except (ValidationError, ValueError) as e:
                logger.error(
                    "Error occurred when processing the question data: %s.",
                    e,
                    exc_info=True,
                )
                raise e  # Raise the exception to propagate it

            try:
                params_repository.set_key_value_api_ask_question(full_popped_question)
                logger.info(
                    f"Question of token {str(popped_question.token)} was successfully answered !"
                )
            except Exception as e:
                logger.error(
                    "Something went wrong when updating a question with an answer %s.",
                    e,
                    exc_info=True,
                )
                raise e  # Raise the exception to propagate it

        except Exception as e:
            logger.error("An unexpected error occurred: %s", e)
            try:
                params_repository.set_key_value_error_qa_question(popped_question)
            except Exception as e:
                logger.critical("A critical error happened %s", e)
