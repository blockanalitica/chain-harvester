import json

from aiobotocore.session import get_session


def _compute_key(config, contract_address):
    return (
        f"{config['dir']}/{config['chain']}/{config['network']}/"
        f"{contract_address.lower()}.json"
    )


async def fetch_abi_from_s3(config, contract_address):
    key = _compute_key(config, contract_address)
    session = get_session()
    async with session.create_client("s3", region_name=config["region"]) as client:
        response = await client.get_object(Bucket=config["bucket_name"], Key=key)
        async with response["Body"] as stream:
            data = await stream.read()
            content = data.decode()

    return json.loads(content)


async def save_abi_to_s3(config, contract_address, abi):
    key = _compute_key(config, contract_address)
    body = json.dumps(abi)

    session = get_session()
    async with session.create_client("s3", region_name=config["region"]) as client:
        await client.put_object(
            Bucket=config["bucket_name"],
            Key=key,
            Body=body,
            ContentType="application/json",
        )
