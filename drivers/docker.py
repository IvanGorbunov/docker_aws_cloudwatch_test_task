import docker


class DockerRunner:
    def __init__(self, docker_image: str, bash_command: str):
        self.client = docker.from_env()
        self.docker_image = docker_image
        self.bash_command = bash_command
        self.container = None

    def run(self):
        self.container = self.client.containers.run(
            self.docker_image,
            command=f'sh -c "{self.bash_command}"',
            detach=True,
            auto_remove=False,
            stream=True,
        )

    def __iter__(self):
        return self.container.logs(stream=True, stdout=True, stderr=True)
