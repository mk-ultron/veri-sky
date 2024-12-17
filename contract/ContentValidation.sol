// SPDX-License-Identifier: MIT
pragma solidity ^0.8.2;

contract ContentValidation {
    struct Content {
        address creator;
        string contentHash;  // IPFS hash or other content identifier
        uint256 timestamp;
        bool isVerified;
        string platformSource;  // e.g., "twitter", "instagram"
        string contentType;    // e.g., "image", "video"
    }
    
    // Maps content hash to Content struct
    mapping(string => Content) public verifiedContent;
    
    // Trusted oracle addresses that can verify content
    mapping(address => bool) public trustedOracles;
    
    event ContentRegistered(string contentHash, address creator);
    event ContentVerified(string contentHash, address oracle);
    
    constructor() {
        trustedOracles[msg.sender] = true;
    }
    
    modifier onlyTrustedOracle() {
        require(trustedOracles[msg.sender], "Not authorized oracle");
        _;
    }
    
    // Register new content (called by content creator)
    function registerContent(
        string memory contentHash,
        string memory platformSource,
        string memory contentType
    ) public {
        require(verifiedContent[contentHash].creator == address(0), "Content already registered");
        
        verifiedContent[contentHash] = Content({
            creator: msg.sender,
            contentHash: contentHash,
            timestamp: block.timestamp,
            isVerified: false,
            platformSource: platformSource,
            contentType: contentType
        });
        
        emit ContentRegistered(contentHash, msg.sender);
    }
    
    // Verify content (called by oracle)
    function verifyContent(string memory contentHash) public onlyTrustedOracle {
        require(verifiedContent[contentHash].creator != address(0), "Content not registered");
        
        verifiedContent[contentHash].isVerified = true;
        
        emit ContentVerified(contentHash, msg.sender);
    }
    
    // Check content verification status
    function isContentVerified(string memory contentHash) public view returns (bool) {
        return verifiedContent[contentHash].isVerified;
    }
    
    // Get content details
    function getContentDetails(string memory contentHash) public view returns (Content memory) {
        return verifiedContent[contentHash];
    }
}