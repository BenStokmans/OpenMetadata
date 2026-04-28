#  Copyright 2025 OpenMetadata
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
Source connection handler
"""

from urllib.parse import urlparse

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine

from metadata.generated.schema.entity.automations.workflow import (
    Workflow as AutomationWorkflow,
)
from metadata.generated.schema.entity.services.connections.database.ducklakeConnection import (
    DucklakeConnection as DucklakeConnectionConfig,
)
from metadata.generated.schema.entity.services.connections.testConnectionResult import (
    TestConnectionResult,
)
from metadata.ingestion.connections.connection import BaseConnection
from metadata.ingestion.connections.query_logger import attach_query_tracker
from metadata.ingestion.connections.test_connections import (
    test_connection_db_schema_sources,
)
from metadata.ingestion.ometa.ometa_api import OpenMetadata
from metadata.ingestion.source.database.ducklake.queries import (
    DUCKLAKE_TEST_GET_QUERIES,
)
from metadata.utils.constants import THREE_MIN


def _quote_identifier(identifier: str) -> str:
    return f'"{identifier.replace(chr(34), chr(34) * 2)}"'


def _quote_literal(value: str) -> str:
    return f"'{value.replace(chr(39), chr(39) * 2)}'"


def _bool_literal(value: bool) -> str:
    return "true" if value else "false"


def _has_s3_path(connection: DucklakeConnectionConfig) -> bool:
    paths = [
        getattr(connection, "dataPath", None),
        getattr(connection, "metadataPath", None),
    ]
    return any(path and path.lower().startswith(("s3://", "r2://", "gcs://", "gs://")) for path in paths)


class DucklakeConnection(BaseConnection[DucklakeConnectionConfig, Engine]):
    def _get_client(self) -> Engine:
        engine = create_engine(
            f"{self.service_connection.scheme.value}:///:memory:",
            pool_reset_on_return=None,
            echo=False,
        )

        event.listen(engine, "connect", self._setup_ducklake)
        attach_query_tracker(engine)

        return engine

    def _setup_ducklake(self, dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        try:
            for statement in self._get_setup_statements():
                cursor.execute(statement)
        finally:
            cursor.close()

    def _get_setup_statements(self) -> list[str]:
        statements = [
            "INSTALL ducklake",
            "LOAD ducklake",
        ]

        if self.service_connection.awsConfig or _has_s3_path(self.service_connection):
            statements.append("LOAD httpfs")

        secret_statement = self._get_s3_secret_statement()
        if secret_statement:
            statements.append(secret_statement)

        statements.append(self._get_attach_statement())
        statements.append(f"USE {_quote_identifier(self._get_catalog_name())}")

        return statements

    def _get_catalog_name(self) -> str:
        return self.service_connection.catalogName or "ducklake"

    def _get_attach_statement(self) -> str:
        connection = self.service_connection
        options = [
            f"CREATE_IF_NOT_EXISTS {_bool_literal(connection.createIfNotExists)}",
        ]

        if connection.dataPath:
            options.append(f"DATA_PATH {_quote_literal(connection.dataPath)}")
            options.append(f"OVERRIDE_DATA_PATH {_bool_literal(connection.overrideDataPath)}")

        if connection.readOnly:
            options.append("READ_ONLY")

        options_sql = f" ({', '.join(options)})" if options else ""

        return (
            f"ATTACH {_quote_literal(f'ducklake:{connection.metadataPath}')} "
            f"AS {_quote_identifier(self._get_catalog_name())}{options_sql}"
        )

    def _get_s3_secret_statement(self) -> str | None:
        aws_config = self.service_connection.awsConfig
        if not aws_config:
            return None

        options = ["TYPE s3"]
        access_key = getattr(aws_config, "awsAccessKeyId", None)
        secret_key = getattr(aws_config, "awsSecretAccessKey", None)
        session_token = getattr(aws_config, "awsSessionToken", None)
        region = getattr(aws_config, "awsRegion", None)
        endpoint = getattr(aws_config, "endPointURL", None)
        profile_name = getattr(aws_config, "profileName", None)

        if access_key and secret_key:
            options.append("PROVIDER config")
            options.append(f"KEY_ID {_quote_literal(access_key)}")
            options.append(f"SECRET {_quote_literal(secret_key.get_secret_value())}")
        else:
            options.append("PROVIDER credential_chain")
            if profile_name:
                options.append("CHAIN config")
                options.append(f"PROFILE {_quote_literal(profile_name)}")

        if region:
            options.append(f"REGION {_quote_literal(region)}")
        if session_token:
            options.append(f"SESSION_TOKEN {_quote_literal(session_token)}")
        if endpoint:
            endpoint_value = str(endpoint).rstrip("/")
            parsed_endpoint = urlparse(endpoint_value)
            options.append(f"ENDPOINT {_quote_literal(parsed_endpoint.netloc or endpoint_value)}")
            if parsed_endpoint.scheme == "http":
                options.append("USE_SSL false")

        return f"CREATE OR REPLACE SECRET openmetadata_ducklake_s3 ({', '.join(options)})"

    def get_connection_dict(self) -> dict:
        raise NotImplementedError("get_connection_dict is not implemented for Ducklake")

    def test_connection(
        self,
        metadata: OpenMetadata,
        automation_workflow: AutomationWorkflow | None = None,
        timeout_seconds: int | None = THREE_MIN,
    ) -> TestConnectionResult:
        return test_connection_db_schema_sources(
            metadata=metadata,
            engine=self.client,
            service_connection=self.service_connection,
            automation_workflow=automation_workflow,
            queries={"GetQueries": DUCKLAKE_TEST_GET_QUERIES},
            timeout_seconds=timeout_seconds,
        )
