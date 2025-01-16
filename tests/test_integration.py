import os
from src.grout_deploy.cli import main

def test_start_and_stop_grout():
    assert os.getenv("GITHUB_ACCESS_TOKEN") is not None, "GITHUB_ACCESS_TOKEN env var must be set to run integration test"
    main(["start", "grout"])
    main(["stop"])