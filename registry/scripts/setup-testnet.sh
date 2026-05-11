#!/usr/bin/env bash
set -euo pipefail

echo "=== Agora — Arc Testnet Setup ==="
echo ""

# 1. Check dependencies
if ! command -v npx &> /dev/null; then
  echo "ERROR: Node.js/npm not found. Install from https://nodejs.org"
  exit 1
fi

# 2. Install project dependencies
echo "[1/4] Installing dependencies..."
cd "$(dirname "$0")/.."
npm install

# 3. Generate wallet if needed
if [ -z "${ARC_PRIVATE_KEY:-}" ]; then
  echo ""
  echo "[2/4] No ARC_PRIVATE_KEY found in environment."
  echo "  Generate a new wallet:"
  echo "    node -e \"const w = require('ethers').Wallet.createRandom(); console.log('Address:', w.address); console.log('Private Key:', w.privateKey);\""
  echo ""
  echo "  Then add to your .env file:"
  echo "    ARC_PRIVATE_KEY=0x..."
  echo ""
else
  echo "[2/4] Wallet configured ✓"
  WALLET_ADDRESS=$(node -e "const {Wallet} = require('ethers'); console.log(new Wallet(process.env.ARC_PRIVATE_KEY).address)")
  echo "  Address: $WALLET_ADDRESS"
fi

# 4. Request testnet tokens
echo "[3/4] Request testnet tokens:"
echo "  Visit: ${ARC_FAUCET_URL:-https://faucet.arc.network}"
echo "  Paste your wallet address and request tokens."
echo ""

# 5. Verify balance
if [ -n "${ARC_PRIVATE_KEY:-}" ]; then
  echo "[4/4] Checking balance..."
  npx hardhat run scripts/verify-balance.js --network arc-testnet 2>/dev/null || echo "  (Deploy network not reachable — verify manually after funding)"
else
  echo "[4/4] Skipped balance check (no wallet configured)"
fi

echo ""
echo "=== Setup complete. Next: npx hardhat run scripts/deploy.js --network arc-testnet ==="
