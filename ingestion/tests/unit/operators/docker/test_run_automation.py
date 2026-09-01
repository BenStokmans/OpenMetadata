#  Copyright 2026 Collate
#  Licensed under the Collate Community License, Version 1.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  https://github.com/open-metadata/OpenMetadata/blob/main/ingestion/LICENSE
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import builtins
import importlib.util
from pathlib import Path

RUNNER_PATH = Path(__file__).parents[4] / "operators/docker/run_automation.py"


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_automation_under_test", RUNNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_runner_loads_without_pyyaml(monkeypatch):
    original_import = builtins.__import__

    def import_without_yaml(name, *args, **kwargs):
        if name == "yaml" or name.startswith("yaml."):
            raise ModuleNotFoundError("No module named 'yaml'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_yaml)

    _load_runner()


def test_runner_parses_json_automation_config(monkeypatch):
    runner = _load_runner()
    validated_configs = []
    executed_workflows = []
    workflow = object()

    class WorkflowValidator:
        @staticmethod
        def model_validate(config):
            validated_configs.append(config)
            return workflow

    monkeypatch.setenv("config", '{"name": "ducklake-test"}')
    monkeypatch.setattr(runner, "AutomationWorkflow", WorkflowValidator)
    monkeypatch.setattr(runner, "execute", executed_workflows.append)

    runner.main()

    assert validated_configs == [{"name": "ducklake-test"}]
    assert executed_workflows == [workflow]
