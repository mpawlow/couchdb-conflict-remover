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
import csv

from cloudant.view import View

from lib.constants import constants
from lib.classes.task_interface import TaskInterface
from lib.utils import logger_util
from lib.utils import string_util
from lib.utils import error_util

# Globals

DEFAULT_LOGGER = logging.getLogger("scan_conflicts_task")

# Classes --------------------------------------------------------------------->

class ScanConflictsTask(TaskInterface): # pylint: disable=unused-variable
    """
    TODO
    """

    def __init__(self, deletion_mode, threshold, ddoc, csv_file):
        """
        Constructor
        """

        self._deletion_mode = deletion_mode
        self._threshold = threshold
        self._ddoc = ddoc
        self._csv_file = csv_file

        self._total_conflicted_documents = 0
        self._total_conflicted_revisions = 0
        self._csv_file_handle = None
        self._csv_file_writer = None
        self._conflicts = []


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
            "Scan Details",
            line,
            "",
            "- Total Conflicted Documents:         {0}".format(self._total_conflicted_documents),
            "- Total Conflicted Revisions:         {0}".format(self._total_conflicted_revisions),
            ""
        ]

        return "\n".join(result)


    # Public Methods ---------------------------------------------------------->

    def run(self, logger=DEFAULT_LOGGER):
        """
        TODO
        """

        logger.info("Scanning database for conflicted documents...")

        # Start timer

        start_time = datetime.datetime.now()

        # Open CSV file

        self._init_csv_file()

        # Iterate over conflicted documents in view result set

        # TODO: QUESTION: Will this work for rate-limited Cloudant accounts (e.g. HTTP 429)?

        view = View(
            ddoc=self._ddoc,
            view_name=constants.VIEW_NAME)

        index = 0

        for row in view.result:
            self._process_row(index, row)
            index += 1

        if index == 0:
            logger.info("No conflicted documents found in database.")

        # Close CSV file

        self._shutdown_csv_file()

        # Stop timer

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds() * 1000  # ms

        # Print status message

        logger.info("Successfully scanned database for conflicted documents (%d ms).", elapsed_time)

        return True


    def get_conflicts(self):
        """
        TODO
        """

        return self._conflicts


    # Private Methods --------------------------------------------------------->

    def _init_csv_file(self, logger=DEFAULT_LOGGER):
        """
        Open CSV file
        """

        logger.info("Opening CSV file: %s...", self._csv_file)

        self._csv_file_handle = open(self._csv_file, "w", newline="", encoding="utf-8")

        fieldnames = [
            constants.CSV_FIELD_ID,
            constants.CSV_FIELD_NAME,
            constants.CSV_FIELD_CONFLICTS,
            constants.CSV_FIELD_REVISIONS
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


    def _process_row(self, index, row, logger=DEFAULT_LOGGER):
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

        # Normalize row

        normalized_row = self._get_normalized_row(row)

        # Print row

        display_row = self._get_display_row(
            index=index,
            row=normalized_row)

        logger.info(display_row)

        # Track total number of conflicted documents

        self._total_conflicted_documents += 1

        # Store conflicted document in memory

        self._store_conflicted_document(normalized_row)

        # Serialize document to CSV file record

        self._serialize_row(normalized_row)


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


    @staticmethod
    def _get_normalized_row(row):
        """
        TODO
        """

        # Sanitize name

        key = row[constants.PROPERTY_KEY]
        field_name = None

        if string_util.is_defined_string(key):
            field_name = string_util.sanitize_control_characters(
                text=key,
                substitute_char=string_util.SUBSTITUTE_BLOCK_CHAR)
        else:
            field_name = constants.VALUE_UNRESOLVED

        normalized_row = {}
        normalized_row[constants.PROPERTY_ID] = row[constants.PROPERTY_ID]
        normalized_row[constants.PROPERTY_KEY] = field_name
        normalized_row[constants.PROPERTY_VALUE] = row[constants.PROPERTY_VALUE]

        return normalized_row


    def _get_display_row(self, index, row):
        """
        Serialize row to CSV file record
        """

        conflicts_count = self._get_conflicts_count(row)
        display_row = "[{0}] Document ID: {1}. {2}: {3}. {4}: {5}.".format(
            index,
            row[constants.PROPERTY_ID],
            constants.CSV_FIELD_NAME,
            row[constants.PROPERTY_KEY],
            constants.CSV_FIELD_CONFLICTS,
            conflicts_count)

        return display_row


    @staticmethod
    def _get_conflicts_count(row):
        """
        TODO
        """

        value = row[constants.PROPERTY_VALUE]
        conflicts_count = len(value)

        return conflicts_count


    def _store_conflicted_document(self, row, logger=DEFAULT_LOGGER):
        """
        TODO
        """

        if not self._deletion_mode:
            # Scan Mode
            return

        # Deletion Mode

        conflicts_count = self._get_conflicts_count(row)

        if conflicts_count <= self._threshold:
            self._conflicts.append(row)
            return

        message = "Conflicted document omitted from deletion phase due to exceeding revision threshold. " \
                  "Document ID: {0}. {1}: {2}. {3}: {4} > {5}.".format(
            row[constants.PROPERTY_ID],
            constants.CSV_FIELD_NAME,
            row[constants.PROPERTY_KEY],
            constants.CSV_FIELD_CONFLICTS,
            conflicts_count,
            self._threshold)

        logger.warning(message)


    def _serialize_row(self, row, logger=DEFAULT_LOGGER):
        """
        Serialize row to CSV file record
        """

        field_id = row[constants.PROPERTY_ID]
        field_name = row[constants.PROPERTY_KEY]

        # Number of conflicted document revisions

        field_conflicts = self._get_conflicts_count(row)

        # Track total number of conflicted document revisions

        self._total_conflicted_revisions += field_conflicts

        # List of conflicted document revisions

        value = row[constants.PROPERTY_VALUE]
        field_revisions = "; ".join(value)

        # Write CSV row

        try:
            self._csv_file_writer.writerow({
                constants.CSV_FIELD_ID: field_id,
                constants.CSV_FIELD_NAME: field_name,
                constants.CSV_FIELD_CONFLICTS: field_conflicts,
                constants.CSV_FIELD_REVISIONS: field_revisions
            })
        except ValueError as err:
            message = "Failed to write CSV row to file: %s. Document ID: %s."
            logger.error(message, self._csv_file, field_id)
            error_util.log_exception(logger, err)
