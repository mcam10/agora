import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

REGISTRY_ADDRESS = "0x7B0A2E609E38D70E43729CfEcBD2030604f88da0"

REGISTRY_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "metadata", "type": "string"}],
        "name": "register",
        "outputs": [{"internalType": "bytes32", "name": "code", "type": "bytes32"}],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "signal", "type": "string"}],
        "name": "writeRegimeSignal",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "ownerToCode",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function"
    }
]

ZERO_BYTES32 = b'\x00' * 32


def get_web3():
    rpc_url = os.environ["ARC_TESTNET_RPC_URL"]
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot connect to Arc testnet at {rpc_url}")
    return w3


def get_account(w3):
    private_key = os.environ["PRIVATE_KEY"]
    account = w3.eth.account.from_key(private_key)
    return account, private_key


def _send_tx(w3, account, private_key, tx):
    signed = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return receipt


def _ensure_registered(w3, account, private_key, registry):
    existing_code = registry.functions.ownerToCode(account.address).call()
    if existing_code != ZERO_BYTES32:
        return existing_code, None

    metadata = json.dumps({"agent": "malik-regime-agent-v1", "version": "1.0"})
    tx = registry.functions.register(metadata).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 300000,
        "gasPrice": w3.eth.gas_price,
    })
    receipt = _send_tx(w3, account, private_key, tx)

    agent_code = registry.functions.ownerToCode(account.address).call()
    return agent_code, receipt


def write_regime_on_chain(regime_result: dict) -> dict:
    w3 = get_web3()
    account, private_key = get_account(w3)
    registry = w3.eth.contract(address=REGISTRY_ADDRESS, abi=REGISTRY_ABI)

    agent_code, reg_receipt = _ensure_registered(w3, account, private_key, registry)

    signal_payload = json.dumps({
        "regime": regime_result["regime"],
        "dgs10": regime_result["dgs10_current"],
        "t10y2y": regime_result["t10y2y_current"],
        "vix": regime_result["vix_current"],
        "signals": regime_result["signals"],
    })

    nonce = w3.eth.get_transaction_count(account.address)
    tx = registry.functions.writeRegimeSignal(signal_payload).build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 200000,
        "gasPrice": w3.eth.gas_price,
    })
    receipt = _send_tx(w3, account, private_key, tx)

    return {
        "registered": reg_receipt is not None,
        "reg_tx": reg_receipt["transactionHash"].hex() if reg_receipt else "already registered",
        "signal_tx": receipt["transactionHash"].hex(),
        "agent_code": "0x" + agent_code.hex(),
        "block": receipt["blockNumber"],
        "status": "success" if receipt["status"] == 1 else "failed",
    }
