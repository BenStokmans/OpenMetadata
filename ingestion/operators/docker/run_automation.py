#  Copyright 2025 Collate
#  Licensed under the Collate Community License, Version 1.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  https://github.com/open-metadata/OpenMetadata/blob/main/ingestion/LICENSE
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""
Entrypoint to run an automation workflow
"""

import json
import logging
import os

from metadata.automations.execute_runner import execute
from metadata.generated.schema.entity.automations.workflow import (
    Workflow as AutomationWorkflow,
)
from metadata.utils.logger import set_loggers_level


def main():
    """Load the automation workflow JSON provided by the server and execute it."""

    config = os.getenv("config")  # noqa: SIM112
    if not config:
        raise RuntimeError("Missing environment variable `config` with the Automations Workflow dict.")

    # Default test connection to INFO logs
    set_loggers_level(logging.INFO)

    automation_workflow_dict = json.loads(config)
    automation_workflow = AutomationWorkflow.model_validate(automation_workflow_dict)

    execute(automation_workflow)


if __name__ == "__main__":
    main()
