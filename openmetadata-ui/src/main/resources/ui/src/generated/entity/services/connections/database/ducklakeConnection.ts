/*
 *  Copyright 2026 Collate.
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *  http://www.apache.org/licenses/LICENSE-2.0
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
/**
 * DuckLake is an open Lakehouse format that is built on SQL and Parquet
 */
export interface DucklakeConnection {
    /**
     * Optional AWS or S3-compatible credentials used by DuckDB to read DuckLake data paths such
     * as s3://, r2://, gcs://, or gs://.
     */
    awsConfig?: AWSCredentials;
    /**
     * Catalog name used to attach DuckLake in DuckDB.
     */
    catalogName?:         string;
    connectionArguments?: { [key: string]: any };
    connectionOptions?:   { [key: string]: string };
    /**
     * Create a new DuckLake if the configured metadata catalog does not exist.
     */
    createIfNotExists?: boolean;
    /**
     * Regex to only include/exclude databases that matches the pattern.
     */
    databaseFilterPattern?: FilterPattern;
    /**
     * Optional name to give to the database in OpenMetadata. If left blank, the attached
     * catalog name is used.
     */
    databaseName?: string;
    /**
     * Database Schema of the data source. This is optional parameter, if you would like to
     * restrict the metadata reading to a single schema.
     */
    databaseSchema?: string;
    /**
     * Optional DuckLake data storage location. Examples: s3://bucket/path/ or /path/to/files/.
     */
    dataPath?: string;
    /**
     * DuckLake metadata catalog path or connection string. Examples: metadata.ducklake,
     * postgres:dbname=postgres, or a DuckDB secret name.
     */
    metadataPath: string;
    /**
     * Override the data path stored in DuckLake metadata for this connection.
     */
    overrideDataPath?: boolean;
    /**
     * Attach DuckLake in read-only mode.
     */
    readOnly?: boolean;
    /**
     * Regex to only include/exclude schemas that matches the pattern.
     */
    schemaFilterPattern?: FilterPattern;
    /**
     * SQLAlchemy driver scheme options.
     */
    scheme?:                     DucklakeScheme;
    supportsDBTExtraction?:      boolean;
    supportsMetadataExtraction?: boolean;
    /**
     * Regex to only include/exclude tables that matches the pattern.
     */
    tableFilterPattern?: FilterPattern;
    /**
     * Service Type
     */
    type?: DucklakeType;
}

/**
 * Optional AWS or S3-compatible credentials used by DuckDB to read DuckLake data paths such
 * as s3://, r2://, gcs://, or gs://.
 *
 * AWS credentials configs.
 */
export interface AWSCredentials {
    /**
     * The Amazon Resource Name (ARN) of the role to assume. Required Field in case of Assume
     * Role
     */
    assumeRoleArn?: string;
    /**
     * An identifier for the assumed role session. Use the role session name to uniquely
     * identify a session when the same role is assumed by different principals or for different
     * reasons. Required Field in case of Assume Role
     */
    assumeRoleSessionName?: string;
    /**
     * The Amazon Resource Name (ARN) of the role to assume. Optional Field in case of Assume
     * Role
     */
    assumeRoleSourceIdentity?: string;
    /**
     * AWS Access key ID.
     */
    awsAccessKeyId?: string;
    /**
     * AWS Region
     */
    awsRegion: string;
    /**
     * AWS Secret Access Key.
     */
    awsSecretAccessKey?: string;
    /**
     * AWS Session Token.
     */
    awsSessionToken?: string;
    /**
     * Enable AWS IAM authentication. When enabled, uses the default credential provider chain
     * (environment variables, instance profile, etc.). Defaults to false for backward
     * compatibility.
     */
    enabled?: boolean;
    /**
     * EndPoint URL for the AWS
     */
    endPointURL?: string;
    /**
     * The name of a profile to use with the boto session.
     */
    profileName?: string;
}

/**
 * Regex to only include/exclude databases that matches the pattern.
 *
 * Regex to only fetch entities that matches the pattern.
 *
 * Regex to only include/exclude schemas that matches the pattern.
 *
 * Regex to only include/exclude tables that matches the pattern.
 */
export interface FilterPattern {
    /**
     * List of strings/regex patterns to match and exclude only database entities that match.
     */
    excludes?: string[];
    /**
     * List of strings/regex patterns to match and include only database entities that match.
     */
    includes?: string[];
}

/**
 * SQLAlchemy driver scheme options.
 */
export enum DucklakeScheme {
    Duckdb = "duckdb",
}

/**
 * Service Type
 *
 * Service type.
 */
export enum DucklakeType {
    Ducklake = "Ducklake",
}
