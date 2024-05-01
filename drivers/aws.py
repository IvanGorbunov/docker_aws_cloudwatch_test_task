import logging
import time

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class AWSRunner:
    def __init__(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region: str = "us-west-2",
        aws_cloudwatch_group: str = "this-test",
        aws_cloudwatch_stream: str = "this-test-proj",
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_cloudwatch_stream = aws_cloudwatch_stream
        self.aws_cloudwatch_group = aws_cloudwatch_group
        self.aws_region = aws_region
        self.client = boto3.client(
            "logs",
            region_name=aws_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.retention_period_in_days = 1

    def __enter__(self):
        try:
            self.create_aws_cloudwatch()
        except ClientError as e:
            logger.error(f"Failed to connect to AWS CloudWatch: {e}", exc_info=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            try:
                self.clean_up()
            except ClientError as e:
                logger.error(f"Failed to clean up AWS CloudWatch: {e}", exc_info=True)

    def create_aws_cloudwatch(self) -> None:
        if not self.is_group_exist:
            self.client.create_log_group(
                logGroupName=self.aws_cloudwatch_group,
                tags={"RetentionPeriod": str(self.retention_period_in_days)},
            )

        if not self.is_stream_exist:
            self.client.create_log_stream(
                logGroupName=self.aws_cloudwatch_group, logStreamName=self.aws_cloudwatch_stream
            )

    @property
    def is_group_exist(self) -> bool | None:
        response = self.client.describe_log_groups(logGroupNamePrefix=self.aws_cloudwatch_group)
        for group in response["logGroups"]:
            if self.aws_cloudwatch_group == group["logGroupName"]:
                return True

    @property
    def is_stream_exist(self) -> bool | None:
        response = self.client.describe_log_streams(logStreamNamePrefix=self.aws_cloudwatch_stream)
        for stream in response["logStreams"]:
            if self.aws_cloudwatch_stream == stream["logGroupName"]:
                return True

    def send_message(self, message: bytes) -> None:
        self.client.put_log_events(
            logGroupName=self.aws_cloudwatch_group,
            logStreamName=self.aws_cloudwatch_stream,
            logEvents=[
                {"timestamp": int(round(time.time() * 1000)), "message": message.decode("utf-8")}
            ],
        )

    def clean_up(self) -> None:
        self.client.delete_log_group(logGroupName=self.aws_cloudwatch_group)
