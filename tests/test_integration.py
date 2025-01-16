import os
from constellation import docker_util
from src.grout_deploy.cli import main

def test_start_and_stop_grout():
    assert os.getenv("GITHUB_ACCESS_TOKEN") is not None, "GITHUB_ACCESS_TOKEN env var must be set to run integration test"
    main(["start", "grout", "--pull"])
    assert docker_util.container_exists("grout")
    main(["stop"])
    assert not docker_util.container_exists("grout")