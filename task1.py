import boto3
import json

client = boto3.client('iam')

# Create Dev Role
dev_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "sts:AssumeRole"
        }
    ]
}

dev_role = client.create_role(
    RoleName='Dev',
    AssumeRolePolicyDocument=json.dumps(dev_policy_document)
)

# Create User Role
user_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"AWS": "*"},
            "Action": "sts:AssumeRole"
        }
    ]
}

user_role = client.create_role(
    RoleName='User',
    AssumeRolePolicyDocument=json.dumps(user_policy_document)
)

print("Roles created successfully.")

# Attach full S3 access to Dev
client.attach_role_policy(
    RoleName='Dev',
    PolicyArn='arn:aws:iam::aws:policy/AmazonS3FullAccess'
)

# Attach list/get policy to User role
user_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": ["s3:ListBucket", "s3:GetObject"],
            "Resource": [
                "arn:aws:s3:::lecture1",
                "arn:aws:s3:::lecture1/*"
            ]
        }
    ]
}

# Inline policy for User role
client.put_role_policy(
    RoleName='User',
    PolicyName='UserS3Access',
    PolicyDocument=json.dumps(user_policy)
)

print("Roles and policies created successfully.")


# Create a new IAM user
user_response = client.create_user(UserName='new_user')

# Attach a basic permission to allow the user to assume roles
client.attach_user_policy(
    UserName='new_user',
    PolicyArn='arn:aws:iam::aws:policy/IAMUserChangePassword'
)

print("User created successfully.")

# Assume the Dev role
sts_client = boto3.client('sts')

assumed_role_object = sts_client.assume_role(
    RoleArn='arn:aws:iam::376129856599:role/Dev',
    RoleSessionName='AssumeDevRoleSession'
)

credentials = assumed_role_object['Credentials']

# Use the assumed role's credentials to interact with S3
s3_dev = boto3.client(
    's3',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
    region_name='us-east-1'
)

# Specify the region and bucket name
bucket_name = 'lecture1llll'

# Create S3 bucket with region specification
s3_dev.create_bucket(
    Bucket=bucket_name
)
# Define the bucket policy
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::376129856599:role/User"
            },
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                f"arn:aws:s3:::{bucket_name}",
                f"arn:aws:s3:::{bucket_name}/*"
            ]
        }
    ]
}

# Convert the policy to a JSON string
bucket_policy_json = json.dumps(bucket_policy)

# Set the bucket policy
s3_dev.put_bucket_policy(
    Bucket=bucket_name,
    Policy=bucket_policy_json
)

print("Bucket created and policy set successfully.")


# Upload assignment1.txt
s3_dev.put_object(
    Bucket=bucket_name,
    Key='assignment1.txt',
    Body='Empty Assignment 1'
)

# Upload assignment2.txt
s3_dev.put_object(
    Bucket=bucket_name,
    Key='assignment2.txt',
    Body='Empty Assignment 2'
)

# Upload recording1.jpg
with open('/Users/luyihan/Desktop/5800/sss.png', 'rb') as img:
    s3_dev.put_object(
        Bucket=bucket_name,
        Key='recording1.jpg',
        Body=img
    )

print("Bucket and objects created successfully.")

# Assume the User role
assumed_user_role = sts_client.assume_role(
    RoleArn='arn:aws:iam::376129856599:role/User',
    RoleSessionName='AssumeUserRoleSession'
)

user_credentials = assumed_user_role['Credentials']

# Use the User role's credentials to interact with S3
s3_user = boto3.client(
    's3',
    aws_access_key_id=user_credentials['AccessKeyId'],
    aws_secret_access_key=user_credentials['SecretAccessKey'],
    aws_session_token=user_credentials['SessionToken']
)

# List objects with prefix 'assignment' and calculate total size
response = s3_user.list_objects_v2(Bucket='lecture1llll', Prefix='assignment')

total_size = 0
for obj in response.get('Contents', []):
    total_size += obj['Size']

print(f"Total size of objects with prefix 'assignment': {total_size} bytes")

# Use Dev role again
assumed_dev_role = sts_client.assume_role(
    RoleArn='arn:aws:iam::376129856599:role/Dev',
    RoleSessionName='AssumeDevRoleSession'
)

dev_credentials = assumed_dev_role['Credentials']

# Use the assumed Dev role's credentials to interact with S3
s3_dev2 = boto3.client(
    's3',
    aws_access_key_id=dev_credentials['AccessKeyId'],
    aws_secret_access_key=dev_credentials['SecretAccessKey'],
    aws_session_token=dev_credentials['SessionToken']
)

# List and delete all objects
response = s3_dev2.list_objects_v2(Bucket='lecture1llll')
for obj in response.get('Contents', []):
    s3_dev2.delete_object(Bucket='lecture1llll', Key=obj['Key'])

# Delete the bucket
s3_dev2.delete_bucket(Bucket='lecture1llll')

print("Bucket and all objects deleted successfully.")
