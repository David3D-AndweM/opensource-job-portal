import boto3
from django.conf import settings
import mimetypes


class AWS:
    def __init__(self):
        # Initialize the S3 and CloudFront clients
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME  # Ensure you have this in your settings
        )
        self.cloudfront_client = boto3.client(
            'cloudfront',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

    def push_to_s3(
        self, file_obj, bucket_name=None, folder="", new_name=None, public_read=True
    ):
        filename = new_name or file_obj.name  # Use new_name or fall back to the original file name
        key = f"{folder}/{filename}" if folder else filename  # Construct the key

        # Guess the MIME type
        mime = mimetypes.guess_type(filename)[0] or 'application/octet-stream'

        # Upload the file
        self.s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            key,
            ExtraArgs={'ContentType': mime, 'ACL': 'public-read' if public_read else 'private'}
        )

        return [key, bucket_name]

    def cloudfront_invalidate(self, paths):
        # Create invalidation for the specified paths
        distribution_id = settings.CLOUDFRONT_DISTRIBUTION_ID  # Ensure you have the distribution ID in your settings
        self.cloudfront_client.create_invalidation(
            DistributionId=distribution_id,
            InvalidationBatch={
                'Paths': {
                    'Quantity': len(paths),
                    'Items': paths
                },
                'CallerReference': str(hash(frozenset(paths)))  # Unique reference for each invalidation
            }
        )
