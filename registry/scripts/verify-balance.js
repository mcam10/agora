const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  const balance = await hre.ethers.provider.getBalance(deployer.address);

  console.log(`  Address: ${deployer.address}`);
  console.log(`  Balance: ${hre.ethers.formatEther(balance)} ETH`);

  if (balance === 0n) {
    console.log("  ⚠ Balance is zero — request tokens from the faucet before deploying.");
    process.exitCode = 1;
  } else {
    console.log("  ✓ Wallet funded and ready to deploy.");
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
