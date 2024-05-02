from docker import DockerClient, from_env
from docker.constants import DEFAULT_NPIPE, IS_WINDOWS_PLATFORM
from docker.errors import DockerException

from pathlib import Path


class DockerRunner:
    def __init__(self, docker_image: str, bash_command: str):
        self.client = self.get_docker_client()
        self.docker_image = docker_image
        self.bash_command = bash_command
        self.container = None

    def __iter__(self):
        return self.container.logs(stdout=True, stderr=True, stream=True, follow=True)

    @staticmethod
    def get_docker_client() -> DockerClient:
        """Load docker client."""
        try:
            return from_env()
        except DockerException:
            return DockerClient(
                DEFAULT_NPIPE
                if IS_WINDOWS_PLATFORM
                else f"unix://{Path.home()}/.docker/desktop/docker.sock"
            )

    def run(self) -> None:
        self.container = self.client.containers.run(
            self.docker_image,
            # command=f"bash -c {self.bash_command}",
            command=[
                "/bin/sh",
                "-c",
                self.bash_command,
            ],
            detach=True,
            auto_remove=False,
            stream=True,
        )
