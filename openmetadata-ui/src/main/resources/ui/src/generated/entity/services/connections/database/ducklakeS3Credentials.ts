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
