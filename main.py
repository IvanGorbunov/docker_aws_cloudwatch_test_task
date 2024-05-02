import argparse
import asyncio
import logging
import select

import click

from drivers.aws import AWSRunner
from drivers.docker import DockerRunner

logging.basicConfig(
    level="INFO",
    format="%(asctime)s [%(levelname)s]: %(message)s",
)
logger = logging.getLogger(__name__)


def main(args: argparse.Namespace):
    docker_runner = DockerRunner(args.docker_image, args.bash_command)
    docker_runner.run()
    if not docker_runner.container:
        logger.error("Failed to run docker container.")
    with AWSRunner(
        aws_access_key_id=args.aws_access_key_id,
        aws_secret_access_key=args.aws_secret_access_key,
        aws_cloudwatch_stream=args.aws_cloudwatch_stream,
        aws_cloudwatch_group=args.aws_cloudwatch_group,
        aws_region=args.aws_region,
    ) as aws_api:
        try:
            for message in docker_runner:
                msg = message.decode("utf-8")
                aws_api.send_message(msg)
                logger.info(f"Sent message: {msg}")

            # TODO: Use select to check for available data on the container logs stream
            # while True:
            #     readable, _, _ = select.select([docker_runner.container.logs(stream=True)], [], [], 0.1)
            #     if readable:
            #         # Read available logs from the stream
            #         message = docker_runner.container.logs(stream=True).decode("utf-8")
            #         aws_api.send_message(message)
            #         logger.info(f"Sent message: {message}")
            #     else:
            #         # No new logs, wait for a short period
            #         select.select([], [], [], 0.1)

        except KeyboardInterrupt:
            return
        except Exception as e:
            logger.error(f"Failed to send message to AWS CloudWatch: {e}")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="Docker-AWS", description="Test Docker+AWS CloudWatch task."
    )

    parser.add_argument("--docker-image", required=True, help="docker image name")
    parser.add_argument(
        "--bash-command", required=True, help="bash command to run inside docker container"
    )
    parser.add_argument(
        "--aws-cloudwatch-group", required=True, help="name of an AWS CloudWatch group"
    )
    parser.add_argument(
        "--aws-cloudwatch-stream", required=True, help="name of an AWS CloudWatch stream"
    )
    parser.add_argument("--aws-access-key-id", required=True, help="AWS access key id")
    parser.add_argument("--aws-secret-access-key", required=True, help="AWS secret access key")
    parser.add_argument("--aws-region", default="us-west-1", help="name of an AWS region")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
