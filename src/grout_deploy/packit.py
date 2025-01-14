import requests

from pyorderly.outpack.location_packit import packit_authorisation
from grout_deploy.config import GroutConfig

# get token header for packit server - use pyorderly packit_authorization
# hit download endpoint to get a particular download for a packit, and save to given path
class GroutPackit:
    def __init__(self, cfg: GroutConfig):
        self.cfg = cfg
        # on demand dictionary of access tokens for packit servers
        # - we only authenticate if and when we need to
        self.token_headers = {}

    def __get_server_url(self, packit_server: str):
        if packit_server not in self.cfg.packit_servers:
            raise Exception(f"Unknown packit server: {packit_server}")
        return self.cfg.packit_servers[packit_server]["url"]

    def __get_token_header(self, packit_server: str):
        # for a given packit server name, either return access token
        # already obtained, or authenticate with configured url and
        # save token before returning
        if packit_server not in self.token_headers:
            url = self.__get_server_url(packit_server)
            token_header = packit_authorisation(url, None)
            self.token_headers[packit_server] = token_header
        return self.token_headers[packit_server]

    def __get_from_packit(self, packit_server: str, relative_url: str):
        # do an authenticated packit GET request
        base = self.__get_server_url(packit_server)
        url = f"{base}{relative_url}"
        print(f"Getting from {url}")
        token_header = self.__get_token_header(packit_server)
        response = requests.get(url, headers=token_header)
        return response.json()

    def __get_download_hash(self, packit_server: str, packet_id: str, download_name: str):
        # get packet metadata
        metadata = self.__get_from_packit(packit_server, f"packit/api/packets/metadata/{packet_id}")
        matched_files = list(filter((lambda file: file["path"] == download_name), metadata["files"]))
        if len(matched_files) == 0:
            raise Exception(f"{download_name} not found in packet {packet_id}")
        return matched_files[0]["hash"]

    def download_file(self, packit_server: str, packet_id: str, download_name: str):
        hash = self.__get_download_hash(packit_server, packet_id, download_name)
        print(hash)
