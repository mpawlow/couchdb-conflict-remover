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

import re
import time

# Globals

# UTC ±00:00 (Zulu)
# Format: ISO 8601
# e.g. 2015-01-01T00:00:00.000Z
UTC_DATE_REGEX = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}Z$")

# Public Functions ------------------------------------------------------------>

def is_valid_utc_date(date): # pylint: disable=unused-variable
    """
    Determines whether the specified date conforms to the UTC date format
    """

    match = re.fullmatch(UTC_DATE_REGEX, date)

    if match:
        return True

    return False

def get_current_timestamp(): # pylint: disable=unused-variable
    """
    Retrieves the current local time in a custom timestamp format
    """

    return time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
