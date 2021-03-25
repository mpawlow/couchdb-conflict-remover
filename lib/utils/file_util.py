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

from lib.utils import error_util

# Globals

DEFAULT_LOGGER = logging.getLogger("file_util")

# Public Functions ------------------------------------------------------------>

def create_text_file(file, content, logger=DEFAULT_LOGGER):  # pylint: disable=unused-variable
    """
    Create the results summary text file
    """

    logger.info("Creating text file: %s...", file)

    # Write summary file content

    try:
        with open(file, "w", newline="", encoding="utf-8", errors="strict") as file_handle:
            file_handle.write(content)
    except ValueError as err:
        logger.error("Failed to create text file: %s.", file)
        error_util.log_exception(logger, err)
        return False
    except OSError as err:
        logger.error("Failed to create text file: %s.", file)
        error_util.log_exception(logger, err)
        return False

    logger.info("Successfully created text file: %s.", file)

    return True
