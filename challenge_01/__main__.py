"""An AWS Python Pulumi program"""

import pulumi
import pulumi_aws as pulumi_aws

bucket_name = "challenge-01-bucket"

# Create an AWS resource (S3 Bucket)
bucket = pulumi_aws.s3.Bucket(bucket_name)

# Export the name of the bucket
pulumi.export('challenge-01-bucket', bucket.id)

postgresql = pulumi_aws.rds.Cluster("postgresql",
    cluster_identifier="aurora-cluster-demo",
    engine="aurora-postgresql",
    availability_zones=[
        "us-west-2a"
    ],
    database_name="s3_db",
    master_username="foo",
    master_password="Change11me",
    backup_retention_period=5,
    preferred_backup_window="07:00-09:00")

assume_role = pulumi_aws.iam.get_policy_document(statements=[pulumi_aws.iam.GetPolicyDocumentStatementArgs(
    effect="Allow",
    principals=[pulumi_aws.iam.GetPolicyDocumentStatementPrincipalArgs(
        type="Service",
        identifiers=["lambda.amazonaws.com"],
    )],
    actions=["sts:AssumeRole"],
)])
iam_for_lambda = pulumi_aws.iam.Role("iam_for_lambda",
    name="iam_for_lambda",
    assume_role_policy=assume_role.json)
func = pulumi_aws.lambda_.Function("func",
    code=pulumi.FileArchive("lambda_files.zip"),
    name="example_lambda_name",
    role=iam_for_lambda.arn,
    handler="index.handler",
    runtime="python3.10")
allow_bucket = pulumi_aws.lambda_.Permission("allow_bucket",
    statement_id="AllowExecutionFromS3Bucket",
    action="lambda:InvokeFunction",
    function=func.arn,
    principal="s3.amazonaws.com",
    source_arn=bucket.arn)
bucket_notification = pulumi_aws.s3.BucketNotification("bucket_notification",
    bucket=bucket.id,
    lambda_functions=[pulumi_aws.s3.BucketNotificationLambdaFunctionArgs(
        lambda_function_arn=func.arn,
        events=["s3:ObjectCreated:*"],
        filter_prefix="AWSLogs/",
        filter_suffix=".log",
    )])
