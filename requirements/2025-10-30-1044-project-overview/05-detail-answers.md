# Expert Requirements Answers

## Q1: Should we build the Docker image with the Wan2.2-Animate model included, or download it at runtime?
**Answer:** Yes - Include model in Docker image (Option A)
**Rationale:** Faster GPU spin-up (45 seconds vs 10+ minutes), predictable costs, no bandwidth waste on repeated downloads.

## Q2: Should the Flask processing endpoint support batch processing (multiple videos per GPU instance), or process one video at a time?
**Answer:** One video at a time for V1 MVP
**Rationale:** Simpler implementation, easier debugging, faster to market. Batch optimization can be added in V2.

## Q3: Should we create a local development environment with a lightweight face-swap model for testing, or require full GPU access from day one?
**Answer:** No local dev - use GPU directly from day one
**Rationale:** User wants minimal complexity and interaction with code. One environment, one model, just works. Worth the extra GPU credits to avoid local setup headaches.

## Q4: Should the system automatically retry failed face-swaps (e.g., if face detection fails), or immediately mark as Failed and require manual intervention?
**Answer:** No automatic retries - mark as Failed immediately with red flag 🚩
**Rationale:** Face detection failures indicate bad input (avatar/video quality). Retries waste GPU credits. User fixes and resubmits manually. Red flag emoji in Status field for easy visual scanning.

## Q5: Should we implement the Airtable MCP integration for easier development/testing, or use direct Airtable API calls via Make.com only?
**Answer:** YES - Airtable MCP for development, testing, and debugging. Make.com for production automation.
**Rationale:** MCP enables zero-code setup and testing from Claude Code. User can see real-time updates, debug issues, and test workflows without touching APIs. Production remains bulletproof with Make.com automation.
