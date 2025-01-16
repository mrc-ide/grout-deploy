import os

import docker

from grout_deploy.config import GroutConfig


class GroutDocker:
    def __init__(self, cfg: GroutConfig, bind_path: str):
        self.repo = cfg.docker_image_repo
        self.image_name = cfg.docker_image_name
        self.tag = cfg.docker_image_tag
        self.port = cfg.docker_port
        self.container_name = cfg.docker_container_name
        self.bind_path = bind_path

    def __get_client(self):
        return docker.from_env()

    def start(self, pull):
        client = self.__get_client()
        repo_image = f"{self.repo}/{self.image_name}"
        if pull:
            print(f"Pulling {self.tag} from {repo_image}")
            client.images.pull(repo_image, tag=self.tag)
        host_path = os.path.abspath(self.bind_path)
        client.containers.run(
            f"{repo_image}:{self.tag}",
            detach=True,
            name=self.container_name,
            ports={5000: 5000},
            volumes={host_path: {"bind": "/data", "mode": "ro"}},
        )
        print(f"{self.container_name} is running with data mounted from {host_path}")

    def stop(self):
        client = self.__get_client()
        container = client.containers.get(self.container_name)
        container.stop()
        print(f"Stopped container {self.container_name}")
        container.remove()
        print(f"Removed container {self.container_name}")
