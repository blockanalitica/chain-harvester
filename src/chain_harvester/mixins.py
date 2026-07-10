import json
import logging
import urllib.parse

import requests
from environs import env

from chain_harvester.exceptions import ChainException
from chain_harvester.http import retry_get_json

log = logging.getLogger(__name__)


class EtherscanMixin:
    def __init__(
        self,
        etherscan_api_key=None,
        *args,
        **kwargs,
    ):
        self.etherscan_api_key = etherscan_api_key or env("ETHERSCAN_API_KEY", None)
        self.etherscan_url = "https://api.etherscan.io/v2"
        super().__init__(*args, **kwargs)

    def get_abi_from_source(self, contract_address):
        query_params = {
            "chainid": self.chain_id,
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
            "apikey": self.etherscan_api_key,
        }
        url = f"{self.etherscan_url}/api?{urllib.parse.urlencode(query_params)}"

        try:
            data = retry_get_json(url, timeout=5)
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when getting abi from etherscan",
                extra={"contract_address": contract_address},
            )
            raise

        if data["status"] != "1":
            raise ChainException("Request to etherscan failed: {}".format(data["result"]))

        abi = json.loads(data["result"])
        return abi

    def get_block_for_timestamp_fallback(self, timestamp):
        query_params = {
            "chainid": self.chain_id,
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
            "apikey": self.etherscan_api_key,
        }
        url = f"{self.etherscan_url}/api?{urllib.parse.urlencode(query_params)}"
        data = retry_get_json(url)
        result = int(data["result"])
        return result


class BlockscoutMixin:
    def __init__(
        self,
        blockscout_url,
        *args,
        **kwargs,
    ):
        self.blockscout_url = blockscout_url
        super().__init__(*args, **kwargs)

    def get_abi_from_source(self, contract_address):
        url = f"{self.blockscout_url}/api/v2/smart-contracts/{contract_address}"
        try:
            data = retry_get_json(url, timeout=5)
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from Blockscout",
                extra={"contract_address": contract_address},
            )
            raise

        return data["abi"]

    def get_block_for_timestamp_fallback(self, timestamp):
        query_params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
        }
        url = f"{self.blockscout_url}/api?{urllib.parse.urlencode(query_params)}"
        data = retry_get_json(url)
        result = int(data["result"]["blockNumber"])
        return result


class RoutescanMixin:
    def _get_url(self):
        return f"https://api.routescan.io/v2/network/mainnet/evm/{self.chain_id}/etherscan/api"

    def get_abi_from_source(self, contract_address):
        query_params = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address,
        }
        url = f"{self._get_url()}?{urllib.parse.urlencode(query_params)}"

        try:
            data = retry_get_json(url, timeout=5)
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when getting abi from routescan",
                extra={"contract_address": contract_address},
            )
            raise

        if data["status"] != "1":
            raise ChainException("Request to routescan failed: {}".format(data["result"]))

        abi = json.loads(data["result"])
        return abi

    def get_block_for_timestamp_fallback(self, timestamp):
        query_params = {
            "module": "block",
            "action": "getblocknobytime",
            "timestamp": timestamp,
            "closest": "before",
        }
        url = f"{self._get_url()}?{urllib.parse.urlencode(query_params)}"
        data = retry_get_json(url)
        result = int(data["result"])
        return result


class FilfoxMixin:
    def get_abi_from_source(self, contract_address):
        log.error("ABI for %s was fetched from filfox. Add it to abis folder!", contract_address)

        try:
            data = retry_get_json(
                f"https://filfox.info/api/v1/address/{contract_address}/contract", timeout=5
            )
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from filfox", extra={"contract_address": contract_address}
            )
            raise

        abi = json.loads(data["abi"])
        return abi

    def get_block_for_timestamp_fallback(self, timestamp):
        """
        Filfox API does not support fetching blocks by timestamp.
        Implemented to satisfy mixin interface.
        """
        raise NotImplementedError(
            "FilfoxMixin: fetching a block by timestamp is not supported by Filfox API"
        )


class TenderlyMixin:
    def __init__(
        self,
        account,
        project,
        testnet_id,
        api_key,
        *args,
        **kwargs,
    ):
        self.account = account
        self.project = project
        self.testnet_id = testnet_id
        self.api_key = api_key
        super().__init__(*args, **kwargs)

    def get_abi_from_source(self, contract_address):
        log.error("ABI for %s was fetched from tenderly. Add it to abis folder!", contract_address)

        url = (
            "https://api.tenderly.co/api/v1/"
            f"account/{self.account}/project/{self.project}/testnet/{self.testnet_id}/"
            f"verified-contract/{contract_address}"
        )
        try:
            data = retry_get_json(
                url=url,
                timeout=5,
                headers={"X-Access-Key": self.api_key},
            )
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from tenderly", extra={"contract_address": contract_address}
            )
            raise

        abi = data["data"]["raw_abi"]
        return abi


class OKLinkMixin:
    def __init__(
        self,
        oklink_chain_short_name,
        oklink_api_key=None,
        *args,
        **kwargs,
    ):
        self.oklink_chain_short_name = oklink_chain_short_name
        self.oklink_api_key = oklink_api_key or env("OKLINK_API_KEY", None)
        self.oklink_url = "https://www.oklink.com/api/v5/explorer"
        super().__init__(*args, **kwargs)

    def get_abi_from_source(self, contract_address):
        query_params = {
            "chainShortName": self.oklink_chain_short_name,
            "contractAddress": contract_address,
        }
        query = urllib.parse.urlencode(query_params)
        url = f"{self.oklink_url}/contract/verify-contract-info?{query}"
        headers = {"Ok-Access-Key": self.oklink_api_key} if self.oklink_api_key else None

        try:
            data = retry_get_json(url, timeout=5, headers=headers)
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when getting abi from oklink",
                extra={"contract_address": contract_address},
            )
            raise

        if data["code"] != "0" or not data["data"]:
            raise ChainException("Request to oklink failed: {}".format(data["msg"]))

        abi = json.loads(data["data"][0]["contractAbi"])
        return abi

    def get_block_for_timestamp_fallback(self, timestamp):
        data = retry_get_json(f"https://coins.llama.fi/block/{self.chain}/{timestamp}")
        block_number = data["height"]
        block_ts = data["timestamp"]
        tries = 0

        while block_ts > timestamp:
            if tries > 5:
                log.error(
                    "Couldn't find closest block before %s. Using %s as closest alternative",
                    timestamp,
                    block_number,
                )
                break
            block_number -= 1
            block_ts = self.get_block_info(block_number).timestamp
            tries += 1

        return block_number


class TempoMixin:
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        self.api = "https://contracts.tempo.xyz/v2"
        super().__init__(*args, **kwargs)

    async def get_abi_from_source(self, contract_address):
        url = f"{self.api}/contract/{self.chain_id}/{contract_address}?fields=abi"

        try:
            data = retry_get_json(url, timeout=5)
        except requests.exceptions.Timeout:
            log.exception(
                "Timeout when get abi from tenderly", extra={"contract_address": contract_address}
            )
            raise

        if data.get("match") != "exact_match":
            raise ChainException(f"Request to {self.api} failed: {data['message']}")

        abi = data["abi"]
        return abi

    def get_block_for_timestamp_fallback(self, timestamp):
        """
        Tempo API does not support fetching blocks by timestamp.
        Implemented to satisfy mixin interface.
        """
        raise NotImplementedError(
            "TempoMixin: fetching a block by timestamp is not supported by Tempo API"
        )
