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
import json
import logging
import logging.config

# Globals

LOG_LEVEL_NAME_TRACE = "TRACE"
LOG_LEVEL_VALUE_TRACE = 5

# TODO: REVISIT: Specify logging configuration file name as an option
LOG_CONF_FILE = "config/logging.json"

# Public Functions ------------------------------------------------------------>

def is_enabled_for_trace(logger): # pylint: disable=unused-variable
    """
    Determine whether the logger is enabled for the TRACE logging level
    """

    return logger.isEnabledFor(LOG_LEVEL_VALUE_TRACE)


def log_trace(logger, msg, *args, **kwargs): # pylint: disable=unused-variable
    """
    Log message at custom TRACE level
    """

    logger.log(LOG_LEVEL_VALUE_TRACE, msg, *args, **kwargs)


def init_logging_subsystem(logger): # pylint: disable=unused-variable
    """
    Initialize logging subsystem
    """

    # Add custom log level: TRACE

    logging.addLevelName(LOG_LEVEL_VALUE_TRACE, LOG_LEVEL_NAME_TRACE)

    # Check if the logging configuration file exists

    if not os.path.exists(LOG_CONF_FILE):
        message = "Failed to load logging configuration file: {0}. File does not exist.".format(
            LOG_CONF_FILE)
        print(message)
        return False

    # Load the logging configuration file

    try:
        # Open JSON logging configuration file (read, text)

        with open(LOG_CONF_FILE, "rt") as file_handle:
            json_file_contents = json.load(file_handle)

        # Load JSON configuration as a dictionary

        logging.config.dictConfig(json_file_contents)

    except (OSError, ValueError, TypeError, AttributeError, ImportError) as err:
        message = "Failed to load logging configuration file: {0}.".format(
            LOG_CONF_FILE)
        print(message)
        print(err)
        return False

    log_trace(logger, "Successfully initialized the logging subsystem.")

    return True
