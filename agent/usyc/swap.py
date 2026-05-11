import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

USYC_CONTRACT_ADDRESS = os.getenv("USYC_CONTRACT_ADDRESS", "")
USDC_CONTRACT_ADDRESS = os.getenv("USDC_CONTRACT_ADDRESS", "")

ERC20_ABI = [
    {
        "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]

USYC_SWAP_ABI = [
    {
        "inputs": [{"name": "usdcAmount", "type": "uint256"}],
        "name": "deposit",
        "outputs": [{"name": "usycAmount", "type": "uint256"}],
        "type": "function",
    },
    {
        "inputs": [{"name": "usycAmount", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [{"name": "usdcAmount", "type": "uint256"}],
        "type": "function",
    },
]


def _get_web3() -> Web3:
    rpc_url = os.getenv("ARC_TESTNET_RPC_URL", "https://testnet-rpc.arc.network")
    return Web3(Web3.HTTPProvider(rpc_url))


def swap_usdc_to_usyc(amount_usdc: float, private_key: str) -> str:
    w3 = _get_web3()
    account = w3.eth.account.from_key(private_key)
    amount_wei = int(amount_usdc * 10**6)

    usdc = w3.eth.contract(address=USDC_CONTRACT_ADDRESS, abi=ERC20_ABI)
    approve_tx = usdc.functions.approve(USYC_CONTRACT_ADDRESS, amount_wei).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 100_000,
    })
    signed_approve = account.sign_transaction(approve_tx)
    w3.eth.send_raw_transaction(signed_approve.raw_transaction)

    usyc = w3.eth.contract(address=USYC_CONTRACT_ADDRESS, abi=USYC_SWAP_ABI)
    deposit_tx = usyc.functions.deposit(amount_wei).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 200_000,
    })
    signed_deposit = account.sign_transaction(deposit_tx)
    tx_hash = w3.eth.send_raw_transaction(signed_deposit.raw_transaction)

    return tx_hash.hex()


def swap_usyc_to_usdc(amount_usyc: float, private_key: str) -> str:
    w3 = _get_web3()
    account = w3.eth.account.from_key(private_key)
    amount_wei = int(amount_usyc * 10**6)

    usyc = w3.eth.contract(address=USYC_CONTRACT_ADDRESS, abi=USYC_SWAP_ABI)
    withdraw_tx = usyc.functions.withdraw(amount_wei).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 200_000,
    })
    signed_withdraw = account.sign_transaction(withdraw_tx)
    tx_hash = w3.eth.send_raw_transaction(signed_withdraw.raw_transaction)

    return tx_hash.hex()
