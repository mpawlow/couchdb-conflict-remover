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
import stat
from pathlib import Path

from lib.utils import error_util

# Globals

DEFAULT_LOGGER = logging.getLogger("directory_util")

# Public Functions ------------------------------------------------------------>

def create_directory(directory, parents=False, logger=DEFAULT_LOGGER):  # pylint: disable=unused-variable
    """
    Creates a directory to store the results
    """

    path = directory

    if not isinstance(directory, Path):
        path = Path(directory)

    logger.info("Creating directory: %s...", path)

    try:
        path.mkdir(parents=parents)
    except FileExistsError as err:
        logger.warning("Directory already exists: %s.", path)
    except OSError as err:
        logger.error("Failed to create directory: %s.", path)
        error_util.log_exception(logger, err)
        return False

    logger.info("Successfully created directory: %s.", path)

    return True


def list_directory(directory, logger=DEFAULT_LOGGER):  # pylint: disable=unused-variable
    """
    TODO
    """

    path = directory

    if not isinstance(directory, Path):
        path = Path(directory)

    logger.info("Listing directory contents: %s ...", path)

    files = []

    try:

        for file in path.iterdir():

            files.append(file)

            file_status = file.stat()
            file_mode = stat.filemode(file_status.st_mode)

            logger.info("%s  %s", file_mode, file)

    except FileNotFoundError as err:
        logger.error("Directory does not exist: %s.", path)
        logger.error("Failed to list directory contents: %s.", path)
        error_util.log_exception(logger, err)
        return files

    file_count = len(files)

    logger.info("Total: %s", file_count)
    logger.info("Successfully listed directory contents: %s.", path)

    return files
