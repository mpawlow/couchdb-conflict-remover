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

from lib.utils import logger_util

# Globals

MIN_VERSION_PYTHON = (3, 9)

DEFAULT_LOGGER = logging.getLogger("python_util")

# Public Functions ------------------------------------------------------------>

def validate_version(logger=DEFAULT_LOGGER): # pylint: disable=unused-variable
    """
    Validates whether the minimum Python interpreter version is satisfied
    """

    if sys.version_info < MIN_VERSION_PYTHON:
        logger.error("Python version %s.%s or later is required.", MIN_VERSION_PYTHON[0], MIN_VERSION_PYTHON[1])
        return False

    logger_util.log_trace(
        logger,
        "Detected Python version: %s.%s.%s",
        sys.version_info.major,
        sys.version_info.minor,
        sys.version_info.micro)

    return True
