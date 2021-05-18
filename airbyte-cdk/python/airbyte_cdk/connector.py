#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


import json
import os
import pkgutil
from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import AirbyteConnectionStatus, ConnectorSpecification


class AirbyteSpec(object):
    @staticmethod
    def from_file(file_name: str):
        with open(file_name) as file:
            spec_text = file.read()
        return AirbyteSpec(spec_text)

    def __init__(self, spec_string):
        self.spec_string = spec_string


class Connector(ABC):

    # can be overridden to change an input config
    def configure(self, config: Mapping[str, Any], temp_dir: str) -> Mapping[str, Any]:
        """
        Persist config in temporary directory to run the Source job
        """
        config_path = os.path.join(temp_dir, "config.json")
        self.write_config(config, config_path)
        return config

    @staticmethod
    def read_config(config_path: str) -> Mapping[str, Any]:
        with open(config_path, "r") as file:
            contents = file.read()
        return json.loads(contents)

    @staticmethod
    def write_config(config: Mapping[str, Any], config_path: str):
        with open(config_path, "w") as fh:
            fh.write(json.dumps(config))

    def spec(self, logger: AirbyteLogger) -> ConnectorSpecification:
        """
        Returns the spec for this integration. The spec is a JSON-Schema object describing the required configurations (e.g: username and password)
        required to run this integration.
        """
        raw_spec: Optional[bytes] = pkgutil.get_data(self.__class__.__module__.split(".")[0], "spec.json")
        if not raw_spec:
            raise ValueError("Unable to find spec.json.")
        return ConnectorSpecification.parse_obj(json.loads(raw_spec))

    @abstractmethod
    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration e.g: if a provided Stripe API token can be used to connect
        to the Stripe API.
        """
