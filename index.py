#!/usr/bin/env python3
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

import os
import sys
import logging
import argparse
import pathlib
import datetime

from lib.constants import constants
from lib.utils import python_util
from lib.utils import logger_util
from lib.utils import date_util
from lib.utils import directory_util
from lib.utils import file_util
from lib.utils.obfuscation_util import obfuscate
from lib.classes.cloudant_database import CloudantDatabase
from lib.classes.scan_conflicts_task import ScanConflictsTask
from lib.classes.delete_conflicts_task import DeleteConflictsTask

# Authorship

# pylint: disable=unused-variable
__author__ = "Mike Pawlowski"
__copyright__ = "Copyright 2021 Mike Pawlowski"
__license__ = "Apache-2.0"
__version__ = "1.0.0"
__maintainer__ = "Mike Pawlowski"
__email__ = "mpawlow@ca.ibm.com"
__status__ = "Production"
# pylint: enable=unused-variable

# Globals

ENV_CLOUDANT_ACCOUNT = "CLOUDANT_ACCOUNT"
ENV_CLOUDANT_API_KEY = "CLOUDANT_API_KEY"
ENV_CLOUDANT_PASSWORD = "CLOUDANT_PASSWORD"

ARGUMENT_PARSER_EPILOG = \
    "=== Environment Variables ===\n" \
    "\n" \
    "CLOUDANT_ACCOUNT : Cloudant account name.\n" \
    "CLOUDANT_API_KEY : Cloudant API key.\n" \
    "CLOUDANT_PASSWORD : Cloudant password.\n" \
    "\n" \
    "=== Examples ===\n" \
    "\n" \
    "export CLOUDANT_ACCOUNT=account_name\n" \
    "export CLOUDANT_API_KEY=api_key\n" \
    "export CLOUDANT_PASSWORD=password\n" \
    "\n" \
    "python index.py -d -n projects-api_prod-dallas\n"

PROP_CLOUDANT_ACCOUNT = "cloudant_account"
PROP_CLOUDANT_API_KEY = "cloudant_api_key"
PROP_CLOUDANT_PASSWORD = "cloudant_password"

CURRENT_TIME = date_util.get_current_timestamp()

DEFAULT_RESULTS_DIRNAME = "{0}/{1}{2}{3}".format(
    "results",
    constants.FILE_PREFIX,
    "results_",
    CURRENT_TIME)

SCAN_DETAILS_CSV_FILENAME = "{0}{1}{2}{3}".format(
    constants.FILE_PREFIX,
    "scan_details_",
    CURRENT_TIME,
    constants.CSV_FILE_EXTENSION)

DELETION_DETAILS_CSV_FILENAME = "{0}{1}{2}{3}".format(
    constants.FILE_PREFIX,
    "deletion_details_",
    CURRENT_TIME,
    constants.CSV_FILE_EXTENSION)

SUMMARY_FILENAME = "{0}{1}{2}{3}".format(
    constants.FILE_PREFIX,
    "summary_",
    CURRENT_TIME,
    constants.TEXT_FILE_EXTENSION)

DEFAULT_LOGGER = logging.getLogger("index")

# Functions ------------------------------------------------------------------->

def _parse_command_line_args():
    """
    Parse command-line arguments
    """

    parser = argparse.ArgumentParser(
        epilog=ARGUMENT_PARSER_EPILOG,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "-n",
        "--database-name",
        required=True,
        help="The name of the target CouchDB / Cloudant database.")

    parser.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="Enable deletion mode. "
             "Default: False.")

    parser.add_argument(
        "-r",
        "--results-dir",
        default=DEFAULT_RESULTS_DIRNAME,
        help="The directory name to use for storing results. "
             "Default: {0}.".format(DEFAULT_RESULTS_DIRNAME))

    args = parser.parse_args()

    return args


def _display_command_line_args(args, logger=DEFAULT_LOGGER):
    """
    Display command-line argument values
    """

    separator = "\n"
    string_buffer = (
        "Command-line Arguments:",
        "- Cloudant Database: {0}.".format(args.database_name),
        "- Deletion Mode: {0}.".format(args.delete),
        "- Results Directory: {0}.".format(args.results_dir)
    )
    content = separator.join(string_buffer)

    logger.info(content)


def _parse_environment_variables(logger=DEFAULT_LOGGER):
    """
    Parse environment variables into dictionary
    """

    if not ENV_CLOUDANT_ACCOUNT in os.environ:
        logger.error("Environment variable not defined: %s.", ENV_CLOUDANT_ACCOUNT)
        return None
    elif not ENV_CLOUDANT_API_KEY in os.environ:
        logger.error("Environment variable not defined: %s.", ENV_CLOUDANT_API_KEY)
        return None
    elif not ENV_CLOUDANT_PASSWORD in os.environ:
        logger.error("Environment variable not defined: %s.", ENV_CLOUDANT_PASSWORD)
        return None

    env_dict = dict([
        (PROP_CLOUDANT_ACCOUNT, os.environ[ENV_CLOUDANT_ACCOUNT]),
        (PROP_CLOUDANT_API_KEY, os.environ[ENV_CLOUDANT_API_KEY]),
        (PROP_CLOUDANT_PASSWORD, os.environ[ENV_CLOUDANT_PASSWORD])
    ])

    return env_dict


def _display_environment_variables(env_dict, logger=DEFAULT_LOGGER):
    """
    Display environment variables
    """

    encoded_cloudant_api_key = obfuscate(env_dict[PROP_CLOUDANT_API_KEY])
    encoded_cloudant_password = obfuscate(env_dict[PROP_CLOUDANT_PASSWORD])
    separator = "\n"
    string_buffer = (
        "Environment Variables:",
        "- Cloudant Account: {0}.".format(env_dict[PROP_CLOUDANT_ACCOUNT]),
        "- Cloudant API Key: {0}.".format(encoded_cloudant_api_key),
        "- Cloudant Password: {0}.".format(encoded_cloudant_password)
    )
    content = separator.join(string_buffer)

    logger.info(content)


def _get_qualified_filename(results_dir, filename):
    """
    Gets the path of the filename qualified with the results directory
    """

    return pathlib.Path("{0}/{1}".format(results_dir, filename))


def _fatal_exit(logger=DEFAULT_LOGGER):
    """
    Exit script with fatal status
    """

    status = 1
    logger.critical("Fatal error encountered. Exit script status: %d.", status)
    sys.exit(status)


def _get_overview_content(account, database_name, doc_count, elapsed_time):
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
        "- Cloudant Account:                   {0}".format(account),
        "- Cloudant Database:                  {0}".format(database_name),
        "- Total Documents:                    {0}".format(doc_count),
        "- Elapsed Time:                       {0}".format(elapsed_time),
        ""
    ]

    return "\n".join(result)


def _main(logger=DEFAULT_LOGGER):
    """
    The main function.
    """

    # TODO: FIXME
    # pylint: disable=too-many-locals
    # TODO: FIXME
    # pylint: disable=too-many-statements

    status = False

    # Logging

    status = logger_util.init_logging_subsystem(logger)

    if status is False:
        # Should never happen
        print("Failed to initialize the logging subsystem.")
        sys.exit(1)

    # Python version

    status = python_util.validate_version()

    if status is False:
        _fatal_exit()

    # Command-line arguments

    args = _parse_command_line_args()

    # Script Banner

    logger.info("[-- CouchDB Conflict Remover --------------------------------------------------".upper())

    # Display command-line argument values

    _display_command_line_args(args)

    # Environment Variables

    env_dict = _parse_environment_variables()

    if env_dict is None:
        _fatal_exit()

    # Display environment variables

    _display_environment_variables(env_dict)

    # Create results Directory

    status = directory_util.create_directory(
        directory=args.results_dir,
        logger=DEFAULT_LOGGER)

    if status is False:
        _fatal_exit()

    # Start timer

    start_time = datetime.datetime.now()

    # Configure database connection

    account = env_dict[PROP_CLOUDANT_ACCOUNT]
    database_name = args.database_name
    database = CloudantDatabase(
        account=account,
        api_key=env_dict[PROP_CLOUDANT_API_KEY],
        password=env_dict[PROP_CLOUDANT_PASSWORD],
        database_name=database_name)

    # Initialize database client

    status = database.init_client()

    if status is False:
        _fatal_exit()

    # Open database

    status = database.open_database()

    if status is False:
        _fatal_exit()

    # Retrieve number of documents in database

    doc_count = database.get_doc_count()

    # Retrieve conflicts design document

    ddoc = database.get_design_document(
        ddoc_name=constants.DDOC_NAME)

    if ddoc is None:
        _fatal_exit()

    # Scan database for conflicted documents

    scan_details_csv_file = _get_qualified_filename(args.results_dir, SCAN_DETAILS_CSV_FILENAME)
    scan_conflicts_task = ScanConflictsTask(
        deletion_mode=args.delete,
        ddoc=ddoc,
        csv_file=scan_details_csv_file)

    status = scan_conflicts_task.run()

    if status is False:
        _fatal_exit()

    # Remove conflicted documents from database

    conflicts = scan_conflicts_task.get_conflicts()
    delete_conflicts_task = None

    if args.delete and \
            len(conflicts) != 0:

        deletion_details_csv_file = _get_qualified_filename(args.results_dir, DELETION_DETAILS_CSV_FILENAME)
        delete_conflicts_task = DeleteConflictsTask(
            database=database,
            conflicts=conflicts,
            csv_file=deletion_details_csv_file)

        status = delete_conflicts_task.run()

        if status is False:
            _fatal_exit()

    # Close database account connection

    database.shutdown_client()

    # Stop timer

    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time

    # Generate summary content

    overview_content = _get_overview_content(
        account=account,
        database_name=database_name,
        doc_count=doc_count,
        elapsed_time=elapsed_time)

    scan_details_content = str(scan_conflicts_task)

    deletion_details_content = ""

    if delete_conflicts_task:
        deletion_details_content = str(delete_conflicts_task)

    summary_content = "{0}{1}{2}".format(
        overview_content,
        scan_details_content,
        deletion_details_content)

    # Create summary file

    summary_file = _get_qualified_filename(args.results_dir, SUMMARY_FILENAME)
    file_util.create_text_file(
        file=summary_file,
        content=summary_content,
        logger=DEFAULT_LOGGER)

    # Display summary content

    print(summary_content)

    # Exit process

    sys.exit(0)


# Main ------------------------------------------------------------------------>

if __name__ == "__main__":
    _main()
