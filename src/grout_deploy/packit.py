import os

import requests
from pyorderly.outpack.location_packit import packit_authorisation

from grout_deploy.config import GroutConfig

PACKIT_API_ROUTE = "packit/api/"
SUCCESS_STATUS = 200
TIMEOUT = 10


class GroutPackit:
    def __init__(self, cfg: GroutConfig):
        self.cfg = cfg
        # on demand dictionary of access tokens for packit servers
        # - we only authenticate if and when we need to
        self.token_headers = {}

    def __get_server_url(self, packit_server: str):
        if packit_server not in self.cfg.packit_servers:
            msg = f"Unknown packit server: {packit_server}"
            raise Exception(msg)
        return self.cfg.packit_servers[packit_server]["url"]

    def __get_token_header(self, packit_server: str):
        # for a given packit server name, either return access token
        # already obtained, or authenticate with configured url and
        # save token before returning
        if packit_server not in self.token_headers:
            url = self.__get_server_url(packit_server)

            # optionally set a personal access token in env var
            # for running in CI without user interaction
            pat = os.getenv("GITHUB_ACCESS_TOKEN")

            token_header = packit_authorisation(url, pat)
            self.token_headers[packit_server] = token_header
        return self.token_headers[packit_server]

    def __get_from_packit(self, packit_server: str, relative_url: str):
        # do an authenticated packit GET request
        base = self.__get_server_url(packit_server)
        url = f"{base}{relative_url}"
        print(f"Getting from {url}")
        token_header = self.__get_token_header(packit_server)
        response = requests.get(url, headers=token_header, timeout=TIMEOUT)
        status_code = response.status_code
        if status_code != SUCCESS_STATUS:
            msg = f"Unsuccessful call to {url}\nStatus code: {status_code}"
            raise Exception(msg)
        return response

    def __get_download_hash(
        self, packit_server: str, packet_id: str, download_name: str
    ):
        # get packet metadata
        metadata = self.__get_from_packit(
            packit_server, f"{PACKIT_API_ROUTE}packets/metadata/{packet_id}"
        ).json()
        matched_files = list(
            filter(
                (lambda file: file["path"] == download_name), metadata["files"]
            )
        )
        if len(matched_files) == 0:
            msg = f"{download_name} not found in packet {packet_id}"
            raise Exception(msg)
        return matched_files[0]["hash"]

    def download_file(
        self,
        packit_server: str,
        packet_id: str,
        download_name: str,
        file_path: str,
    ):
        download_hash = self.__get_download_hash(
            packit_server, packet_id, download_name
        )
        download_response = self.__get_from_packit(
            packit_server,
            f"{PACKIT_API_ROUTE}/packets/file/{packet_id}?hash={download_hash}&filename={download_name}",
        )
        with open(file_path, "wb") as fd:
            for chunk in download_response.iter_content(chunk_size=128):
                fd.write(chunk)
        print(f"Downloaded data to {file_path}")
