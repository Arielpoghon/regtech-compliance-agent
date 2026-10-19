// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title CompliantRWA — example of a well-governed RWA token
contract CompliantRWA {
    address public admin;
    address public timelock;
    address public multisig;
    bool public paused;
    mapping(address => bool) public kycVerified;
    mapping(address => bool) public transferAllowed;

    // Governance: 2-of-3 multisig + 48h timelock on upgrades
    modifier onlyMultisig() { require(msg.sender == multisig, "not multisig"); _; }
    modifier onlyTimelock() { require(msg.sender == timelock, "not timelock"); _; }

    constructor(address _multisig, address _timelock) {
        admin = msg.sender;
        multisig = _multisig;
        timelock = _timelock;
    }

    // KYC-gated transfer
    function transfer(address to, uint256 amt) external {
        require(kycVerified[msg.sender] && kycVerified[to], "kyc required");
        require(transferAllowed[to], "not allowed");
        require(!paused, "paused");
        _transfer(msg.sender, to, amt);
    }

    function pause() external onlyMultisig { paused = true; }
    function unpause() external onlyMultisig { paused = false; }

    // Upgrade only via timelock
    function upgradeTo(address newImpl) external onlyTimelock { /* UUPS */ }

    // No minting without governance approval (handled off-chain via proposal)
    // No emergency rescue; no reentrancy-prone external calls
    // No oracle dependency for pricing

    function _transfer(address from, address to, uint256 amt) internal {}
}
EOF
echo written