import json
import time
from dataclasses import dataclass, asdict
from web3 import Web3


@dataclass
class AttributedDecision:
    agent_code: str
    action: str
    venue: str
    params: dict
    timestamp: int
    signature: str = ""


def create_decision(agent_code: str, action: str, venue: str, params: dict) -> AttributedDecision:
    return AttributedDecision(
        agent_code=agent_code,
        action=action,
        venue=venue,
        params=params,
        timestamp=int(time.time()),
    )


def sign_decision(decision: AttributedDecision, private_key: str) -> AttributedDecision:
    message = json.dumps(asdict(decision), sort_keys=True, separators=(",", ":"))
    w3 = Web3()
    account = w3.eth.account.from_key(private_key)
    signed = account.sign_message(
        encode_defunct(text=message)
    )
    decision.signature = signed.signature.hex()
    return decision


def encode_defunct(text: str):
    from eth_account.messages import encode_defunct as _encode
    return _encode(text=text)


def to_builder_code_payload(decision: AttributedDecision) -> dict:
    return {
        "builder_code": decision.agent_code,
        "action": decision.action,
        "venue": decision.venue,
        "params": decision.params,
        "timestamp": decision.timestamp,
        "sig": decision.signature,
    }
