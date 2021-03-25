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

# Globals

# ASCII CODE 219: Block, graphic character
SUBSTITUTE_BLOCK_CHAR = '█' # pylint: disable=unused-variable

# Note: NULL byte: '\x00'
# Note: BS (backspace) byte: '\x08'
# See: http://jkorpela.fi/chars/c0.html
# See: http://www.aboutmyip.com/AboutMyXApp/AsciiChart.jsp
CONTROL_CHARACTER_REGEX = re.compile("[\x00-\x1f\x7f]")

# Public Functions ------------------------------------------------------------>

def is_defined_string(value): # pylint: disable=unused-variable
    """
    Returns true if the specified value is a non-zero length String
    """
    if isinstance(value, str) and value:
        return True
    return False


def remove_control_characters(text): # pylint: disable=unused-variable
    """
    Remove control characters from the specified String
    """
    return CONTROL_CHARACTER_REGEX.sub('', text)


def sanitize_control_characters(text, substitute_char): # pylint: disable=unused-variable
    """
    Sanitize control characters in the specified String by replacing them with the specified substitute character
    """
    return CONTROL_CHARACTER_REGEX.sub(substitute_char, text)
