# GitHub Actions Setup for Docker Push

## Problem
Docker push keeps failing due to network issues when uploading 67.7GB image from local machine.

## Solution
Use GitHub Actions to build and push from GitHub's servers (fast, stable network).

## Setup Steps

### 1. Create GitHub Repository
```bash
# Initialize git repo (if not already done)
git init
git add .
git commit -m "Initial commit with face swapper deployment"

# Create repo on GitHub (private recommended for credentials)
gh repo create faceswapper-deployment --private --source=. --remote=origin --push
```

Or manually:
1. Go to https://github.com/new
2. Create private repo: `faceswapper-deployment`
3. Push code:
```bash
git remote add origin git@github.com:YOUR_USERNAME/faceswapper-deployment.git
git branch -M main
git push -u origin main
```

### 2. Add Docker Hub Secrets to GitHub
1. Go to: https://github.com/YOUR_USERNAME/faceswapper-deployment/settings/secrets/actions
2. Click "New repository secret"
3. Add these secrets:
   - Name: `DOCKER_USERNAME` Value: `kaspamontana`
   - Name: `DOCKER_PASSWORD` Value: `your-docker-hub-password-or-token`

To create Docker Hub token (recommended):
1. Go to https://hub.docker.com/settings/security
2. Click "New Access Token"
3. Name: "GitHub Actions"
4. Copy the token and use it as DOCKER_PASSWORD

### 3. Trigger Build
Push to GitHub will automatically trigger the workflow:
```bash
git push origin main
```

Or trigger manually:
1. Go to: https://github.com/YOUR_USERNAME/faceswapper-deployment/actions
2. Click "Build and Push Docker Image"
3. Click "Run workflow"

### 4. Monitor Progress
- Watch the Actions tab on GitHub
- Build takes ~60-90 minutes on GitHub's servers
- Much more reliable than local network

### 5. Once Complete
Update Runpod endpoint:
```bash
cd scripts
./update_endpoint.sh
```

Then test:
```bash
./test_endpoint.sh "VIDEO_URL" "AVATAR_URL"
```

## Advantages
- GitHub's fast, stable network
- No local bandwidth usage
- Free for public repos, 2000 min/month for private
- Can retry easily if needed
- Logs are preserved

## Cost
- Free for public repos
- Private repos: ~90 min build uses ~1.5 hours of 2000 free minutes
- Still plenty of quota remaining
