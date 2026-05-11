// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract AgentRegistry {
    struct Agent {
        bytes32 code;
        address owner;
        string metadata;
        uint256 registeredAt;
        bool active;
    }

    mapping(bytes32 => Agent) public agents;
    mapping(address => bytes32) public ownerToCode;

    uint256 public agentCount;

    event AgentRegistered(bytes32 indexed code, address indexed owner, string metadata);
    event AgentDeactivated(bytes32 indexed code);
    event AgentMetadataUpdated(bytes32 indexed code, string newMetadata);

    error AlreadyRegistered();
    error NotOwner();
    error AgentNotFound();

    function register(string calldata metadata) external returns (bytes32 code) {
        if (ownerToCode[msg.sender] != bytes32(0)) revert AlreadyRegistered();

        code = keccak256(abi.encodePacked(msg.sender, block.timestamp, agentCount));

        agents[code] = Agent({
            code: code,
            owner: msg.sender,
            metadata: metadata,
            registeredAt: block.timestamp,
            active: true
        });

        ownerToCode[msg.sender] = code;
        agentCount++;

        emit AgentRegistered(code, msg.sender, metadata);
    }

    function deactivate() external {
        bytes32 code = ownerToCode[msg.sender];
        if (code == bytes32(0)) revert AgentNotFound();

        agents[code].active = false;
        emit AgentDeactivated(code);
    }

    function updateMetadata(string calldata newMetadata) external {
        bytes32 code = ownerToCode[msg.sender];
        if (code == bytes32(0)) revert AgentNotFound();

        agents[code].metadata = newMetadata;
        emit AgentMetadataUpdated(code, newMetadata);
    }

    function getAgent(bytes32 code) external view returns (Agent memory) {
        if (agents[code].owner == address(0)) revert AgentNotFound();
        return agents[code];
    }

    function isActive(bytes32 code) external view returns (bool) {
        return agents[code].active;
    }
}
