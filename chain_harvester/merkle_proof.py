from multiproof import StandardMerkleTree


def generate_merkle_proof(claims):
    values = [
        [claim["epoch"], claim["account"], claim["token"], claim["cumulativeAmount"]]
        for claim in claims
    ]

    leaf_encoding = ["uint256", "address", "address", "uint256"]

    tree = StandardMerkleTree.of(values, leaf_encoding)

    result = {
        "root": tree.root,
        "totalAmount": str(sum(int(claim["cumulativeAmount"]) for claim in claims)),
        "totalClaims": len(claims),
        "values": [],
    }

    for claim, value in zip(claims, values, strict=True):
        proof = tree.get_proof(value)
        result["values"].append(
            {
                **claim,
                "proof": list(proof),
            }
        )

    return result
