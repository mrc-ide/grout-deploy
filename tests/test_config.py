import re

import pytest

from src.grout_deploy.config import GroutConfig

packet_id_regex = "^\\d{8}-\\d{6}-[\\da-f]{8}$"

@pytest.fixture
def cfg():
    return GroutConfig("config", "grout")


def test_docker(cfg):
    assert cfg.docker_image_repo == "ghcr.io/mrc-ide"
    assert cfg.docker_image_name == "grout"
    assert cfg.docker_image_tag == "main"
    assert cfg.docker_container_name == "grout"
    assert cfg.docker_port == 5000


def test_packit(cfg):
    assert len(cfg.packit_servers.keys()) == 1
    assert (
        cfg.packit_servers["reside"]["url"]
        == "https://reside.packit.dide.ic.ac.uk/"
    )


def test_get_dataset_names(cfg):
    assert cfg.datasets.get_dataset_names() == ["gadm41", "arbomap"]


def test_get_dataset_tile_levels(cfg):
    assert cfg.datasets.get_dataset_tile_levels("gadm41") == [
        "admin0",
        "admin1",
        "admin2",
    ]
    assert cfg.datasets.get_dataset_tile_levels("arbomap") == [
        "admin0",
        "admin1",
        "admin2",
    ]


def test_get_tile_level_details(cfg):
    server, packet_id, download = cfg.datasets.get_tile_level_details(
        "gadm41", "admin0"
    )
    assert server == "reside"
    assert download == "level0.mbtiles"
    assert re.match(packet_id_regex, packet_id)


def test_has_region_metadata(cfg):
    assert cfg.datasets.has_region_metadata("gadm41")
    assert cfg.datasets.has_region_metadata("arbomap") == False


def test_get_dataset_region_metadata_levels(cfg):
    assert cfg.datasets.get_dataset_region_metadata_levels("gadm41") == ["admin0", "admin1", "admin2"]


def test_get_region_metadata_level_details(cfg):
    server, packet_id, artefact_name = cfg.datasets.get_region_metadata_level_details("gadm41", "admin1")
    assert server == "reside"
    assert re.match(packet_id_regex, packet_id)
    assert artefact_name == "Level 1 region metadata"