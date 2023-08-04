from chain_harvester.chain import Chain


def test_chain():
    chain = Chain(rpc="http://localhost:8545")
    assert chain.rpc == "http://localhost:8545"
    assert chain.step == 10_000
