# jarpc - just another RPC
# Copyright (C) 2019  Eugene Ershov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum


class StatusCode(Enum):
    SUCCESS = 0
    BAD_FORMAT = 1
    UNKNOWN_COMMAND = 2
    BAD_PARAMS = 3
    INTERNAL_ERROR = 4


class MessageType(Enum):
    UNKNOWN_TYPE = 0
    REQUEST = 1
    RESPONSE = 2
