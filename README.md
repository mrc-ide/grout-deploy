# grout-deploy
Deployment tool for [grout](https://github.com/mrc-ide/grout).

The tool pulls grout data from [packit](https://github.com/mrc-ide/packit) API according to its configuration and 
runs the grout server in docker. 

A proxy is not included in the tool - the proxy must be configured separately. 

## Requirements

1. [Python3](https://www.python.org/downloads/) (>= 3.10)
2. [Hatch](https://hatch.pypa.io/latest/install/)

## Installation

This project is built with hatch. It is not published to PyPI, so must be run using hatch from local source.

Clone this repo, then: `hatch shell` before using the deploy tool as below. (You can exit the hatch shell with `exit`.)

## Usage

// TODO

## Deployment configuration

// TODO

## Dependencies

// TODO - constellation for config but not running docker, pyorderly for packit auth but not pulling files

## Testing
Run tests with `hatch test`. Generate coverage with `hatch test --cover`.

In order to run integration tests which need to non-interactively log in to packit, set `GITHUB_ACCESS_TOKEN`
environment variable to a PAT with access to `https://packit.dide.ic.ac.uk/reside/`.

## Linting
Run linting with automatic fixes with `hatch fmt`. To check linting only, with no file changes, use `hatch fmt --check`.