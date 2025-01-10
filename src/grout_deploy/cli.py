"""
Usage:
  grout start [--pull] [--refresh] [<configname>]
  grout stop [--delete] [--network]

Options:
  --pull            Pull docker images before starting
  --refresh         Refresh all data even if dataset/level is already downloaded (source location may have changed)
  --delete          Delete all data when pull down containers
  --network         Remove network
"""
import docopt
import os
import pickle
import time
import timeago

from grout_deploy.config import GroutConfig

def parse(argv=None):
    path = "config"
    config_name = None
    dat = docopt.docopt(__doc__, argv)
    if dat["start"]:
        action = "start"
        config_name = dat["<configname>"]
        args = {"pull_images": dat["--pull"], "refresh_data": dat["--refresh"]}
    elif dat["stop"]:
        action = "stop"
        args = {"delete_data": dat["--delete"], "remove_network": dat["--network"]}

    return path, config_name, action, args


def path_last_deploy(path):
    return path + "/.last_deploy"


def read_config(path):
    with open(path_last_deploy(path), "rb") as f:
        return pickle.load(f)


def load_config(path, config_name=None):
    if os.path.exists(path_last_deploy(path)):
        dat = read_config(path)
        when = timeago.format(dat["time"])
        prev_config_name = dat["config_name"]
        cfg = GroutConfig(path, prev_config_name)
        print("[Loaded configuration matching previous deploy '{}' ({})]".format(prev_config_name, when))
    else:
        if config_name is None:
            msg = "Config name must be provided when there is no previous deploy config,"
            raise Exception(msg)
        cfg = GroutConfig(path, config_name)
        print("[Loaded configuration for first deploy '{}']".format(config_name))
    return config_name, cfg


def save_config(path, config_name, cfg):
    dat = {"config_name": config_name, "time": time.time(), "data": cfg}
    with open(path_last_deploy(path), "wb") as f:
        pickle.dump(dat, f)


def main(argv=None):
    path, config_name, action, args = parse(argv)
    config_name, cfg = load_config(path, config_name)
    if action == "start":
        save_config(path, config_name, cfg)