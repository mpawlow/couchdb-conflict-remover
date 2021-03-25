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

# pylint: disable=invalid-name

# Modules

# Globals

# Private Functions ----------------------------------------------------------->

def const(name):
    """
    Constant annotation
    """

    # pylint: disable=unused-argument

    def fset(self, value):
        """
        Set constant value (illegal)
        """
        message = "Overriding a constant value is an illegal operation: {0} = {1}.".format(
            name.__name__,
            value)
        raise TypeError(message)


    def fget(self):
        """
        Get constant value
        """
        return name()


    return property(fget, fset)


# Private Classes ------------------------------------------------------------->

class _Constants():

    """
    Collection of global constants
    """

    # pylint: disable=missing-docstring
    # pylint: disable=no-method-argument
    # pylint: disable=too-many-public-methods

    @const
    def JSON_FORMAT_INDENT():
        return 3

    @const
    def DDOC_NAME():
        return "conflicts"

    @const
    def VIEW_NAME():
        return "conflicts"

    @const
    def PROPERTY_ID():
        return "id"

    @const
    def PROPERTY_KEY():
        return "key"

    @const
    def PROPERTY_VALUE():
        return "value"

    @const
    def VALUE_UNRESOLVED():
        return "__UNRESOLVED__"


constants = _Constants() # pylint: disable=unused-variable
