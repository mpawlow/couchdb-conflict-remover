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

import abc

# Globals


# Classes --------------------------------------------------------------------->

class TaskInterface(metaclass=abc.ABCMeta): # pylint: disable=unused-variable
    """
    TODO
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        """
        TODO
        """
        if hasattr(subclass, "run") and \
                callable(subclass.run):
            return True

        return NotImplemented


    # Public Methods ---------------------------------------------------------->

    @abc.abstractmethod
    def run(self, logger):
        """
        TODO
        """
        raise NotImplementedError
