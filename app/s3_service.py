import enum

import boto3

s3_client = boto3.client(
    's3',
    endpoint_url="https://s3.us-west-004.backblazeb2.com",
    region_name="us-west-004",
    aws_access_key_id="004e9bf4baea5940000000007",
    aws_secret_access_key="K004P7/917xjAk8gjoFq4lomgKbI2hs"
)


class PresignType(enum.Enum):
    GET = 'get_object'
    PUT = 'put_object'


def create_presigned_url(object_name, c_type, p_type, bucket_name="Lame-bucket", expiration=3600):
    response = s3_client.generate_presigned_url(
        p_type,
        Params={
            'Bucket': bucket_name,
            'Key': object_name,
            # 'ContentType': c_type
        },
        ExpiresIn=expiration
    )
    return response
