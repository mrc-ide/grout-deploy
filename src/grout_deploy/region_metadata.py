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

        packet_artefacts = self.packit.get_artefacts(packit_server, packet_id)
        artefact_paths = packet_artefacts[artefact_name]
        for artefact_path in artefact_paths:
            filename = artefact_path.rsplit('/')[-1]
            destination_path = os.path.join(folder, filename)
            file_exists = os.path.exists(destination_path)
            # If not refreshing, do not download if file already exists
            # TODO: DRY here
            if not refresh_all and file_exists:
                print(f"{level} exists locally - skipping download")
                continue
            if file_exists:
                print(f"Deleting previous data at {destination_path}")
                os.remove(destination_path)

            self.packit.download_file(
                packit_server, packet_id, filename, artefact_path, destination_path
            )
            # TODO: DRY to here

    def download(self, refresh_all):
        for dataset_name in self.config.get_dataset_names():
            if self.config.has_region_metadata(dataset_name):
                print(f"Downloading region metadata for dataset {dataset_name}")
                for level in self.config.get_dataset_region_metadata_levels(dataset_name):
                    folder = os.path.join(self.path, dataset_name, level)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                    self.__download_files(dataset_name, level, folder, refresh_all)

    def delete_all(self):
        print(f"Deleting region metadata folder {self.path}")
        shutil.rmtree(self.path)
