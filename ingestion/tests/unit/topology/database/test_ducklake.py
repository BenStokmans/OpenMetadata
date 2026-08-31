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
Unit tests for the DuckLake connector.
"""

from unittest.mock import MagicMock, patch

import pytest

from metadata.generated.schema.entity.services.connections.database.ducklakeConnection import (
    DucklakeConnection as DucklakeConnectionConfig,
)
from metadata.generated.schema.security.credentials.awsCredentials import AWSCredentials
from metadata.ingestion.api.steps import InvalidSourceException
from metadata.ingestion.source.database.ducklake.connection import DucklakeConnection
from metadata.ingestion.source.database.ducklake.metadata import DucklakeSource

MOCK_WORKFLOW_CONFIG = {
    "source": {
        "type": "ducklake",
        "serviceName": "ducklake_test",
        "serviceConnection": {
            "config": {
                "type": "Ducklake",
                "metadataPath": "metadata.ducklake",
                "dataPath": "s3://warehouse/ducklake/",
                "catalogName": "ducklake",
            }
        },
        "sourceConfig": {"config": {"type": "DatabaseMetadata"}},
    },
    "sink": {"type": "metadata-rest", "config": {}},
    "workflowConfig": {
        "openMetadataServerConfig": {
            "hostPort": "http://localhost:8585/api",
            "authProvider": "openmetadata",
            "securityConfig": {"jwtToken": "test-token"},
        }
    },
}


def test_create_accepts_ducklake_connection():
    mock_metadata = MagicMock()
    with patch(
        "metadata.ingestion.source.database.common_db_source.CommonDbSourceService.__init__",
        return_value=None,
    ):
        source = DucklakeSource.create(MOCK_WORKFLOW_CONFIG["source"], mock_metadata)

    assert isinstance(source, DucklakeSource)


def test_create_raises_for_wrong_connection_type():
    mock_metadata = MagicMock()
    bad_config = dict(MOCK_WORKFLOW_CONFIG)
    bad_config["source"] = dict(MOCK_WORKFLOW_CONFIG["source"])
    bad_config["source"]["serviceConnection"] = {
        "config": {"type": "Mysql", "hostPort": "localhost:3306", "username": "root"}
    }

    with pytest.raises(InvalidSourceException):
        DucklakeSource.create(bad_config["source"], mock_metadata)


@patch("metadata.ingestion.source.database.ducklake.connection.attach_query_tracker")
@patch("metadata.ingestion.source.database.ducklake.connection.event.listen")
@patch("metadata.ingestion.source.database.ducklake.connection.create_engine")
def test_get_client_uses_in_memory_duckdb_engine(mock_create_engine, mock_listen, mock_attach_query_tracker):
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    connection = DucklakeConnection(DucklakeConnectionConfig(metadataPath="metadata.ducklake"))

    assert connection.client == mock_engine
    mock_create_engine.assert_called_once_with("duckdb:///:memory:", pool_reset_on_return=None, echo=False)
    mock_listen.assert_called_once_with(mock_engine, "connect", connection._setup_ducklake)
    mock_attach_query_tracker.assert_called_once_with(mock_engine)


def test_attach_statement_quotes_values_and_sets_ducklake_options():
    connection = DucklakeConnection(
        DucklakeConnectionConfig(
            metadataPath="meta's.ducklake",
            dataPath="s3://bucket/path's/",
            catalogName='lake"catalog',
        )
    )

    statement = connection._get_attach_statement()

    assert statement == (
        "ATTACH 'ducklake:meta''s.ducklake' AS \"lake\"\"catalog\" "
        "(CREATE_IF_NOT_EXISTS false, DATA_PATH 's3://bucket/path''s/', "
        "OVERRIDE_DATA_PATH false, READ_ONLY)"
    )


def test_setup_statements_include_ducklake_attach_and_active_catalog():
    connection = DucklakeConnection(DucklakeConnectionConfig(metadataPath="metadata.ducklake", catalogName="lake"))

    statements = connection._get_setup_statements()

    assert statements[:2] == ["INSTALL ducklake", "LOAD ducklake"]
    assert ("ATTACH 'ducklake:metadata.ducklake' AS \"lake\" (CREATE_IF_NOT_EXISTS false, READ_ONLY)") in statements
    assert statements[-1] == 'USE "lake"'


def test_s3_compatible_aws_config_maps_to_duckdb_secret():
    connection = DucklakeConnection(
        DucklakeConnectionConfig(
            metadataPath="metadata.ducklake",
            dataPath="s3://warehouse/ducklake/",
            awsConfig=AWSCredentials(
                awsAccessKeyId="access-key",
                awsSecretAccessKey="secret-key",
                awsRegion="us-east-1",
                awsSessionToken="session-token",
                endPointURL="http://minio:9000",
            ),
        )
    )

    statements = connection._get_setup_statements()
    secret_statement = next(statement for statement in statements if statement.startswith("CREATE OR REPLACE SECRET"))

    assert "LOAD httpfs" in statements
    assert "TYPE s3" in secret_statement
    assert "PROVIDER config" in secret_statement
    assert "KEY_ID 'access-key'" in secret_statement
    assert "SECRET 'secret-key'" in secret_statement
    assert "REGION 'us-east-1'" in secret_statement
    assert "SESSION_TOKEN 'session-token'" in secret_statement
    assert "ENDPOINT 'minio:9000'" in secret_statement
    assert "USE_SSL false" in secret_statement


def test_setup_ducklake_executes_statements_and_closes_cursor():
    connection = DucklakeConnection(DucklakeConnectionConfig(metadataPath="metadata.ducklake"))
    dbapi_connection = MagicMock()
    cursor = dbapi_connection.cursor.return_value

    connection._setup_ducklake(dbapi_connection, MagicMock())

    cursor.execute.assert_any_call("INSTALL ducklake")
    cursor.execute.assert_any_call("LOAD ducklake")
    cursor.execute.assert_any_call(
        "ATTACH 'ducklake:metadata.ducklake' AS \"ducklake\" (CREATE_IF_NOT_EXISTS false, READ_ONLY)"
    )
    cursor.execute.assert_any_call('USE "ducklake"')
    cursor.close.assert_called_once()


@patch("metadata.ingestion.source.database.ducklake.connection.test_connection_db_schema_sources")
def test_test_connection_delegates_to_schema_source_test(mock_test_connection):
    engine = MagicMock()
    metadata = MagicMock()
    connection = DucklakeConnection(DucklakeConnectionConfig(metadataPath="metadata.ducklake"))
    connection._client = engine

    connection.test_connection(metadata)

    assert mock_test_connection.call_args.kwargs["metadata"] == metadata
    assert mock_test_connection.call_args.kwargs["engine"] == engine
    assert mock_test_connection.call_args.kwargs["service_connection"] == connection.service_connection
    assert mock_test_connection.call_args.kwargs["queries"]["GetQueries"].strip() == "SELECT 1"
