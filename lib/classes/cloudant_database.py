"""
    Copyright 2021 Mike Pawlowski

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

# Pylint Rule Overrides

# Modules

import logging
import datetime
import json
from urllib.parse import quote
from urllib.parse import quote_plus
from pprint import pformat
import requests
from requests.exceptions import HTTPError
from cloudant.client import Cloudant
from cloudant.error import CloudantDocumentException

from lib.constants import constants
from lib.utils import error_util
from lib.utils import logger_util

# Globals

PROPERTY_BOOKMARK = "bookmark"
PROPERTY_DOCS = "docs"

DEFAULT_LOGGER = logging.getLogger("cloudant_database")

# Classes --------------------------------------------------------------------->

class CloudantDatabase: # pylint: disable=unused-variable
    """
    Manages Cloudant database connection
    """

    def __init__(self, account, api_key, password, database_name):
        """
        Constructor
        """

        self._account = account
        self._api_key = api_key
        self._password = password
        self._database_name = database_name

        self._client = None
        self._database = None
        self._doc_count = 0


    def __del__(self):
        """
        Destructor
        """

        self.shutdown_client()


    # Public Methods ---------------------------------------------------------->

    def init_client(self, logger=DEFAULT_LOGGER):
        """
        Open the Cloudant account connection
        """

        logger.info("Establishing a connection with the Cloudant account: %s...", self._account)

        try:
            self._client = Cloudant(
                cloudant_user=self._api_key,
                auth_token=self._password,
                account=self._account,
                connect=True)
        except requests.exceptions.HTTPError as err:
            logger.error("Failed to establish a connection with the Cloudant account: %s.", self._account)
            error_util.log_exception(logger, err)
            return False

        logger.info("Successfully established a connection with the Cloudant account: %s.", self._account)

        return True


    def shutdown_client(self, logger=DEFAULT_LOGGER):
        """
        Close the Cloudant account connection
        """

        if self._client:
            self._client.disconnect()
            logger.info("Closed connection with the Cloudant account: %s.", self._account)
            self._client = None


    def open_database(self, logger=DEFAULT_LOGGER):
        """
        Open Cloudant database
        """

        logger.info("Opening Cloudant database: %s...", self._database_name)

        try:
            self._database = self._client[self._database_name]
        except requests.exceptions.HTTPError as err:
            logger.error("Failed to open Cloudant database: %s.", self._database_name)
            error_util.log_exception(logger, err)
            return False

        logger.info("Successfully opened Cloudant database: %s.", self._database_name)

        return True


    def get_doc_count(self, logger=DEFAULT_LOGGER):
        """
        Retrieve number of Cloudant documents in database
        """

        logger.info("Retrieving Cloudant database document count: %s...", self._database_name)

        if self._database is None:
            message = "Failed to retrieve Cloudant database document count. " \
                "Database connection is closed: {0}.".format(self._database_name)
            logger.error(message)
            return self._doc_count

        self._doc_count = self._database.doc_count()

        logger.info(
            "Successfully retrieved Cloudant document count from database: %s (%d).",
            self._database_name,
            self._doc_count)

        return self._doc_count


    def get_design_document(self, ddoc_name, logger=DEFAULT_LOGGER):
        """
        Retrieve the Cloudant design document
        """

        ddoc = None

        logger.info("Retrieving Cloudant design document: %s...", ddoc_name)

        if self._database is None:
            message = "Failed to retrieve Cloudant design document: {0}. " \
                "Database connection is closed: {1}.".format(ddoc_name, self._database_name)
            logger.error(message)
            return None

        try:
            ddoc = self._database.get_design_document(ddoc_name)
        except HTTPError as err:
            logger.error("Failed to retrieve Cloudant design document: %s.", ddoc_name)
            error_util.log_http_error(logger, err)
            return None

        if ddoc and (ddoc_name in ddoc.views):
            logger.info("Successfully retrieved Cloudant design document: %s.", ddoc_name)

            if logger_util.is_enabled_for_trace(logger):
                logger_util.log_trace(logger, "Design Document:")
                formatted_ddoc = json.dumps(ddoc, indent=constants.JSON_FORMAT_INDENT)
                logger_util.log_trace(logger, formatted_ddoc)

            return ddoc

        logger.error("Failed to retrieve Cloudant design document: %s.", ddoc_name)

        return None


    def get_document(self, document_id, logger=DEFAULT_LOGGER):
        """
        Retrieve the Cloudant document by ID (latest revision)
        """

        logger.debug("Retrieving Cloudant document: %s...", document_id)

        if self._database is None:
            message = "Failed to retrieve Cloudant document: {0}. " \
                "Database connection is closed: {1}.".format(document_id, self._database_name)
            logger.error(message)
            return None

        start_time = datetime.datetime.now()

        try:
            document = self._database[document_id]
        except KeyError as err:
            message = "Failed to retrieve Cloudant document: {0}.".format(document_id)
            logger.error(message)
            error_util.log_exception(logger, err)
            return None
        except HTTPError as err:
            message = "Failed to retrieve Cloudant document: {0}.".format(document_id)
            logger.error(message)
            error_util.log_http_error(logger, err)
            return None

        if not document:
            message = "Failed to retrieve Cloudant document: {0}. " \
                "The document is undefined.".format(document_id)
            logger.error(message)
            return None

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds() * 1000  # ms

        logger.debug("Successfully retrieved Cloudant document: %s (%d ms).", document_id, elapsed_time)

        if logger_util.is_enabled_for_trace(logger):
            formatted_document = json.dumps(document, indent=constants.JSON_FORMAT_INDENT)
            logger_util.log_trace(logger, formatted_document)

        return document


    def delete_document(self, document_id, logger=DEFAULT_LOGGER):
        """
        Delete the Cloudant document by ID
        """

        logger.info("Deleting Cloudant document: %s...", document_id)

        if self._database is None:
            message = "Failed to delete Cloudant document: {0}. " \
                "Database connection is closed: {1}.".format(document_id, self._database_name)
            logger.error(message)
            return None

        # Fetch document

        start_time = datetime.datetime.now()

        document = self.get_document(document_id, logger)

        if not document:
            message = "Failed to delete Cloudant document: {0}. " \
                "The document is undefined.".format(document_id)
            logger.error(message)
            return None

        # Delete document

        try:
            document.delete()
        except CloudantDocumentException as err:
            message = "Failed to delete Cloudant document: {0}. " \
                "The document revision ID is missing.".format(document_id)
            logger.error(message)
            error_util.log_exception(logger, err)
            return None
        except HTTPError as err:
            message = "Failed to delete Cloudant document: {0}.".format(
                document_id)
            logger.error(message)
            error_util.log_http_error(logger, err)
            return None

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds() * 1000  # ms

        logger.info("Successfully deleted Cloudant document: %s (%d ms).", document_id, elapsed_time)

        return document


    def delete_document_revision(self, document_id, revision_id, logger=DEFAULT_LOGGER):
        """
        Delete the Cloudant document revision
        """

        logger.info("Deleting Cloudant document: %s. Revision: %s...", document_id, revision_id)

        if self._database is None:
            message = "Failed to delete Cloudant document: {0}. Revision: {1}. " \
                "Database connection is closed: {2}.".format(document_id, revision_id, self._database_name)
            logger.error(message)
            return False

        start_time = datetime.datetime.now()

        document_url = self._get_document_url(document_id)

        if not document_url:
            message = "Failed to delete Cloudant document: {0}. Revision: {1}. " \
                "Document URL is undefined: {2}.".format(document_id, revision_id, self._database_name)
            logger.error(message)
            return False

        params = {
            "rev": revision_id
        }

        session = self._database.r_session
        response = session.delete(document_url, params=params)

        if logger_util.is_enabled_for_trace(logger):
            serialized_response = pformat(vars(response))
            logger_util.log_trace(logger, serialized_response)

        try:
            response.raise_for_status()
        except HTTPError as err:
            logger.error("Failed to delete Cloudant document: %s. Revision: %s.", document_id, revision_id)
            error_util.log_http_error(logger, err)
            return False

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds() * 1000  # ms

        logger.info("Successfully deleted Cloudant document: %s. Revision: %s (%d ms).",
            document_id, revision_id, elapsed_time)

        return True


    def get_query_results(self, query, logger=DEFAULT_LOGGER):
        """
        Retrieve a page of the Cloudant Query result set
        """

        page = query.get_page()

        logger.debug("Page [%d]: Retrieve Cloudant Query results...", page)

        if self._database is None:
            message = "Page [{0}]: Failed to retrieve Cloudant Query results. " \
                "Database connection is closed: {1}.".format(page, self._database_name)
            logger.error(message)
            return None

        # Run Cloudant Query

        # TODO: REFACTOR: Create timing utility

        start_time = datetime.datetime.now()

        options = query.get_query_json()
        results = self._database.get_query_result(**options)

        end_time = datetime.datetime.now()

        if not self._is_valid_results(results):
            return None

        elapsed_time = (end_time - start_time).total_seconds() * 1000  # ms

        logger.debug("Page [%d]: Successfully retrieved Cloudant Query results (%d ms).", page, elapsed_time)

        docs = results[PROPERTY_DOCS]
        bookmark = results[PROPERTY_BOOKMARK]

        query.set_bookmark(bookmark, len(docs))

        return docs


    def get_database_connection(self):
        """
        TODO
        """
        return self._database


    # Private Methods --------------------------------------------------------->

    def _is_valid_results(self, results):
        """
        Determine whether the Cloudant query result set is valid
        """

        # Docs

        if not self._is_valid_docs(results):
            return False

        # Bookmark

        if not self._is_valid_bookmark(results):
            return False

        return True


    @staticmethod
    def _is_valid_docs(results, logger=DEFAULT_LOGGER):
        """
        Determine whether the Cloudant documents is valid
        """

        # Docs: Check if missing

        if not PROPERTY_DOCS in results:
            logger.error(
                "Encountered Cloudant Query result set with missing property: %s.",
                PROPERTY_DOCS)
            return False

        # Docs: Check if defined

        docs = results[PROPERTY_DOCS]

        if not docs:
            logger.error(
                "Encountered undefined property value: %s: %s.",
                PROPERTY_DOCS,
                docs)
            return False

        return True


    @staticmethod
    def _is_valid_bookmark(results, logger=DEFAULT_LOGGER):
        """
        Determine whether the Cloudant Query bookmark is valid
        """

        # Docs: Check if missing

        if not PROPERTY_BOOKMARK in results:
            logger.error(
                "Encountered Cloudant Query result set with missing property: %s.",
                PROPERTY_BOOKMARK)
            return False

        # Docs: Check if defined

        bookmark = results[PROPERTY_BOOKMARK]

        if not bookmark:
            logger.error(
                "Encountered undefined property value: %s: %s.",
                PROPERTY_BOOKMARK,
                bookmark)
            return False

        return True


    def _get_document_url(self, document_id):
        """
        TODO
        """

        # e.g.
        # https://cdsxorg.cloudant.com/portal-common-api_ys1-dev-dallas/a.t.smith21%40ibm.com

        if not self._client:
            return None
        elif not self._client.server_url:
            return None
        elif not self._database_name:
            return None
        elif not document_id:
            return None

        encoded_database_name = quote_plus(self._database_name)
        encoded_document_id = quote(document_id, safe="")
        url_parts = (self._client.server_url, encoded_database_name, encoded_document_id)
        url = url = "/".join(url_parts)

        return url
