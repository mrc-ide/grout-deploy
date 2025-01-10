from constellation import config

class GroutConfig:
    def __init__(self, path, config_name):
        dat = config.read_yaml(f"{path}/{config_name}.yml")

        # docker
        docker_image = config.config_dict(dat, ["docker", "image"])
        docker_repo = config_config_string(docker_image, ["repo"])
        print("docker repo is")
        print(docker_repo)

        # packit

        # datasets