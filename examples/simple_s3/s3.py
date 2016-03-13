from cloudarmy.core.base import BaseTemplate
from cloudarmy.core import register
from troposphere import Ref
from troposphere.s3 import Bucket, PublicRead


@register('s3')
class S3Template(BaseTemplate):

    description = """
    AWS CloudFormation Sample Template S3_Bucket:
    Sample template showing how to create a publicly accessible
    S3 bucket.
    """

    s3bucket = Bucket(
        "S3Bucket", AccessControl=PublicRead
    )

    outputs = {
        'BucketName': {
            'Value': Ref('S3Bucket'),
            'Description': 'Name of S3 bucket to hold website content'
        }
    }
