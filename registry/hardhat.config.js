require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: "../.env" });

module.exports = {
  solidity: "0.8.20",
  networks: {
    "arc-testnet": {
      url: process.env.ARC_TESTNET_RPC_URL || "https://testnet-rpc.arc.network",
      accounts: process.env.ARC_PRIVATE_KEY ? [process.env.ARC_PRIVATE_KEY] : [],
    },
  },
};
