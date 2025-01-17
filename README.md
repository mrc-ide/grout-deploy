# grout-deploy
Deployment tool for [grout](https://github.com/mrc-ide/grout).

The tool pulls grout data (tile databases) from [packit](https://github.com/mrc-ide/packit) API according to its 
configuration and runs the grout server in docker. Data is bind mounted into the server container.

A proxy is not included in the tool - the proxy must be configured separately. 

## Requirements

1. [Python3](https://www.python.org/downloads/) (>= 3.10)
2. [Hatch](https://hatch.pypa.io/latest/install/)

## Installation

This project is built with hatch. It is not published to PyPI, so must be run using hatch from local source.

Clone this repo, then: `hatch shell` before using the deploy tool as below. (You can exit the hatch shell with `exit`.)

## Usage

```
Usage:
  grout start [--pull] [--refresh] [<configname>]
  grout stop [--delete]

Options:
  --pull            Pull docker image before starting
  --refresh         Refresh all data even if dataset/level is already downloaded (source location may have changed)
  --delete          Delete all data locally when pull down container
```

Config files are in the `config` folder - there is currently only one configuration, called "grout", so you would
do a first-time start with `grout start --pull grout`.

Once a configuration is set during start, it will be reused by subsequent commands. The configuration usage information 
is stored in `config/.last_deploy`.

During deployment, you'll be prompted to authenticate with packit via github. 

After deployment, the server with be available on `http://localhost:5000`.

## Deployment configuration

The config file has these sections:

- `docker` - properties of the docker image, running container name and port to use for the grout server
- `packit_servers` - to avoid repeating packit server urls for every database location, this section defines 
packit server names and associates them with urls.
- `datasets` - defines a dictionary of datasets by name e.g. "gadm41", and within each dataset, admin levels for which 
tile databases are available e.g. "admin0". For each level, the packit server name, packit id and download file name
are configured. 

## Dependencies

The project uses [constellation](https://github.com/reside-ic/constellation) as a dependency, but only for the 
config utils it provides - we do not run the docker image as a constellation. 

[pyorderly](https://github.com/mrc-ide/pyorderly) is used to authenticate with packit, but not for pulling orderly
data - for individual files it's simpler to just access the packit endpoint with the access token received on
authentication. 

## Testing
Run tests with `hatch test`. Generate coverage with `hatch test --cover`.

In order to run integration tests which need to non-interactively authenticate with packit, set `GITHUB_ACCESS_TOKEN`
environment variable to a PAT with access to `https://packit.dide.ic.ac.uk/reside/`.

## Linting
Run linting with automatic fixes with `hatch fmt`. To check linting only, with no file changes, use `hatch fmt --check`.