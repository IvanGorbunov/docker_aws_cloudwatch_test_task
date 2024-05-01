import argparse
import asyncio
import logging

from drivers.docker import DockerRunner


logger = logging.getLogger(__name__)


async def main(args):
    docker_runner = DockerRunner(args.docker_image, args.bash_command)
    docker_runner.run()
    if not docker_runner.container:
        logger.error("Failed to run docker container.")

    try:
        for log_line in docker_runner:
            logger.info(log_line)

    except KeyboardInterrupt:
        return


def parse_args():
    parser = argparse.ArgumentParser(prog="Test Task", description="Task that test me")

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
    asyncio.run(main(args))
