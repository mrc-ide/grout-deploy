import os

import requests
from pyorderly.outpack.location_packit import packit_authorisation

from grout_deploy.config import GroutConfig

PACKIT_API_ROUTE = "api/"
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

    def __packit_url(self, packit_server: str, relative_url: str):
        base = self.__get_server_url(packit_server)
        return f"{base}{relative_url}"

    def __check_status(self, response: requests.Response, url: str):
        status_code = response.status_code
        if status_code != SUCCESS_STATUS:
            msg = f"Unsuccessful call to {url}\nStatus code: {status_code}"
            raise Exception(msg)

    def __get_from_packit(self, packit_server: str, relative_url: str):
        # do an authenticated packit GET request
        url = self.__packit_url(packit_server, relative_url)
        token_header = self.__get_token_header(packit_server)
        response = requests.get(url, headers=token_header, timeout=TIMEOUT)
        self.__check_status(response, url)
        return response

    def __get_one_time_token(self, packit_server: str, packet_id: str, path: str):
        url = self.__packit_url(packit_server, f"{PACKIT_API_ROUTE}packets/{packet_id}/files/token")
        token_header = self.__get_token_header(packit_server)
        response = requests.post(url, json = {"paths": [path]}, headers=token_header)
        self.__check_status(response, url)
        return response.json()["id"]

    def get_artefacts(
        self,
        packit_server: str,
        packit_id: str
    ):
        # get artefact metadata for a packet
        packet_summary_response = self.__get_from_packit(
            packit_server,
            f"{PACKIT_API_ROUTE}packets/{packit_id}"
        )
        json = packet_summary_response.json()
        artefacts = json["custom"]["orderly"]["artefacts"]
        return {artefact["description"]: artefact["paths"] for artefact in artefacts}

    def download_file(
        self,
        packit_server: str,
        packet_id: str,
        filename: str,
        path: str,
        destination_path: str,
    ):
        # POST to get one time token
        ott = self.__get_one_time_token(packit_server, packet_id, path)

        download_response = self.__get_from_packit(
            packit_server,
            f"{PACKIT_API_ROUTE}packets/{packet_id}/file?path={path}&filename={filename}&token={ott}&inline=false",
        )
        with open(destination_path, "wb") as fd:
            for chunk in download_response.iter_content(chunk_size=128):
                fd.write(chunk)
        print(f"Downloaded data to {destination_path}")
