import os
import time
from contextlib import suppress

import requests
from constellation import docker_util

from src.grout_deploy.cli import main

base_url = "http://localhost:5000"


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


def test_start_and_stop_grout():
    assert (
        os.getenv("GITHUB_ACCESS_TOKEN") is not None
    ), "GITHUB_ACCESS_TOKEN env var must be set to run integration test"
    main(["start", "grout", "--pull"])
    assert docker_util.container_exists("grout")

    # check can access metadata endpoint
    wait_for_web_app()
    response = requests.get(f"{base_url}/metadata")
    assert response.status_code == 200
    json = response.json()
    assert json["data"]["datasets"]["tile"]["gadm41"]["levels"] == [
        "admin0",
        "admin1",
        "admin2",
    ]

    # check expected tile databases exist
    assert os.path.exists("data/gadm41/admin0.mbtiles")
    assert os.path.exists("data/gadm41/admin1.mbtiles")
    assert os.path.exists("data/gadm41/admin2.mbtiles")

    main(["stop"])
    assert not docker_util.container_exists("grout")
