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

from json import JSONDecodeError
from requests.exceptions import HTTPError
from cloudant.error import CloudantDocumentException

# Globals

# Public Functions ------------------------------------------------------------>

def log_exception(logger, err): # pylint: disable=unused-variable
    """
    Log a general exception
    """

    separator = "\n"
    exception_name = type(err).__name__
    exception_message = str(err)
    string_buffer = (
        "Exception:",
        "Name: {0}.".format(exception_name),
        "Message: {0}.".format(exception_message)
    )
    content = separator.join(string_buffer)

    logger.exception(content)


def log_json_error(logger, err): # pylint: disable=unused-variable
    """
    Log a JSON decode exception
    """

    # See: https://docs.python.org/3/library/json.html

    exception_name = type(err).__name__

    if not isinstance(err, JSONDecodeError):
        message = "Exception is not an instance of JSONDecodeError: {0}".format(
            exception_name)
        logger.error(message)
        log_exception(logger, err)
        return

    separator = "\n"
    exception_message = str(err)
    string_buffer = (
        "Exception:",
        "Name: {0}.".format(exception_name),
        "Message: {0}.".format(err.msg),
        "Character Index: {0}.".format(err.pos),
        "Line Number: {0}.".format(err.lineno),
        "Column Number: {0}.".format(err.colno),
        "Error: {0}.".format(exception_message)
    )
    content = separator.join(string_buffer)

    logger.exception(content)
    logger.error("JSON Document:\n%s", err.doc)


def log_http_error(logger, err): # pylint: disable=unused-variable
    """
    Log a HTTPError
    """

    exception_name = type(err).__name__

    if not isinstance(err, HTTPError):
        message = "Exception is not an instance of HTTPError: {0}".format(
            exception_name)
        logger.error(message)
        log_exception(logger, err)
        return

    # TODO: Handle individual status codes: e.g. 400, 401, 403, 404, 409, 500

    separator = "\n"
    exception_message = str(err)
    status_code = err.response.status_code
    url = err.response.url
    string_buffer = (
        "Exception:",
        "Name: {0}.".format(exception_name),
        "Status Code: {0}.".format(status_code),
        "URL: {0}.".format(url),
        "Message: {0}.".format(exception_message)
    )
    content = separator.join(string_buffer)

    logger.error(content)


def log_cloudant_document_exception(logger, err): # pylint: disable=unused-variable
    """
    Log a CloudantDocumentException
    """

    exception_name = type(err).__name__

    if not isinstance(err, CloudantDocumentException):
        message = "Exception is not an instance of CloudantDocumentException: {0}".format(
            exception_name)
        logger.error(message)
        log_exception(logger, err)
        return

    separator = "\n"
    exception_message = str(err)
    code = err.code
    string_buffer = (
        "Exception:",
        "Name: {0}.".format(exception_name),
        "Code: {0}.".format(code),
        "Message: {0}.".format(exception_message)
    )
    content = separator.join(string_buffer)

    logger.error(content)
