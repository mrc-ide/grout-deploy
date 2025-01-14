import os

from grout_deploy.config import GroutDatasetsConfig
from grout_deploy.packit import GroutPackit

class GroutDatasets:
    def __init__(self, path: str, datasets_config: GroutDatasetsConfig, packit: GroutPackit, refresh_all = False):
        self.path = path
        self.config = datasets_config
        self.packit = packit
        self.refresh_all = refresh_all

    def __download_file(self, dataset, level, full_file_name):
        print(f"Downloading {dataset} {level}")
        packit_server, packet_id, download_name = self.config.get_tile_level_details(dataset, level)
        self.packit.download_file(packit_server, packet_id, download_name)


    def download(self):
        for dataset_name in self.config.get_dataset_names():
            print("downloading {}".format(dataset_name))
            folder = os.path.join(self.path, dataset_name)
            if not os.path.exists(folder):
                os.makedirs(folder)
            for level in self.config.get_dataset_tile_levels(dataset_name):
                full_file_name = os.path.join(folder, "{}.mbtiles".format(level))
                # If not refreshing, do not download if file already exists locally
                if not self.refresh_all and os.path.exists(full_file_name):
                    print(f"{level} exists locally - skipping download")
                    continue
                self.__download_file(dataset_name, level, full_file_name)




