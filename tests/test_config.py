import re

import pytest

from src.grout_deploy.config import GroutConfig


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
        == "https://packit.dide.ic.ac.uk/reside/"
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
    server, packit_id, download = cfg.datasets.get_tile_level_details(
        "gadm41", "admin0"
    )
    assert server == "reside"
    assert download == "level0.mbtiles"
    assert re.match("^\\d{8}-\\d{6}-[\\da-f]{8}$", packit_id)
