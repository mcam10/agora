import os
import requests
from dotenv import load_dotenv

load_dotenv()

CIRCLE_BASE_URL = "https://api.circle.com/v1"


class CircleWalletClient:
    def __init__(self):
        self.api_key = os.getenv("CIRCLE_API_KEY")
        if not self.api_key:
            raise ValueError("CIRCLE_API_KEY not set in environment")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def create_wallet(self, idempotency_key: str) -> dict:
        resp = requests.post(
            f"{CIRCLE_BASE_URL}/w3s/developer/wallets",
            headers=self.headers,
            json={
                "idempotencyKey": idempotency_key,
                "blockchains": ["ARC-TESTNET"],
                "count": 1,
                "walletSetId": os.getenv("CIRCLE_WALLET_SET_ID", ""),
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()["data"]["wallets"][0]

    def get_balance(self, wallet_id: str) -> dict:
        resp = requests.get(
            f"{CIRCLE_BASE_URL}/w3s/wallets/{wallet_id}/balances",
            headers=self.headers,
            timeout=10,
        )
        resp.raise_for_status()
        balances = resp.json()["data"]["tokenBalances"]
        return {b["token"]["symbol"]: float(b["amount"]) for b in balances}

    def get_wallet_address(self, wallet_id: str) -> str:
        resp = requests.get(
            f"{CIRCLE_BASE_URL}/w3s/wallets/{wallet_id}",
            headers=self.headers,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()["data"]["wallet"]["address"]
