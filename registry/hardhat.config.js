require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../.env" });

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: { enabled: true, runs: 200 },
    },
  },
  networks: {
    "arc-testnet": {
      url: process.env.ARC_TESTNET_RPC_URL || "https://testnet-rpc.arc.network",
      chainId: parseInt(process.env.ARC_TESTNET_CHAIN_ID || "1270", 10),
      accounts: process.env.ARC_PRIVATE_KEY ? [process.env.ARC_PRIVATE_KEY] : [],
      gasPrice: "auto",
    },
  },
};
