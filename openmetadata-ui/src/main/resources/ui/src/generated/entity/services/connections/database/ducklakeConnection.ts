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
     * Optional credentials used by DuckDB to read DuckLake catalogs or data paths in
     * S3-compatible object storage. Leave empty for public HTTPS catalogs.
     */
    awsConfig?: DucklakeS3Credentials;
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
 * Optional credentials used by DuckDB to read DuckLake catalogs or data paths in
 * S3-compatible object storage. Leave empty for public HTTPS catalogs.
 *
 * Optional credentials and connection settings for DuckLake catalogs or data stored in
 * S3-compatible object storage.
 */
export interface DucklakeS3Credentials {
    /**
     * Optional Amazon Resource Name of a role to assume.
     */
    assumeRoleArn?: string;
    /**
     * Optional identifier for the assumed role session.
     */
    assumeRoleSessionName?: string;
    /**
     * Optional source identity for the assumed role session.
     */
    assumeRoleSourceIdentity?: string;
    /**
     * AWS or S3-compatible access key ID.
     */
    awsAccessKeyId?: string;
    /**
     * Optional region for AWS or S3-compatible object storage.
     */
    awsRegion?: string;
    /**
     * AWS or S3-compatible secret access key.
     */
    awsSecretAccessKey?: string;
    /**
     * Optional session token for temporary AWS credentials.
     */
    awsSessionToken?: string;
    /**
     * Use the default AWS credential provider chain.
     */
    enabled?: boolean;
    /**
     * Optional endpoint URL for S3-compatible object storage.
     */
    endPointURL?: string;
    /**
     * Optional AWS profile used by the credential provider chain.
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
