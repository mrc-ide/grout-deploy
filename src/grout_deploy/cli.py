"""
Usage:
  grout start [--pull] [--refresh] [<configname>]
  grout stop [--delete]

Options:
  --pull            Pull docker images before starting
  --refresh         Refresh all data even if dataset/level is already downloaded (source location may have changed)
  --delete          Delete all data when pull down container
"""

import os
import pickle
import time

import docopt
import timeago

from grout_deploy.config import GroutConfig
from grout_deploy.datasets import GroutDatasets
from grout_deploy.docker import GroutDocker


def parse(argv=None):
    config_path = "config"
    config_name = None
    dat = docopt.docopt(__doc__, argv)
    if dat["start"]:
        action = "start"
        config_name = dat["<configname>"]
        args = {"pull_image": dat["--pull"], "refresh_data": dat["--refresh"]}
    elif dat["stop"]:
        action = "stop"
        args = {"delete_data": dat["--delete"]}

    return config_path, config_name, action, args


def path_last_deploy(config_path):
    return config_path + "/.last_deploy"


def read_config(config_path):
    with open(path_last_deploy(config_path), "rb") as f:
        return pickle.load(f)


def load_config(config_path, config_name=None):
    if os.path.exists(path_last_deploy(config_path)):
        dat = read_config(config_path)
        when = timeago.format(dat["time"])
        prev_config_name = dat["config_name"]
        cfg = GroutConfig(config_path, prev_config_name)
        print(
            f"[Loaded configuration matching previous deploy '{prev_config_name}' ({when})]"
        )
        return prev_config_name, cfg

    if config_name is None:
        msg = "Config name must be provided when there is no previous deploy config,"
        raise Exception(msg)
    cfg = GroutConfig(config_path, config_name)
    print(f"[Loaded configuration for first deploy '{config_name}']")
    return config_name, cfg


def save_config(config_path, config_name, cfg):
    dat = {"config_name": config_name, "time": time.time(), "data": cfg}
    with open(path_last_deploy(config_path), "wb") as f:
        pickle.dump(dat, f)


def start(data_path, cfg, refresh_all, pull_image):
    datasets = GroutDatasets(cfg, data_path)
    datasets.download(refresh_all)
    docker = GroutDocker(cfg, data_path)
    docker.start(pull_image)


def stop(data_path, cfg, delete_data):
    if delete_data:
        print("WARNING! THIS WILL DELETE ALL LOCAL DATASETS.")
        if input("Do you want to continue? [yes/no] ") != "yes":
            print("Not continuing")
            return
    docker = GroutDocker(cfg, data_path)
    docker.stop()
    if delete_data:
        datasets = GroutDatasets(cfg, data_path)
        datasets.delete_all()


def main(argv=None):
    config_path, config_name, action, args = parse(argv)
    config_name, cfg = load_config(config_path, config_name)
    data_path = "data"
    if action == "start":
        save_config(config_path, config_name, cfg)
        print(f"Saving config with name {config_name}")
        start(data_path, cfg, args["refresh_data"], args["pull_image"])
    elif action == "stop":
        stop(data_path, cfg, args["delete_data"])
