"""
Repository used to query the database
against the params collection.

The params collection keep dynamic configuration
elements of the application.
"""

import logging
from unidecode import unidecode
from shared.services.graphdb_client import GraphDBClient

from shared.models.article import Article


class ArticleRepository:
    """
    """

    def __init__(self, graphdb_client: GraphDBClient) -> None:
        self._logger = logging.getLogger(__name__)

        if not isinstance(graphdb_client, GraphDBClient):
            self._logger.error(
                "The GraphDBClient connector given to the repository is not of "
                "the right type : %s",
                type(graphdb_client),
                exc_info=True
            )
            raise RuntimeError("GraphDB Client Bad Type")
        self.graphdb_client = graphdb_client

    def insert_article(self, article: Article) -> None:
        """   
        """
        if not isinstance(article, Article):
            self._logger.error(
                "The parameter given for update of api retrieval is not "
                "of the right type : %s",
                type(article),
                exc_info=True
            )
            raise RuntimeError("Parameter Bad Type")

        try:
            data = """
            PREFIX fabio: <http://purl.org/spar/fabio/>\n
            PREFIX dcterms: <https://www.dublincore.org/specifications/dublin-core/dcmi-terms/>\n
            INSERT DATA\n
            {\n
            GRAPH <pfr:pfr> {\n
            """
            data +=f'<{article.id}> a fabio:work ;\n'
            data +=f'dcterms:title "{article.title}" .\n'
            data +="""}\n
            }
            """
            self.graphdb_client.request_update(data=data)
        except Exception as e:
            raise RuntimeError from e


        try:
            for author in article.creators:
                person_uri = author.replace(" ", "-")
                person_uri = unidecode(person_uri)
                person_uri = person_uri.replace(",", "")
                person_divided = author.split(", ")
                
                data = """
                PREFIX  foaf: <http://xmlns.com/foaf/0.1/>\n
                PREFIX  frbr: <http://purl.org/vocab/frbr/core#>\n
                INSERT DATA\n
                {\n
                GRAPH <pfr:pfr> {\n
                """
                data +=f"    <pfr:{person_uri}> a foaf:Person ;\n"
                data +=f'      foaf:givenName "{person_divided[0]}" ;\n'
                data +=f'      foaf:familyName "{person_divided[1]}" .\n'
                data +=f'    <{article.id}> frbr:creator <pfr:{person_uri}> .\n'
                data +=f'    <pfr:{person_uri}> frbr:creatorOf <{article.id}> .\n'
                data +="""}\n
                }
                """
                self.graphdb_client.request_update(data=data)
        except Exception as e:
            self._logger.error(
                "Failed to insert an author in the article %s : %s.",
                article.id,
                e
            )

        try:
            for subject in article.subjects:
                subject = unidecode(subject)
                encoded_subject = subject.replace(" ", "-")
                encoded_subject = encoded_subject.replace(",", "-")
                data = """
                PREFIX  frbr: <http://purl.org/vocab/frbr/core#>\n
                PREFIX dcterms: <https://www.dublincore.org/specifications/dublin-core/dcmi-terms/>\n
                INSERT DATA\n
                {\n
                GRAPH <pfr:pfr> {\n
                """
                data +=f"    <pfr:{encoded_subject}> a frbr:Concept ;\n"
                data +=f'      dcterms:title "{subject}" .\n'
                data +=f'    <{article.id}> frbr:subject <pfr:{encoded_subject}> .\n'
                data +="""}\n
                }
                """
                self.graphdb_client.request_update(data=data)
        except Exception as e:
            self._logger.error(
                "Failed to insert a subject in the article %s : %s.",
                article.id,
                e
            )

        try:
            for date in article.dates:
                date = unidecode(date)
                data = """
                PREFIX dcterms: <https://www.dublincore.org/specifications/dublin-core/dcmi-terms/>\n
                INSERT DATA\n
                {\n
                GRAPH <pfr:pfr> {\n
                """
                data +=f'    <{article.id}> dcterms:date "{date}" .\n'
                data +="""}\n
                }
                """
                self.graphdb_client.request_update(data=data)
        except Exception as e:
            self._logger.error(
                "Failed to insert a date in the article %s : %s.",
                article.id,
                e
            )