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

import sys
import logging
import datetime
import csv

from cloudant.view import View

from lib.constants import constants

from lib.utils import logger_util
from lib.utils import string_util
from lib.utils import error_util

# Globals

CSV_FIELD_ID = "ID"
CSV_FIELD_NAME = "Name"
CSV_FIELD_CONFLICTS = "Conflicts"

DOCS_PROCESSED_MAJOR_FACTOR = 100
DOCS_PROCESSED_MINOR_FACTOR = 10

DEFAULT_LOGGER = logging.getLogger("conflict_scanner")

# Classes --------------------------------------------------------------------->

class ConflictScanner: # pylint: disable=unused-variable
    """
    TODO
    """

    def __init__(self, database, deletion_mode, ddoc, csv_file):
        """
        Constructor
        """

        self._database = database
        self._deletion_mode = deletion_mode
        self._ddoc = ddoc
        self._csv_file = csv_file

        self._total_conflicted_documents = 0
        self._total_resolved_documents = 0
        self._total_conflicted_revisions = 0
        self._total_deleted_revisions = 0
        self._csv_file_handle = None
        self._csv_file_writer = None


    def __del__(self):
        """
        Destructor
        """

        self._shutdown_csv_file()


    def __str__(self):
        """
        TODO
        """

        line = '=' * 80
        result = [
            "",
            line,
            "Details",
            line,
            "",
            "- Total Conflicted Documents:         {0}".format(self._total_conflicted_documents),
            "- Total Resolved Documents:           {0}".format(self._total_resolved_documents),
            "- Total Conflicted Revisions:         {0}".format(self._total_conflicted_revisions),
            "- Total Deleted Revisions:            {0}".format(self._total_deleted_revisions),
            ""
        ]

        return "\n".join(result)


    # Public Methods ---------------------------------------------------------->

    def scan(self, logger=DEFAULT_LOGGER):
        """
        TODO
        """

        database_connection = self._database.get_database_connection()

        if database_connection is None:
            logger.error("Database connection is closed.")
            return

        logger.info("Scanning Cloudant database for document conflicts...")

        # Start timer

        start_time = datetime.datetime.now()

        # Open CSV file

        self._init_csv_file()

        # Iterate over entire Cloudant View result set page by page

        # TODO: QUESTION: Will this work for rate-limited Cloudant accounts (e.g. HTTP 429)?

        view = View(
            ddoc=self._ddoc,
            view_name=constants.VIEW_NAME)

        for row in view.result:

            self._process_row(row)

            # Show progress

            if self._is_major_progress_interval():

                if not self._deletion_mode:
                    sys.stdout.write("\n")
                    sys.stdout.flush()

                logger.info("Conflicted Documents Processed: %d.", self._total_conflicted_documents)

            elif self._is_minor_progress_interval():

                if not self._deletion_mode:
                    sys.stdout.write(".")
                    sys.stdout.flush()

                # TODO: QUESTION: Is it necessary to add a delay to reduce any potential load
                # on the Cloudant database cluster?
                # time.sleep(1)

        # Reset progress output

        if not self._deletion_mode:
            sys.stdout.write("\n")
            sys.stdout.flush()

        # Close CSV file

        self._shutdown_csv_file()

        # Stop timer

        end_time = datetime.datetime.now()
        elapsed_time = end_time - start_time

        # Print status message

        # TODO: Outline ms in brackets
        logger.info("Successfully scanned Cloudant database for document conflicts.")


    # Private Methods --------------------------------------------------------->

    def _init_csv_file(self, logger=DEFAULT_LOGGER):
        """
        Open CSV file
        """

        logger.info("Opening CSV file: %s...", self._csv_file)

        self._csv_file_handle = open(self._csv_file, "w", newline="", encoding="utf-8")

        fieldnames = [
            CSV_FIELD_ID,
            CSV_FIELD_NAME,
            CSV_FIELD_CONFLICTS
        ]

        self._csv_file_writer = csv.DictWriter(
            f=self._csv_file_handle,
            fieldnames=fieldnames,
            dialect="excel")

        self._csv_file_writer.writeheader()

        logger.info("Successfully Opened CSV file: %s.", self._csv_file)


    def _shutdown_csv_file(self, logger=DEFAULT_LOGGER):
        """
        Close CSV file
        """

        if self._csv_file_handle:
            logger.info("Closing CSV file: %s...", self._csv_file)
            self._csv_file_handle.close()
            logger.info("Successfully closed CSV file: %s.", self._csv_file)
            self._csv_file_handle = None


    def _process_row(self, row, logger=DEFAULT_LOGGER):
        """
        TODO
        """

        # e.g.
        # {
        #    "id":"agapic@ca.ibm.com",
        #    "key":"agapic@ca.ibm.com",
        #    "value":[
        #       "263-b01372f0f37ec98867bce7a2a015402a",
        #       "164-aa6ffd5138393226f3bd65da320fa75a"
        #    ]
        # }

        if logger_util.is_enabled_for_trace(logger):
            logger_util.log_trace(logger, str(row))

        # Validate row
        # TODO: REVISIT: Should we abort the entire scan when an exception is encountered ?

        error = self._validate_row(
            row=row,
            index=self._total_conflicted_documents)

        if error:
            logger.error(error)
            return

        self._total_conflicted_documents += 1

        # Delete conflicted revisions

        # if self._deletion_mode:
            # TODO

        # Serialize document to CSV file record

        self._serialize_row(row)


    @staticmethod
    def _validate_row(row, index):
        """
        TODO
        """

        error = ""

        if not row:
            # Error: Undefined row
            # Note: This should never happen
            error = "Undefined row encountered in the view result set at index [{0}]." \
                    .format(index)
        elif not constants.PROPERTY_ID in row:
            # Error: Undefined row ID
            # Note: This should never happen
            error = "Row with an undefined ID encountered in the view result set at index [{0}]." \
                    .format(index)
        elif not constants.PROPERTY_KEY in row:
            # Error: Undefined row key
            # Note: This should never happen
            doc_id = row[constants.PROPERTY_ID]
            error = "Row with an undefined key encountered in the view result set at index [{0}]. " \
                    "Document ID: {1}." \
                    .format(index, doc_id)
        elif not constants.PROPERTY_VALUE in row:
            # Error: Undefined row value
            # Note: This should never happen
            doc_id = row[constants.PROPERTY_ID]
            error = "Row with an undefined value encountered in the view result set at index [{0}]. " \
                    "Document ID: {1}." \
                    .format(index, doc_id)
        elif not isinstance(row[constants.PROPERTY_VALUE], list) or \
                len(row[constants.PROPERTY_VALUE]) == 0:
            # Error: Invalid or empty list of conflicted document revisions
            # Note: This should never happen
            doc_id = row[constants.PROPERTY_ID]
            error = "Invalid or empty list of conflicted document revisions encountered " \
                    "in the view result set at index [{0}]. " \
                    "Document ID: {1}." \
                    .format(index, doc_id)

        return error


    def _serialize_row(self, row, logger=DEFAULT_LOGGER):
        """
        Serialize row to CSV file record
        """

        # Document ID

        field_id = row[constants.PROPERTY_ID]

        # Document Name
        # Sanitize key (if defined)

        key = row[constants.PROPERTY_KEY]
        field_name = None

        if string_util.is_defined_string(key):
            field_name = string_util.sanitize_control_characters(
                text=key,
                substitute_char=string_util.SUBSTITUTE_BLOCK_CHAR)
        else:
            field_name = constants.VALUE_UNRESOLVED

        # Conflicted Document Revisions

        value = row[constants.PROPERTY_VALUE]
        field_conflicts = len(value)

        self._total_conflicted_revisions += field_conflicts

        # Write CSV row

        try:
            self._csv_file_writer.writerow({
                CSV_FIELD_ID: field_id,
                CSV_FIELD_NAME: field_name,
                CSV_FIELD_CONFLICTS: field_conflicts
            })
        except ValueError as err:
            message = "Failed to write CSV row to file: %s. Document ID: %s."
            logger.error(message, self._csv_file, field_id)
            error_util.log_exception(logger, err)


    def _is_major_progress_interval(self):
        """
        Determine whether the number Cloudant documents processed qualifies as major progress
        """

        if (self._total_conflicted_documents % DOCS_PROCESSED_MAJOR_FACTOR) == 0:
            return True
        return False


    def _is_minor_progress_interval(self):
        """
        Determine whether the number Cloudant documents processed qualifies as minor progress
        """

        if (self._total_conflicted_documents % DOCS_PROCESSED_MINOR_FACTOR) == 0:
            return True
        return False
