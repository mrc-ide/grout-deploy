import os
import time
from contextlib import suppress

import requests
from constellation import docker_util

from src.grout_deploy.cli import main

base_url = "http://localhost:5000"
packit_base_url = "https://reside.packit.dide.ic.ac.uk"


def login_to_packit():
    # We need to provide a packit token to pyrorderly so that
    # interactive device login is not initiated during tests.
    # To do that we need to obtain one from packit, using
    # GITHUB_ACCESS_TOKEN then set a PACKIT_TOKEN env var
    # for grout deploy to pick up and pass to pyorderly
    gh_token = os.getenv("GITHUB_ACCESS_TOKEN")
    assert gh_token is not None, (
        "GITHUB_ACCESS_TOKEN env var must be set to run integration test"
    )
    auth_body = {"token": gh_token}
    auth_url = f"{packit_base_url}/api/auth/login/api"
    auth_response = requests.post(auth_url, json=auth_body)
    assert auth_response.status_code == 200
    packit_token = auth_response.json()["token"]
    assert len(packit_token) > 0
    os.environ["PACKIT_TOKEN"] = packit_token


def wait_for_web_app(poll_interval=0.2, timeout=5):
    for _ in range(round(timeout / poll_interval)):
        status_code = None
        with suppress(requests.exceptions.ConnectionError):
            status_code = requests.get(base_url).status_code
        if status_code == 200:
            return
        time.sleep(poll_interval)
    msg = f"Web app not available within max timeout of {max}s"
    raise Exception(msg)


def get_response(url):
    response = requests.get(f"{base_url}{url}")
    assert response.status_code == 200
    return response.json()


def test_start_and_stop_grout():
    login_to_packit()

    main(["start", "grout", "--pull"])
    assert docker_util.container_exists("grout")

    # check can access metadata endpoint
    wait_for_web_app()
    json = get_response("/metadata")
    assert json["data"]["datasets"]["tile"]["gadm41"]["levels"] == [
        "admin0",
        "admin1",
        "admin2",
    ]

    assert json["data"]["datasets"]["regionMetadata"]["gadm41"]["levels"] == [
        "admin0",
        "admin1",
        "admin2",
    ]

    # check global admin0 region_metadata response
    json = get_response("/region-metadata/gadm41/admin0")
    first_country = json["data"][0]
    assert first_country["id"] == "ABW"
    assert first_country["name"] == "Aruba"

    # check a country admin1 region_metadata response
    json = get_response("/region-metadata/gadm41/admin1/FRA")
    first_region = json["data"][0]
    assert first_region["id"] == "FRA.1_1"
    assert first_region["name"] == "Auvergne-Rhône-Alpes"

    # check expected tile databases exist
    assert os.path.exists("data/tile/gadm41/admin0.mbtiles")
    assert os.path.exists("data/tile/gadm41/admin1.mbtiles")
    assert os.path.exists("data/tile/gadm41/admin2.mbtiles")

    main(["stop"])
    assert not docker_util.container_exists("grout")
