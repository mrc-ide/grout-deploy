import os
import shutil

from grout_deploy.config import GroutConfig
from grout_deploy.packit import GroutPackit


class GroutRegionMetadata:
    def __init__(self, config: GroutConfig, path: str):
        self.config = config.datasets
        self.path = path
        self.packit = GroutPackit(config)

    def __download_files(self, dataset, level, folder, refresh_all):
        print(f"Downloading {dataset} {level}")
        packit_server, packet_id, artefact_name = (
            self.config.get_region_metadata_level_details(dataset, level)
        )

        full_file_name = os.path.join(folder, f"{level}.mbtiles")
        file_exists = os.path.exists(full_file_name)
        if not refresh_all and file_exists:
            print(f"{level} exists locally - skipping download")
            continue
        if file_exists:
            print(f"Deleting previous data at {full_file_name}")
            os.remove(full_file_name)

        self.packit.download_file(
            packit_server, packet_id, download_name, full_file_name
        )

    def download(self, refresh_all):
        for dataset_name in self.config.get_dataset_names():
            if config.has_region_metadata(dataset_name):
            print(f"Downloading region metadata for dataset {dataset_name}")
            for level in self.config.get_dataset_region_metadata_levels(dataset_name):
                folder = os.path.join(self.path, dataset_name, level)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                # If not refreshing, do not download if file already exists
                self.__download_files(self, dataset, level, folder, refresh_all)

    def delete_all(self):
        print(f"Deleting region metadata folder {self.path}")
        shutil.rmtree(self.path)
