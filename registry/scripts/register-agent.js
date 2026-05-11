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

  const metadata = process.argv[2] || "agora-regime-agent-v1";

  console.log(`Registering agent with metadata: "${metadata}"`);
  const tx = await registry.register(metadata);
  const receipt = await tx.wait();

  const [signer] = await hre.ethers.getSigners();
  const code = await registry.ownerToCode(signer.address);

  console.log(`✓ Agent registered`);
  console.log(`  Code:    ${code}`);
  console.log(`  Owner:   ${signer.address}`);
  console.log(`  Tx Hash: ${receipt.hash}`);
  console.log(`  Block:   ${receipt.blockNumber}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
