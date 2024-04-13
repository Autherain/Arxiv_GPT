import logging

from typing import Union
import os

from langchain.chains.graph_qa.prompts import GRAPH_QA_PROMPT
from langchain_community.graphs import OntotextGraphDBGraph
from langchain_openai import ChatOpenAI

from langchain.chains import OntotextGraphDBQAChain
from langchain import PromptTemplate

from pydantic import ValidationError

from shared.models.ontology_graphdb_qa_parameters import OntologyGraphdbQaParameters


class OntologyGraphdbQA:
    """
    A service to perform question answering using an ontology-based approach for graphdb.

    Attributes:
    _logger: Logger
        The logger for this service.
    graph: OntotextGraphDBGraph
        Graph database representing the ontology.
    chain: OntotextGraphDBQAChain
        QA chain for answering questions based on the ontology.
    """

    def __init__(self, app_config: dict) -> None:
        """
        Initialize the OntologyQA service.

        Parameters:
        config: dict
            Configuration parameters for the service.
        """
        self._logger = logging.getLogger(__name__)

        # Check if config is a dictionary
        if not isinstance(app_config, dict):
            self._logger.critical(
                msg="The configuration given to the service is not of dict type."
            )
            raise RuntimeError("Bad Config Type")

        try:
            self.parameters = OntologyGraphdbQaParameters(**app_config)
        except ValidationError as e:
            self._logger.critical(
                exc_info=True,
                msg=f"Faulty parameter into the db client's configuration : {e}.",
            )
            raise RuntimeError("Bad Config Parameter") from e

        # Needed by lanhchain. Not good practive in my opinion
        os.environ["OPENAI_API_KEY"] = self.parameters.openai_api_key
        os.environ["GRAPHDB_USERNAME"] = self.parameters.graphdb_user
        os.environ["GRAPHDB_PASSWORD"] = self.parameters.graphdb_pwd

        try:
            # Create a graph representing the ontology
            self.graph = OntotextGraphDBGraph(
                query_endpoint=f"http://{self.parameters.graphdb_host}:{self.parameters.graphdb_port}{self.parameters.graphdb_url_end}",
                query_ontology=self.parameters.graphdb_query_ontology,
            )
        except Exception as e:
            self._logger.critical(
                "An error occurred while creating OntotextGraphDBGraph %s",
                e,
                exc_info=True,
            )
            raise RuntimeError("OntotextGraphDbGraph was not able to be created")

        try:
            # Create a QA chain for question answering
            self.chain = OntotextGraphDBQAChain.from_llm(
                ChatOpenAI(temperature=0, model=self.parameters.openai_model),
                graph=self.graph,
                verbose=True,
                qa_prompt=PromptTemplate(
                    input_variables=["context", "prompt"],
                    template=self.parameters.langchain_graphdb_qa_prompt,
                ),
            )
        except Exception as e:
            self._logger.critical(
                "An error occurred while creating OntotextGraphDBQAChain %s",
                e,
                exc_info=True,
            )
            raise RuntimeError(
                "OntotextGraphDBQAChain.from_llm was not able to be created"
            )

    def answer_question(self, question: str) -> str:
        """
        Answer a question based on the ontology.

        Parameters:
        question: str
            The question to be answered.

        Returns:
        Union[str, None]
            The answer to the question, or None if an error occurs.
        """
        try:
            # Invoke the QA chain to answer the question
            return self.chain.invoke(
                {
                    self.chain.input_key: question,
                }
            )[self.chain.output_key]
        except Exception as e:
            self._logger.error(
                "An error occurred while invoking the query chain for graphdb %s",
                e,
                exc_info=True,
            )
            raise RuntimeError
