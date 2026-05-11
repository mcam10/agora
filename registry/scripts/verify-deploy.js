const hre = require("hardhat");

async function main() {
  const registryAddress = process.env.REGISTRY_ADDRESS;
  if (!registryAddress) {
    console.error("ERROR: Set REGISTRY_ADDRESS in .env (from deploy output)");
    process.exitCode = 1;
    return;
  }

  const AgentRegistry = await hre.ethers.getContractFactory("AgentRegistry");
  const registry = AgentRegistry.attach(registryAddress);

  const count = await registry.agentCount();
  console.log(`✓ AgentRegistry live at ${registryAddress}`);
  console.log(`  Agent count: ${count}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
