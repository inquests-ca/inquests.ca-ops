import re

import boto3
import botocore


class S3Client:

    def __init__(self, bucket):
        self._bucket = bucket
        session = boto3.Session(profile_name='migration')
        self._s3_client = session.client('s3')
        self._s3_client_url_generator = session.client(
            's3',
            config=botocore.client.Config(signature_version=botocore.UNSIGNED)
        )

    def generate_s3_key(self, segments, file_type):
        escaped_segments = []
        for segment in segments:
            if segment is None:
                escaped_segments.append('MissingData')
            else:
                # Escape given strings to avoid need for URL encoding.
                escaped_segments.append(re.sub(r'[^a-zA-Z0-9]+', '-', segment).strip('-'))
        return '/'.join(escaped_segments) + '.' + file_type

    def generate_object_url(self, key):
        """Generate S3 object URL for given object key."""
        # Currently no other way to get the object link with the Boto client.
        # See https://stackoverflow.com/a/48197877
        return self._s3_client_url_generator.generate_presigned_url(
            'get_object',
            ExpiresIn=0,
            Params={
                'Bucket': self._bucket,
                'Key': key
            }
        )

    def object_exists(self, key):
        """Return True if object with given key exists."""
        try:
            self._s3_client.get_object(
                Bucket=self._bucket,
                Key=key,
            )
            return True
        except self._s3_client.exceptions.NoSuchKey:
            return False

    def upload_pdf(self, file_path, key):
        """Upload PDF at given local path to S3 under given key."""
        self._s3_client.upload_file(
            file_path,
            self._bucket,
            key,
            ExtraArgs={
                'ContentDisposition': 'inline',
                'ContentType': 'application/pdf'
            },
        )
