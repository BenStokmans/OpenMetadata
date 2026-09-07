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

"""Regression tests for Kubernetes job entrypoints in ingestion images."""

from pathlib import Path

INGESTION_ROOT = Path(__file__).parents[4]
ENTRYPOINTS = {"main.py", "run_automation.py", "exit_handler.py"}


def test_kubernetes_job_entrypoints_exist() -> None:
    """Every script referenced by K8sPipelineClient must exist in the build context."""

    runner_directory = INGESTION_ROOT / "operators" / "docker"

    assert {path.name for path in runner_directory.glob("*.py")} >= ENTRYPOINTS


def test_ingestion_images_copy_all_kubernetes_job_entrypoints() -> None:
    """Both ingestion image definitions must package every Python entrypoint."""

    expected_copy = "COPY --chown=airflow:0 ingestion/operators/docker/*.py /opt/airflow/"

    for dockerfile_name in ("Dockerfile", "Dockerfile.ci"):
        dockerfile = INGESTION_ROOT / dockerfile_name
        assert expected_copy in dockerfile.read_text(encoding="utf-8")
