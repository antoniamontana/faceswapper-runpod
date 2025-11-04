# Expert Requirements Questions

Now that I understand the system architecture deeply, I need clarification on specific V1 MVP implementation decisions:

## Q1: Should we build the Docker image with the Wan2.2-Animate model included, or download it at runtime?
**Default if unknown:** Include model in Docker image (faster spin-up, more predictable costs, but larger image ~15GB)
**Reasoning:** Runtime download adds 5-10 minutes per GPU spin-up and bandwidth costs. Baked-in model = 45-second spin-up vs. 10+ minute spin-up.

## Q2: Should the Flask processing endpoint support batch processing (multiple videos per GPU instance), or process one video at a time?
**Default if unknown:** One video per instance for V1 MVP (simpler, easier debugging, matches SOP workflow)
**Reasoning:** MVP SOP mentions batch processing but as optimization. Single-video processing is safer for V1, can optimize to batch in V2.

## Q3: Should we create a local development environment with a lightweight face-swap model for testing, or require full GPU access from day one?
**Default if unknown:** Yes - local dev with lightweight model (InsightFace or similar, ~500MB instead of 15GB)
**Reasoning:** Developers can test segmentation, S3 uploads, webhooks without burning Runpod credits. GPU testing only for final validation.

## Q4: Should the system automatically retry failed face-swaps (e.g., if face detection fails), or immediately mark as Failed and require manual intervention?
**Default if unknown:** No automatic retries - mark as Failed immediately with clear error message
**Reasoning:** Face detection failures usually indicate bad avatar/video quality. Automatic retries waste GPU time. User can fix and resubmit.

## Q5: Should we implement the Airtable MCP integration for easier development/testing, or use direct Airtable API calls via Make.com only?
**Default if unknown:** Yes - use Airtable MCP for development tools and testing scripts, but production flow still uses Make.com
**Reasoning:** MCP enables Claude Code to help with setup, debugging, and testing. Production automation remains in Make.com for reliability.
