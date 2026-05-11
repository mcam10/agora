const hre = require("hardhat");

async function main() {
  const AgentRegistry = await hre.ethers.getContractFactory("AgentRegistry");
  const registry = await AgentRegistry.deploy();
  await registry.waitForDeployment();

  const address = await registry.getAddress();
  console.log(`AgentRegistry deployed to: ${address}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
