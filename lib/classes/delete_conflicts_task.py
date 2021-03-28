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

from lib.constants import constants
from lib.classes.task_interface import TaskInterface
from lib.utils import logger_util
from lib.utils import error_util

# Globals

DEFAULT_LOGGER = logging.getLogger("delete_conflicts_task")

# Classes --------------------------------------------------------------------->

class DeleteConflictsTask(TaskInterface): # pylint: disable=unused-variable
    """
    TODO
    """

    def __init__(self, database, conflicts, csv_file):
        """
        Constructor
        """

        self._database = database
        self._conflicts = conflicts or []
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
            "Deletion Details",
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

    def run(self, logger=DEFAULT_LOGGER):
        """
        TODO
        """

        logger.info("Deleting document conflicts from database...")

        # Start timer

        start_time = datetime.datetime.now()

        # Open CSV file

        self._init_csv_file()

        # Iterate over conflicted documents

        index = 0

        for row in self._conflicts:
            self._process_row(index, row)
            index += 1

        # Close CSV file

        self._shutdown_csv_file()

        # Stop timer

        end_time = datetime.datetime.now()
        elapsed_time = (end_time - start_time).total_seconds() * 1000  # ms

        # Print status message

        logger.info("Successfully deleted document conflicts from database (%d ms).", elapsed_time)

        return True


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
            constants.CSV_FIELD_DELETED,
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

        # Print row

        display_row = self._get_display_row(index, row)
        logger.info(display_row)

        # Track total number of conflicted documents

        self._total_conflicted_documents += 1

        # Track number of conflicted document revisions

        field_conflicts = len(row[constants.PROPERTY_VALUE])

        # Track total number of conflicted document revisions

        self._total_conflicted_revisions += field_conflicts

        # Delete conflicted document revisions

        deleted_revisions = self._delete_conflicted_revisions(index, row)

        # Generate CSV fields

        fields = {}
        fields[constants.CSV_FIELD_ID] = row[constants.PROPERTY_ID]
        fields[constants.CSV_FIELD_NAME] = row[constants.PROPERTY_KEY]
        fields[constants.CSV_FIELD_CONFLICTS] = field_conflicts
        fields[constants.CSV_FIELD_DELETED] = len(deleted_revisions)
        fields[constants.CSV_FIELD_REVISIONS] = deleted_revisions

        # Serialize document to CSV file record

        self._serialize_csv_fields(fields)


    @staticmethod
    def _get_display_row(index, row):
        """
        TODO
        """

        conflicts_count = len(row[constants.PROPERTY_VALUE])
        display_row = "[{0}] Document ID: {1}. {2}: {3}. {4}: {5}.".format(
            index,
            row[constants.PROPERTY_ID],
            constants.CSV_FIELD_NAME,
            row[constants.PROPERTY_KEY],
            constants.CSV_FIELD_CONFLICTS,
            conflicts_count)

        return display_row


    def _delete_conflicted_revisions(self, document_index, row, logger=DEFAULT_LOGGER):
        """
        TODO
        """

        document_id = row[constants.PROPERTY_ID]
        revisions = row[constants.PROPERTY_VALUE]
        conflicted_revision_count = len(revisions)
        deleted_revision_count = 0
        deleted_revisions = []
        revision_index = 0

        logger.info("Deleting all conflicted revisions: %s (%d)...", document_id, conflicted_revision_count)

        for revision_id in revisions:

            # Print revision

            display_revision = self._get_display_revision(document_index, revision_index, revision_id)
            logger.info(display_revision)

            # Delete revision

            status = self._database.delete_document_revision(
                document_id=document_id,
                revision_id=revision_id)

            if status:
                deleted_revision_count +=1
                deleted_revisions.append(revision_id)

            revision_index += 1

        # Track total number of deleted revisions

        self._total_deleted_revisions += deleted_revision_count

        # Track total number of resolved documents

        if conflicted_revision_count == deleted_revision_count:
            logger.info("Successfully deleted all conflicted revisions: %s (deleted: %d out of %d).",
                document_id, deleted_revision_count, conflicted_revision_count)

            self._total_resolved_documents += 1
        else:
            logger.error("Failed to delete all conflicted revisions: %s (deleted %d out of %d).",
                document_id, deleted_revision_count, conflicted_revision_count)

        return deleted_revisions


    @staticmethod
    def _get_display_revision(document_index, revision_index, revision_id):
        """
        TODO
        """

        display_revision = "[{0}][{1}] Revision ID: {2}.".format(
            document_index,
            revision_index,
            revision_id)

        return display_revision


    def _serialize_csv_fields(self, fields, logger=DEFAULT_LOGGER):
        """
        Serialize fields to CSV file record
        """

        field_id = fields[constants.CSV_FIELD_ID]

        # List of conflicted document revisions

        field_revisions = "; ".join(fields[constants.CSV_FIELD_REVISIONS])

        # Write CSV row

        try:
            self._csv_file_writer.writerow({
                constants.CSV_FIELD_ID: field_id,
                constants.CSV_FIELD_NAME: fields[constants.CSV_FIELD_NAME],
                constants.CSV_FIELD_CONFLICTS: fields[constants.CSV_FIELD_CONFLICTS],
                constants.CSV_FIELD_DELETED:  fields[constants.CSV_FIELD_DELETED],
                constants.CSV_FIELD_REVISIONS: field_revisions
            })
        except ValueError as err:
            message = "Failed to write CSV row to file: %s. Document ID: %s."
            logger.error(message, self._csv_file, field_id)
            error_util.log_exception(logger, err)
