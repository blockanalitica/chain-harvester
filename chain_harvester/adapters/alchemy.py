import requests

from chain_harvester.helpers import get_chain
from chain_harvester.utils.graphql import call_graphql


class Alchemy:
    def __init__(
        self,
        chain,
        network,
        subgraph_api_key=None,
        rpc=None,
        rpc_nodes=None,
        api_key=None,
        api_keys=None,
        abis_path=None,
        **kwargs,
    ):
        if rpc or rpc_nodes:
            self.chain = get_chain(
                chain,
                rpc=rpc,
                rpc_nodes=rpc_nodes,
                api_key=api_key,
                api_keys=api_keys,
                abis_path=abis_path,
                **kwargs,
            )
            self.rpc = rpc or rpc_nodes[chain][network]
        self.subgraph_api_key = subgraph_api_key

    def get_block_transactions(self, block_number):
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "alchemy_getTransactionReceipts",
            "params": [{"blockNumber": str(block_number)}],
        }
        headers = {"accept": "application/json", "content-type": "application/json"}
        response = requests.post(self.rpc, json=payload, headers=headers, timeout=10)
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

    def _get_blocks_query(self, to_block=None):
        base_query = """
            query ($first: Int!, $skip: Int!, $from_block: Int!{to_block_var}) {{
                blocks (orderBy: number, first: $first, skip: $skip, where:
                    {{number_gt: $from_block{to_block_filter}}}) {{
                    number
                    timestamp
                }}
            }}
        """

        to_block_var = ", $to_block: Int!" if to_block is not None else ""
        to_block_filter = ", number_lte: $to_block" if to_block is not None else ""

        query = base_query.format(to_block_var=to_block_var, to_block_filter=to_block_filter)
        return query

    def get_blocks(self, url, from_block, to_block=None, limit=10000):
        first = limit
        skip = 0
        while True:
            query = self._get_blocks_query(to_block)
            response = call_graphql(
                url,
                query,
                variables={
                    "first": first,
                    "skip": skip,
                    "from_block": from_block,
                    "to_block": to_block,
                },
            )
            if not response.get("data", {}).get("blocks"):
                break
            yield from response["data"]["blocks"]
            skip += first
