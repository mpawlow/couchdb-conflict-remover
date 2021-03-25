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

# TODO: FIXME
# pylint: disable=too-many-arguments

# Modules

import datetime
import logging

from lib.constants import constants
from lib.utils import file_util
from lib.classes.task_interface import TaskInterface
from lib.classes.cloudant_database import CloudantDatabase
from lib.classes.conflict_scanner import ConflictScanner

# Globals

DEFAULT_LOGGER = logging.getLogger("scan_conflicts_task")

# Classes --------------------------------------------------------------------->

class ScanConflictsTask(TaskInterface): # pylint: disable=unused-variable
    """
    TODO
    """

    def __init__(self, cloudant_account, cloudant_api_key, cloudant_password, database_name, deletion_mode, csv_file,
            summary_file):
        """
        Constructor
        """

        self._cloudant_account = cloudant_account
        self._cloudant_api_key = cloudant_api_key
        self._cloudant_password = cloudant_password
        self._database_name = database_name
        self._deletion_mode = deletion_mode
        self._csv_file = csv_file
        self._summary_file = summary_file

        self._doc_count = 0
        self._elapsed_time = None


    def __str__(self):
        """
        TODO
        """
        # TODO
        return ""


    # Public Methods ---------------------------------------------------------->

    def run(self, logger=DEFAULT_LOGGER):
        """
        TODO
        """

        status = False

        logger.info("Running remove conflicts task...")

        # Start timer

        start_time = datetime.datetime.now()

        # Cloudant Database

        database = CloudantDatabase(
            account=self._cloudant_account,
            api_key=self._cloudant_api_key,
            password=self._cloudant_password,
            database_name=self._database_name)

        # Open database account connection

        status = database.init_client()

        if status is False:
            logger.error("Failed to run remove conflicts task.")
            return False

        # Database Connection

        status = database.open_database()

        if status is False:
            logger.error("Failed to run remove conflicts task.")
            return False

        # Document Count

        self._doc_count = database.get_doc_count()

        logger.info("Cloudant Document Count: %d.", self._doc_count)

        # Design Document

        ddoc = database.get_design_document(
            ddoc_name=constants.DDOC_NAME)

        if ddoc is None:
            logger.error("Failed to run remove conflicts task.")
            return False

        # Scan Documents

        remover = ConflictScanner(
            database=database,
            deletion_mode=self._deletion_mode,
            ddoc=ddoc,
            csv_file=self._csv_file)

        remover.scan()

        # Close database account connection

        database.shutdown_client()

        # Stop timer

        end_time = datetime.datetime.now()
        self._elapsed_time = end_time - start_time

        logger.info("Successfully ran remove conflicts task.")

        # Generate summary content

        overview_content = self._get_overview_content()
        details_content = str(remover)
        summary_content = "{0}{1}".format(
            overview_content,
            details_content)

        # Create summary file

        file_util.create_text_file(
            file=self._summary_file,
            content=summary_content,
            logger=DEFAULT_LOGGER)

        # Display summary content

        print(summary_content)

        return True


    # Private Methods --------------------------------------------------------->

    def _get_overview_content(self):
        """
        Generate overview content
        """

        line = '=' * 80
        result = [
            "",
            line,
            "Overview",
            line,
            "",
            "- Cloudant Account:                   {0}".format(self._cloudant_account),
            "- Cloudant Database:                  {0}".format(self._database_name),
            "- Total Documents:                    {0}".format(self._doc_count),
            "",
            "- Elapsed Time:                       {0}".format(self._elapsed_time),
            ""
        ]

        return "\n".join(result)
