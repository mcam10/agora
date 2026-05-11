const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AgentRegistry", function () {
  let registry;
  let owner, agent1, agent2;

  beforeEach(async function () {
    [owner, agent1, agent2] = await ethers.getSigners();
    const AgentRegistry = await ethers.getContractFactory("AgentRegistry");
    registry = await AgentRegistry.deploy();
  });

  describe("Registration", function () {
    it("should register an agent and return a code", async function () {
      const tx = await registry.connect(agent1).register("test-agent-v1");
      const receipt = await tx.wait();

      const code = await registry.ownerToCode(agent1.address);
      expect(code).to.not.equal(ethers.ZeroHash);

      const agent = await registry.getAgent(code);
      expect(agent.owner).to.equal(agent1.address);
      expect(agent.metadata).to.equal("test-agent-v1");
      expect(agent.active).to.be.true;
    });

    it("should reject duplicate registration", async function () {
      await registry.connect(agent1).register("first");
      await expect(
        registry.connect(agent1).register("second")
      ).to.be.revertedWithCustomError(registry, "AlreadyRegistered");
    });

    it("should increment agent count", async function () {
      await registry.connect(agent1).register("agent1");
      await registry.connect(agent2).register("agent2");
      expect(await registry.agentCount()).to.equal(2);
    });
  });

  describe("Deactivation", function () {
    it("should deactivate an agent", async function () {
      await registry.connect(agent1).register("agent");
      const code = await registry.ownerToCode(agent1.address);

      await registry.connect(agent1).deactivate();
      expect(await registry.isActive(code)).to.be.false;
    });
  });

  describe("Metadata", function () {
    it("should update metadata", async function () {
      await registry.connect(agent1).register("v1");
      await registry.connect(agent1).updateMetadata("v2");

      const code = await registry.ownerToCode(agent1.address);
      const agent = await registry.getAgent(code);
      expect(agent.metadata).to.equal("v2");
    });
  });
});
