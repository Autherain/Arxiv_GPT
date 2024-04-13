"""
Keep and validate the parameters for a RecordFetcher. A pydantic
model is used to validate the entries on init.
"""
import time
import datetime
import logging
import requests

from pydantic import ValidationError

from retriever.services.article_converter_oaidc import ArticleConverterOAIDC
from retriever.services.record_fetcher_parameters import RecordFetcherParameters
from retriever.services.record_fetcher_query import RecordFetcherQuery

class RecordFetcher:
    """
    This service is used to fecth data on the arXiv endpoint.

    Attributes
    ----------
    _parameters : RecordFetcherParameters
        The inside class object defining redis options

    _logger : Logger
        The service logger.

    """

    def __init__(self, config: dict, article_converter: ArticleConverterOAIDC) -> None:
        """This function is used to ensure the presence and coherence
        of configuration parameters needed by the service.

        Parameters
        ----------
        config
            The configuration dictionary of the application.

        Returns
        -------
        None

        Exceptions
        -------
        RuntimeError
            Something went wrong during setup process.

        """
        self._logger = logging.getLogger(__name__)

        if not isinstance(config, dict):
            self._logger.critical(
                exc_info=True,
                msg="The configuration given to the service is not of dict type."
            )
            raise RuntimeError("Bad Config Type")

        if not isinstance(article_converter, ArticleConverterOAIDC):
            self._logger.critical(
                exc_info=True,
                msg="The article converter given to the service is not of ArticleConverterOAIDC type."
            )
            raise RuntimeError("Bad Article converter Type")
        self.article_converter = article_converter
        self.documents_retrieved = 0
        
        try:
            self._parameters = RecordFetcherParameters(**config)
        except ValidationError as e:
            self._logger.critical(
                "Faulty parameter into the service's configuration : %s",
                e,
                exc_info=True
            )
            raise RuntimeError("Bad Config Parameter") from e
        
        self.metrics_fetch_time = 0
        self.metrics_convert_time = 0

    def _build_query_parameters(self, from_date) -> RecordFetcherQuery:
        return RecordFetcherQuery(
            **{
                "verb": "ListRecords",
                "metadataPrefix": self._parameters.format,
                "set": self._parameters.set,
                "from": from_date,
            }
        )

    def _fetch(
        self, query_parameters: RecordFetcherQuery, resumption_token=None
    ) -> str:
        """
        Request data from ArXiv API and return the result.

        Notes
        ----------
        The request and response follows the OAI 2.0 format.
        http://www.openarchives.org/OAI/openarchivesprotocol.html
        The response is a string, a XML list of metadata records .

        Parameters
        ----------
        query_parameters : RecordFetcherQuery | None
            Query parameters for the request.

        Returns
        -------
        str
            A XML list of metadata records
        """

        if not isinstance(query_parameters, RecordFetcherQuery):
            raise TypeError(
                "The parameter object is not of the right type : %s",
                type(query_parameters)
            )

        query_parameters_dict = query_parameters.model_dump(by_alias=True)

        if resumption_token is not None:
            if not isinstance(resumption_token, str):
                raise ValueError("Resumption token is not of the right type.")
            query_parameters_dict = {
                "resumptionToken": resumption_token,
                "verb": "ListRecords",
            }

        # REQUEST
        response = requests.get(
            url=self._parameters.host,
            params=query_parameters_dict,
            timeout=self._parameters.time_out,
        )

        if response.status_code != 200:
            raise ValueError(f"API bad response code : {response.status_code}")

        return response.text

    def get_records(
        self,
        from_date: datetime.date = None
    ):
        """
        Build the query parameters, request the API endpoint
        and convert the response into a list of records.

        It's an iterator method that return an RecordPage Object.
        It will loop until no resumption token is given by the API
        (aka. all the records are retrieved). The API only give
        packs of 1000 records at a time.

        If no date is given, the start date in the application
        parameters is used.

        Parameters
        ----------
        from_date : date | None
            Entries date to fetch from.

        resumption_token : string | None
            A token used to get the next elements of arxiv

        Returns
        -------
        Iterator(list[Record])
            A XML list of metadata records
        """
        if from_date is None:
            from_date = self._parameters.start_date

        try:
            query_parameters = self._build_query_parameters(from_date)
        except (ValidationError,Exception) as e:
            self._logger.error(
                "An error occured when building query "
                "parameters %s",
                e,
                exc_info=True
            )
            raise RuntimeError("Query Parameter Error") from e

        chain_requests = True
        resumption_token = None
        self.documents_retrieved = 0

        while chain_requests:
            self.article_converter.clear()
            self.metrics_fetch_time = 0
            self.metrics_convert_time = 0

            try:
                metrics_fetch_start_time = time.perf_counter()
                query_result = self._fetch(query_parameters, resumption_token)
                self.metrics_fetch_time = time.perf_counter() - metrics_fetch_start_time
            except Exception as e:
                self._logger.error(
                    "An error occured when requesting the API : %s.",
                    e,
                    exc_info=True
                )
                raise RuntimeError("Fetch Error") from e

            try:
                metrics_convert_start_time = time.perf_counter()
                result = self.article_converter.convert(query_result)
                self.metrics_convert_time = time.perf_counter() - metrics_convert_start_time
                
            except Exception as e:
                self._logger.error(
                    "An error occured when converting the response : %s.",
                    e,
                    exc_info=True
                )
                raise RuntimeError("Convert Error") from e
            
            resumption_token = self.article_converter.records_elements.resumption_token

            if self._parameters.limit > 0:
                if self.documents_retrieved + len(result.records) >= self._parameters.limit:
                    result.records = result.records[:(self._parameters.limit - self.documents_retrieved)]
                    resumption_token = None
            self.documents_retrieved += len(result.records)

            if resumption_token is None or len(resumption_token) == 0:
                chain_requests = False

            yield result
            

