# Agora — On-Chain Agent Identity & Regime-Aware Portfolio Manager

> Built for the [Agora Agents Hackathon](https://agora.thecanteenapp.com) · Canteen × Circle × Arc · May 2026

---

## What This Is

AI agents are becoming economic actors — but they have no persistent identity. Every trade they make is anonymous. No attribution, no reputation, no revenue.

This project solves that. It's two things working together:

1. **An on-chain agent identity registry on Arc** — any AI agent can register and receive a `bytes32` identity code that travels with every trade it makes, across venues.
2. **A regime-detecting portfolio manager** — reads FRED macro data (including the 10-year Treasury yield), classifies the market as risk-on or risk-off, and allocates accordingly — parking idle capital in USYC during risk-off periods.

When the portfolio agent trades, its decisions are attributed on-chain via the identity registry. Its structured outputs are exposed as a signed feed compatible with Polymarket V2 builder codes — meaning the agent earns USDC fees on every attributed fill.

**Arc is the settlement layer.** Sub-second finality, ~$0.01 USDC fees. The registry, the attribution, and the capital movement all run on Arc.

---

## Architecture

```
┌─────────────────────────────────────────────┐
│              Agent Layer (Python)            │
│  - Regime Detection (FRED / DGS10)          │
│  - Opportunity Scanner (151 strategies)     │
│  - Structured JSON decision outputs         │
└────────────────┬────────────────────────────┘
                 │ signs decisions
┌────────────────▼────────────────────────────┐
│         Identity Layer (Arc / Solidity)      │
│  - Agent Registry Contract                  │
│  - bytes32 agent code issuance              │
│  - Attribution travels with every trade     │
│  - Public leaderboard of agent performance  │
└────────────────┬────────────────────────────┘
                 │ settles on
┌────────────────▼────────────────────────────┐
│              Venue Layer                     │
│  - Arc (primary settlement)                 │
│  - Polymarket V2 (builder code compatible)  │
│  - USYC (risk-off capital parking)          │
│  - Gateway (cross-chain USDC movement)      │
└─────────────────────────────────────────────┘
```

---

## The Problem

Three independent venues — Polymarket V2, Hyperliquid HIP-3, and Pump.fun — each independently invented a `bytes32` attribution primitive in the last six months. There is still no canonical registry that ties them together.

An AI agent operating across all three needs three different attribution mechanisms in three different signing flows. A chain-agnostic registry on Arc closes this gap. One identity, bridgeable to every venue.

---

## Open Source Components

| Module | Status | Description |
|---|---|---|
| `registry/` | 🟢 Public | Arc Solidity contract — agent registration, bytes32 code issuance |
| `agent/regime_detection/` | 🟢 Public | FRED macro data pull, DGS10 signal, risk-on/risk-off classifier |
| `agent/builder_wrapper/` | 🟢 Public | Polymarket V2 builder code compatibility layer |
| `leaderboard/` | 🟢 Public | On-chain agent performance leaderboard UI |
| `agent/strategies/` | 🔴 Private | 151 strategy opportunity scanner — not open sourced |
| `agent/dca/` | 🔴 Private | Personal DCA execution parameters |

---

## Stack

- **Smart Contracts** — Solidity, deployed on Arc testnet
- **Agent Framework** — Python, structured JSON outputs
- **Chain Interaction** — web3.py / ethers.py
- **Circle Tools** — USDC, USYC, Gateway, Paymaster, App Kit
- **Data** — FRED API (macro), Plaid (cash flow, private)
- **Infrastructure** — AWS Lambda, Terraform

---

## Regime Detection — How It Works

The agent reads three primary macro signals from FRED:

| Signal | Ticker | Role |
|---|---|---|
| 10-Year Treasury Yield | DGS10 | Primary risk regime indicator |
| Yield Curve (10Y-2Y) | T10Y2Y | Recession signal |
| Federal Funds Rate | FEDFUNDS | Rate environment context |

**Risk-off conditions** (any of the following):
- DGS10 rising > 50bps over 30 days
- Yield curve inverted (T10Y2Y < 0)
- High volatility regime detected

When risk-off: capital allocation shifts to USYC (tokenized money market fund via Circle).
When risk-on: opportunity scanner activates across 151 strategies.

---

## Getting Started

```bash
git clone https://github.com/mcam10/agora
cd agora
pip install -r requirements.txt
cp .env.example .env
# Add your FRED API key and Arc testnet config
python -m agent.regime_detection.run
```

### Arc Testnet Setup
```bash
cd registry
npm install
npx hardhat compile
npx hardhat test
npx hardhat run scripts/deploy.js --network arc-testnet
```

---

## Roadmap

**Week 1 (May 11–17)**
- [x] Arc testnet environment
- [x] Registry contract (compiled, tested)
- [x] Regime detection module (FRED client, classifier, portfolio volatility)
- [x] USYC integration (allocator, Circle client, swap logic)
- [x] Builder wrapper (decision signing, builder code payload)

**Week 2 (May 18–25)**
- [x] Deploy registry to Arc testnet
- [x] Wire end-to-end: regime → on-chain signal write (Arc testnet)
- [ ] Leaderboard UI
- [ ] Cross-venue attribution demo
- [ ] Submission

---

## Deployed Contracts (Arc Testnet)

| Contract | Address |
|---|---|
| AgentRegistry (v2) | `0x7B0A2E609E38D70E43729CfEcBD2030604f88da0` |

- **Deployer:** `0xDE7Bd3B4a29C621870ca38C24183771E5dd2992F`
- **Deploy tx:** `0x09f163c94d68bde63e03e576d8999e50cb5009a486c4dd32c4d544e917d022b5`
- **Agent code:** `0x41147067c38cad0a521cf4d091d3ef46b2988e27c4bb73ae2507c254c1525407`
- **Registration tx:** `0x8e82cf6a0c85fb6ab209170b68db2eee2d1d37d8a24e796aa75805e868bde5f5`
- **First signal tx:** `0x3ad718955b0edccf2cd667d34018a7f2f760585503e8b7015bd7c408f807ae4a`
- **Block:** `43904784`

---

## About

Built by **Bingi** ([@mcam10](https://github.com/mcam10)) for the Agora Agents Hackathon.

Background: AI/ML systems, DevOps infrastructure (AWS/EKS), quant finance agent systems (regime detection, opportunity scanning, DCA execution).

LA-based. Building at [BingiTech](https://bingitech.io).

---

*Part of the [Agora Agents Hackathon](https://agora.thecanteenapp.com) · Canteen × Circle × Arc · May 2026*
