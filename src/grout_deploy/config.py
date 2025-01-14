from constellation import config


class GroutDatasetsConfig:
    def __init__(self, config_dict):
        self.datasets = {}
        for dataset, dataset_config in config_dict.items():
            levels_config = config.config_dict(dataset_config, ["tiles"])
            dataset_levels = {}
            for level, level_config in levels_config.items():
                packit_server = config.config_string(level_config, ["packit_server"])
                packet_id = config.config_string(level_config, ["packet_id"])
                download = config.config_string(level_config, ["download"])
                dataset_levels[level] = {
                    "packit_server": packit_server,
                    "packet_id": packet_id,
                    "download": download
                }
            self.datasets[dataset] = dataset_levels

    def get_dataset_names(self):
        return self.datasets.keys()

    def get_dataset_tile_levels(self, dataset_name: str):
        return self.datasets[dataset_name].keys()

    def get_tile_level_details(self, dataset_name: str, level: str):
        level = self.datasets[dataset_name][level]
        return level["packit_server"], level["packet_id"], level["download"]

class GroutConfig:
    def __init__(self, path: str, config_name: str):
        dat = config.read_yaml(f"{path}/{config_name}.yml")

        # docker
        docker = config.config_dict(dat, ["docker"])
        docker_image = config.config_dict(docker, ["image"])
        self.docker_repo = config.config_string(docker_image, ["repo"])
        self.docker_name = config.config_string(docker_image, ["name"])
        self.docker_tag = config.config_string(docker_image, ["tag"])
        self.docker_container_name = config.config_string(docker, ["container_name"])
        self.docker_port = config.config_integer(docker, ["port"])

        # packit
        packit_config = config.config_dict(dat, ["packit_servers"])
        self.packit_servers = {}
        for server, server_config in packit_config.items():
            self.packit_servers[server] = { "url": config.config_string(server_config, ["url"]) }

        # datasets
        self.datasets = GroutDatasetsConfig(config.config_dict(dat, ["datasets"]))
