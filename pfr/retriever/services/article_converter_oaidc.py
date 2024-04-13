"""
Convert a plain text XML list of record in the Open Archives Initiative
Protocol format 'aoi_dc' into structured data.
"""
import io
import re
import xml.sax
import logging
from pydantic import ValidationError
from unidecode import unidecode

from shared.models.article import Article
from shared.models.articles_page import ArticlesPage


class ArticleConverterOAIDC(xml.sax.ContentHandler):
    """
    Convert a plain text XML list of record in the Open Archives Initiative
    Protocol format 'aoi_dc' into structured data.

    It's based on the XML SAX parser for python. This parser read data
    in a sequential way.

    When it encounter en opening element, startElement() is called.
    endElement() when it is a closing one.
    Between them, the characters() function is called
    on each character readed.

    Parsing steps :

        1. When a "record" opening element is found, _current_record_dict
            variable is initialized with an empty dict.
        2. When an other element is found, it can be used to fill the record
            dictionnary with data.
        3. When the record closing element is found, we try to create a Article
            objet with the accumulated data. If the creation is successfull,
            the object is added to the records_list.
    At the end of the parsing, the records_list is populated with
        the converted records

    Notes
    -------
    http://www.openarchives.org/OAI/openarchivesprotocol.html#ListRecords

    Example of XML entry
    -------
    See in the test folder for examples

    Parameters
    ----------
    _logger : Logger
        The service logger.

    records_elements: ArticlesPage
        Contains the record list to populate and the elements to
        continue requesting the API if more records can be retrieved.

    _current_record_dict : dict
        The dictionnary containing the current record's data during parsing

    _accumulator : str
        The string accumulator

    _node_name_conversion : dict
        A dictionnary used redirect on specific save function corresponding
        to the element tag.
    """

    def __init__(self):
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self.clear()

        # nodes names vs methods to use to save their data
        self._node_name_conversion = {
            "identifier": self._save_id,
            "datestamp": self._save_modified_at,
            "dc:title": self._save_title,
            "dc:creator": self._save_creator,
            "dc:subject": self._save_subject,
            "dc:description": self._save_description,
            "dc:date": self._save_date,
            "resumptionToken": self._save_token,
            "error": self._error_node
        }
    
    def clear(self):
        self.records_elements = ArticlesPage()
        self._current_record_dict = None
        self._accumulator = io.StringIO("")

    def startElement(self, name, attrs):
        """
        Called when a node start. If it's a new record node,
        the current record is replaced with an eloty dict to clear the data.
        Reset the string accumulator.

        Parameters
        ----------
        name : str
            Name of the found name

        attrs: dict
            attributes of the node

        Returns
        -------
        None
        """
        self._accumulator = io.StringIO("")
        if name == "record":
            self._current_record_dict = {}
        if name == "resumptionToken":
            if "cursor" in attrs:
                self.records_elements.resumption_token_cursor = \
                    attrs["cursor"]
            if "completeListSize" in attrs:
                self.records_elements.resumption_total_size = \
                    attrs["completeListSize"]

    def endElement(self, name):
        """
        Called when an element ends. The name is used
        against the methods dictionnary. The returned method
        contains the process to save the corresponding data.

        Parameters
        ----------
        name : str
            Name of the found name

        Returns
        -------
        None
        """
        if name == "record":
            self._save_record()
        else:
            if name in self._node_name_conversion:
                self._node_name_conversion[name]()

        self._accumulator = io.StringIO("")

    def characters(self, content):
        """
        Read a character and add it to the accumulator buffer

        Parameters
        ----------
        content : str
            Content read by the parser

        Returns
        -------
        None
        """
        self._accumulator.write(content)

    def _save_token(self):
        """
        Save the resumption token used in list completion

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.records_elements.resumption_token = self._accumulator.getvalue()

    def _error_node(self):
        """
        An error was detected into the xml file

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        raise ConnectionAbortedError(
            "Error node detected into the response : "
            f"{self._accumulator.getvalue()}"
            )

    def _save_record(self):
        """
        Read a character and add it to the accumulator buffer

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            arxiv_record = Article.model_validate(
                self._current_record_dict
                )
            self.records_elements.records.append(arxiv_record)
        except ValidationError as ve:
            try:
                self._logger.error(
                    "An validation error occured when converting "
                    "a record : %s.",
                    ve,
                    exc_info=True
                )
                self._logger.error(
                    "Faulty record : %s",
                    self._current_record_dict,
                    exc_info=True
                )
            except Exception as e:
                self._logger.error(
                    "An unexpected error occured when converting "
                    "a record : %s.",
                    e,
                    exc_info=True
                )

    def _save_id(self):
        """
        Save the record's id.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self._current_record_dict["id"] = self._accumulator.getvalue()

    def _save_modified_at(self):
        """
        Save the record's last modification date.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self._current_record_dict["modified_at"] = \
            self._accumulator.getvalue() + " 00:00:00"

    def _save_title(self):
        """
        Save the record's title.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        title = unidecode(self._accumulator.getvalue())
        title = re.sub(r'[^A-Za-z0-9, ]+', '', title)
        self._current_record_dict["title"] = title

    def _save_creator(self):
        """
        Save a record's creator. If the creators key is not present
        in the record dict, initialize it with an empty list.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if "creators" not in self._current_record_dict:
            self._current_record_dict["creators"] = []
        
        creator = unidecode(self._accumulator.getvalue())
        self._current_record_dict["creators"].append(creator)

    def _save_subject(self):
        """
        Save a record's subject. If the subjects key is not present
        in the record dict, initialize it with an empty list.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if "subjects" not in self._current_record_dict:
            self._current_record_dict["subjects"] = []
                
        subject = unidecode(self._accumulator.getvalue())
        subject = re.sub(r'[^A-Za-z0-9, ]+', '', subject)
        self._current_record_dict["subjects"].append(subject)

    def _save_description(self):
        """
        Save a record's description.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if "description" not in self._current_record_dict:
            self._current_record_dict["description"] = ""
        self._current_record_dict["description"] += self._accumulator.getvalue().replace('\\n', ' ')

    def _save_date(self):
        """
        Save a record's date. If the dates key is not present
        in the record dict, initialize it with an empty list.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if "dates" not in self._current_record_dict:
            self._current_record_dict["dates"] = []
        self._current_record_dict["dates"].append(
            self._accumulator.getvalue() + " 00:00:00")

    def convert(self, data: str) -> ArticlesPage:
        """
        Launch the conversion process of a plain XML string data to a list
        of Records.

        Convert the string into a readable stream, then create a sax parser
        and give it this class to tune the behaviour of the parser. At the
        end, give the stream to the parser.

        Parameters
        ----------
        None

        Returns
        -------
        None

        Exception
        -------
        Exception

        """
        try:
            if not isinstance(data, str):
                raise TypeError("record data to parse is not of the right"
                                f" type {type(data)}. str needed.")

            buffer = io.StringIO(data)
            parser = xml.sax.make_parser()
            parser.setFeature(xml.sax.handler.feature_namespaces, 0)
            parser.setContentHandler(self)
            parser.parse(buffer)
        except ConnectionAbortedError as ce:
            self._logger.error(
                "Arxiv response returned an error. %s", ce)
        except Exception as e:
            self._logger.critical(
                "A critical error occured. Aborting the "
                "conversion's process. %s",
                e,
                exc_info=True
            )
            raise RuntimeError() from e
        return self.records_elements

