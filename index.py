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

from lib.utils import python_util
from lib.utils import logger_util
from lib.utils import date_util
from lib.utils import directory_util
from lib.utils.obfuscation_util import obfuscate

from lib.classes.scan_conflicts_task import ScanConflictsTask

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

CSV_FILE_EXTENSION = ".csv"
TEXT_FILE_EXTENSION = ".txt"
RESULTS_DIR = "results"
FILE_PREFIX = "conflicts_"
FILE_SEGMENT_DETAILS = "details_"
FILE_SEGMENT_RESULTS = "results_"
FILE_SEGMENT_SUMMARY = "summary_"

DEFAULT_RESULTS_DIRNAME = "{0}/{1}{2}{3}".format(
    RESULTS_DIR,
    FILE_PREFIX,
    FILE_SEGMENT_RESULTS,
    CURRENT_TIME)

DEFAULT_CSV_FILENAME = "{0}{1}{2}{3}".format(
    FILE_PREFIX,
    FILE_SEGMENT_DETAILS,
    CURRENT_TIME,
    CSV_FILE_EXTENSION)

DEFAULT_SUMMARY_FILENAME = "{0}{1}{2}{3}".format(
    FILE_PREFIX,
    FILE_SEGMENT_SUMMARY,
    CURRENT_TIME,
    TEXT_FILE_EXTENSION)

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
        help="The name of the target Cloudant database.")

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

    parser.add_argument(
        "-c",
        "--csv-file",
        default=DEFAULT_CSV_FILENAME,
        help="The CSV filename to use for outlining Cloudant database conflicts. "
             "Default: {0}.".format(DEFAULT_CSV_FILENAME))

    parser.add_argument(
        "-s",
        "--summary-file",
        default=DEFAULT_SUMMARY_FILENAME,
        help="The summary filename to use for outlining Cloudant database conflicts. "
             "Default: {0}.".format(DEFAULT_SUMMARY_FILENAME))

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
        "- Results Directory: {0}.".format(args.results_dir),
        "- CSV File: {0}.".format(args.csv_file),
        "- Summary File: {0}.".format(args.summary_file)
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
        "- Cloudant Database: {0}.".format(env_dict[PROP_CLOUDANT_ACCOUNT]),
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


def _main(logger=DEFAULT_LOGGER):
    """
    The main function.
    """

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

    # Run Task: Remove Conflicts

    csv_file = _get_qualified_filename(args.results_dir, args.csv_file)
    summary_file = _get_qualified_filename(args.results_dir, args.summary_file)
    scan_conflicts_task = ScanConflictsTask(
        cloudant_account=env_dict[PROP_CLOUDANT_ACCOUNT],
        cloudant_api_key=env_dict[PROP_CLOUDANT_API_KEY],
        cloudant_password=env_dict[PROP_CLOUDANT_PASSWORD],
        database_name=args.database_name,
        deletion_mode=args.delete,
        csv_file=csv_file,
        summary_file=summary_file)

    status = scan_conflicts_task.run()

    if status is False:
        _fatal_exit()

    # Exit process

    sys.exit(0)


# Main ------------------------------------------------------------------------>

if __name__ == "__main__":
    _main()
