"""
This function is used to return the db_engine. If the engine
is not created, the engine is initialized with the parameters.
If the engine is not initialized and no parameters are given,
an error is raised.
"""
import logging
from pydantic import ValidationError
from requests import Request
from requests import Response
from requests import Session
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError

from shared.services.graphdb_client_parameters import GraphDBClientParameters

class GraphDBClient:
    """
    This class is used to insure the requests given to
    the graphDB API are authorized by authenticating the
    client beforehand.

    GraphDB use a token system. The client send his credentials
    first and a GDB token is given to him. this token his used in
    each next request to the database.

    """

    def __init__(self, app_config: dict = None):
        self.logger = logging.getLogger(__name__)

        if not isinstance(app_config, dict):
            self.logger.critical(
                exc_info=True,
                msg="The configuration given to the graphdb client is not of dict type "
                "and the engine isn't initialized."
            )
            raise RuntimeError("Bad Config Type")

        try:
            self.parameters = GraphDBClientParameters(**app_config)
        except ValidationError as e:
            self.logger.critical(
                exc_info=True,
                msg=f"Faulty parameter into the db client's configuration : {e}."
            )
            raise RuntimeError("Bad Config Parameter") from e

        self.auth_session = Session()
        self.token_session = None
        self.getToken()

    def getToken(self):
        """
        Retrieve and store the authorization token.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.auth_session.headers.update({'X-GraphDB-Password': self.parameters.pwd})

        try:
            response = self.auth_session.post(f"http://{self.parameters.host}:{self.parameters.port}/rest/login/{self.parameters.user}")
            response.raise_for_status()
        except ConnectionError as e:
            raise RuntimeError("GraphDB Token Retrieve Error : Connection Error.")
        
        except HTTPError as e:
            raise RuntimeError(f"GraphDB Token Retrieve Error : {e}.")

        if "authorization" not in response.headers:
            raise RuntimeError(f"GraphDB Token Retrieve Error : Token absent of the DB response.")
        
        self.token_session = Session()
        self.token_session.headers["authorization"] = response.headers["authorization"]

    def request(self, request: Request) -> Response:
        """
        Pass a request to the grapDB database and add the elements 
        needed to reach it and be authorized.
        
        Parameters
        ----------
        a request object. The URL used must be relative, the method
        will add the host and port used to reach the db.

        Exemple
        ----------
        request = Request('GET', '/rest/repositories/pfr')
        client.request(request)
        ---> The method will add "http://host:port" prefix to it and auth token
        ---> The method will add "http://host:port" prefix to it and auth token
        ---> Result : "http://host:port/rest/repositories/pfr"
        
        Returns
        -------
        Response object
        """

        if self.token_session is None:
            self.getToken()

        if not isinstance(request, Request):
            self.logger.error(
                exc_info=True,
                msg="The request given is not of the right type."
            )
            raise TypeError("Bad Config Type")
        
        try:
            request.url = f"http://{self.parameters.host}:{self.parameters.port}{request.url}"
            prepared_request = self.token_session.prepare_request(request=request)
            response = self.token_session.send(prepared_request)
            response.raise_for_status()
            return response
        except ConnectionError as e:
            raise RuntimeError("GraphDB Repository communication test Error : Connection Error.")
        
        except HTTPError as e:
            raise RuntimeError(f"GraphDB Repository Error : {e}.")
        
    def request_update(self, data):
        request = Request('POST', '/repositories/pfr/statements', headers={"Content-Type": "application/sparql-update"}, data=data)
        self.request(request=request)
