import json

import requests

from chain_harvester.helpers import get_chain


class AlchemyChain:
    def __init__(
        self,
        chain,
        rpc=None,
        rpc_nodes=None,
        api_key=None,
        api_keys=None,
        abis_path=None,
        **kwargs,
    ):
        self.chain = get_chain(
            chain,
            rpc=rpc,
            rpc_nodes=rpc_nodes,
            api_key=api_key,
            api_keys=api_keys,
            abis_path=abis_path,
            **kwargs,
        )

    def get_batch_codes(self, addresses):
        data = []
        for address in addresses:
            payload = {
                "id": self.chain.chain_id,
                "jsonrpc": "2.0",
                "params": [address, "latest"],
                "method": "eth_getCode",
            }
            data.append(payload)
        headers = {"content-type": "application/json"}
        response = requests.post(self.chain.rpc, json=data, headers=headers, timeout=60)
        response.raise_for_status()
        return json.loads(response.text)

    def get_block_transactions(self, block_number):
        payload = {
            "id": self.chain.chain_id,
            "jsonrpc": "2.0",
            "method": "alchemy_getTransactionReceipts",
            "params": [{"blockNumber": str(block_number)}],
        }
        headers = {"accept": "application/json", "content-type": "application/json"}
        response = requests.post(self.chain.rpc, json=payload, headers=headers, timeout=10)
        return response.json()["result"]["receipts"]

    def get_transactions_for_contracts(
        self, contract_addresses, from_block, to_block=None, failed=False
    ):
        if not isinstance(contract_addresses, list):
            raise TypeError("contract_addresses must be a list")

        if not to_block:
            to_block = self.chain.get_latest_block()

        contract_addresses = [addr.lower() for addr in contract_addresses]

        for block in range(from_block, to_block + 1):
            data = self.get_block_transactions(block)
            for tx in data:
                if tx["to"] and tx["to"].lower() in contract_addresses:
                    if failed and tx["status"] == "0x1":
                        continue
                    transaction = self.chain.eth.get_transaction(tx["transactionHash"])
                    contract = self.chain.get_contract(tx["to"])
                    func_obj, func_params = contract.decode_function_input(transaction["input"])
                    yield {
                        "tx": tx,
                        "transaction": transaction,
                        "contract": tx["to"].lower(),
                        "function_abi": func_obj.__dict__,
                        "function_name": func_obj.fn_name,
                        "args": func_params,
                        "status": tx["status"],
                    }
