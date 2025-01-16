import os
import shutil

from grout_deploy.config import GroutConfig
from grout_deploy.packit import GroutPackit


class GroutDatasets:
    def __init__(self, config: GroutConfig, path: str):
        self.config = config.datasets
        self.path = path
        self.packit = GroutPackit(config)

    def __download_file(self, dataset, level, full_file_name):
        print(f"Downloading {dataset} {level}")
        packit_server, packet_id, download_name = self.config.get_tile_level_details(dataset, level)
        self.packit.download_file(packit_server, packet_id, download_name, full_file_name)

    def download(self, refresh_all):
        for dataset_name in self.config.get_dataset_names():
            print(f"Downloading dataset {dataset_name}")
            folder = os.path.join(self.path, dataset_name)
            if not os.path.exists(folder):
                os.makedirs(folder)
            for level in self.config.get_dataset_tile_levels(dataset_name):
                full_file_name = os.path.join(folder, f"{level}.mbtiles")
                # If not refreshing, do not download if file already exists locally
                file_exists = os.path.exists(full_file_name)
                if not refresh_all and file_exists:
                    print(f"{level} exists locally - skipping download")
                    continue
                if file_exists:
                    print(f"Deleting previous data at {full_file_name}")
                    os.remove(full_file_name)
                self.__download_file(dataset_name, level, full_file_name)

    def delete_all(self):
        print(f"Deleting datasets folder {self.path}")
        shutil.rmtree(self.path)
