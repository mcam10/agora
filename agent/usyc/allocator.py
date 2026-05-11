import os
from dotenv import load_dotenv

from .circle_client import CircleWalletClient
from .swap import swap_usdc_to_usyc, swap_usyc_to_usdc

load_dotenv()

RISK_OFF_ALLOCATION_PCT = float(os.getenv("USYC_ALLOCATION_PCT", "0.80"))


def allocate(regime_result: dict, wallet_id: str) -> dict:
    client = CircleWalletClient()
    balances = client.get_balance(wallet_id)
    private_key = os.getenv("ARC_PRIVATE_KEY", "")

    usdc_balance = balances.get("USDC", 0.0)
    usyc_balance = balances.get("USYC", 0.0)

    if regime_result["regime"] == "risk-off":
        return _enter_risk_off(usdc_balance, private_key)
    else:
        return _exit_risk_off(usyc_balance, private_key)


def _enter_risk_off(usdc_balance: float, private_key: str) -> dict:
    amount_to_park = usdc_balance * RISK_OFF_ALLOCATION_PCT

    if amount_to_park < 1.0:
        return {"action": "hold", "reason": "insufficient USDC balance"}

    tx_hash = swap_usdc_to_usyc(amount_to_park, private_key)
    return {
        "action": "parked_in_usyc",
        "amount": amount_to_park,
        "tx_hash": tx_hash,
    }


def _exit_risk_off(usyc_balance: float, private_key: str) -> dict:
    if usyc_balance < 1.0:
        return {"action": "hold", "reason": "no USYC to unwind"}

    tx_hash = swap_usyc_to_usdc(usyc_balance, private_key)
    return {
        "action": "unwound_to_usdc",
        "amount": usyc_balance,
        "tx_hash": tx_hash,
    }
