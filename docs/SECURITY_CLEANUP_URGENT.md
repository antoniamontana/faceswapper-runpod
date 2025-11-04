# 🚨 URGENT SECURITY CLEANUP - Exposed Credentials

## What Happened

**Exposed credentials in GitHub repository:**
- AWS Access Key: `AKIAQPFMTVPPQLCI6X3X`
- AWS Secret Key
- RunPod API Key
- Airtable API Key
- Make.com Webhook URL

**Files containing secrets:**
1. `READY_TO_LAUNCH.md` (committed to git)
2. `docker/config.yaml` (committed to git)
3. `SESSION_HANDOFF.md` (committed to git)
4. `config/config.yaml` (NOT committed but has credentials)

**AWS Response:** Applied quarantine policy to your IAM user `faceswapper-service`

---

## IMMEDIATE ACTION PLAN (30 minutes)

### Phase 1: Clean Repository (10 min)

#### Step 1: Remove Credentials from Files
I'll sanitize the files and remove all credentials.

#### Step 2: Update .gitignore
I'll make it more comprehensive to prevent future exposure.

#### Step 3: Clean Git History
Remove sensitive data from all commits:
```bash
# Use git-filter-repo (recommended) or BFG Repo Cleaner
git filter-repo --path READY_TO_LAUNCH.md --invert-paths
git filter-repo --path docker/config.yaml --invert-paths
```

**OR simpler approach:**
```bash
# Force push sanitized version (loses history but fastest)
git checkout main
git rm --cached docker/config.yaml
git commit -m "Remove sensitive config file"
git push --force origin main
```

---

### Phase 2: Rotate ALL Credentials (20 min)

#### A. AWS Credentials (5 min)
1. Go to: https://console.aws.amazon.com/iam/
2. Find user: `faceswapper-service`
3. **Delete the compromised access key**
4. **Create NEW access key**
5. Save the new credentials (you'll need them!)

**New credentials will be:**
- Access Key: `AKIA...` (new)
- Secret Key: `...` (new)

#### B. RunPod API Key (2 min)
1. Go to: https://www.runpod.io/console/user/settings
2. Under "API Keys"
3. **Delete:** `rpa_OSPY0BMF92K6JKMWOTMIJ6EJQHCY3FVNJBJBGEKM1td0zk`
4. **Create new key**
5. Save it

#### C. Airtable API Key (3 min)
1. Go to: https://airtable.com/create/tokens
2. Find token that starts with: `patlwJxGENTnKmGeF...`
3. **Delete it**
4. **Create new token** with same permissions:
   - `data.records:read`
   - `data.records:write`
   - Scoped to base: `appHjohuWApnPJvd3`
5. Save it

#### D. Make.com Webhook (5 min)
1. Go to: https://make.com/scenarios
2. Open "Face Swap - Webhook Receiver"
3. Click the Webhook module
4. Click "Delete" on current webhook
5. Click "Add" to create new webhook
6. **Copy NEW webhook URL**
7. Save scenario

8. **Update Main Pipeline:**
   - Open "Face Swap - Main Pipeline"
   - Find the HTTP module that sends webhook back
   - Update with new webhook URL
   - Save

---

### Phase 3: Update Configurations (5 min)

#### A. Update Local Config Files

**Edit:** `config/config.yaml`
```yaml
runpod:
  api_key: "NEW_RUNPOD_KEY"

storage:
  s3_access_key: "NEW_AWS_ACCESS_KEY"
  s3_secret_key: "NEW_AWS_SECRET_KEY"

airtable:
  api_key: "NEW_AIRTABLE_KEY"

webhook:
  completion_url: "NEW_MAKE_COM_WEBHOOK_URL"
```

**Edit:** `docker/config.yaml` (same changes)

#### B. Update RunPod Environment Variables

1. Go to: https://www.runpod.io/console/serverless
2. Click endpoint: `eaj61xejeec2iw`
3. Click "Edit"
4. Update Environment Variables:
   ```
   AWS_ACCESS_KEY_ID=NEW_AWS_ACCESS_KEY
   AWS_SECRET_ACCESS_KEY=NEW_AWS_SECRET_KEY
   WEBHOOK_URL=NEW_MAKE_COM_WEBHOOK_URL
   ```
5. Click "Update Endpoint"

#### C. Update Make.com Scenarios

**In "Face Swap - Main Pipeline":**
1. HTTP Request module → Update RunPod API key
2. Airtable modules → Reconnect with new API key
3. Save scenario

---

## Step-by-Step Execution Order

### DO THIS IN ORDER:

1. **I'll clean the files** (remove credentials from code)
2. **You rotate credentials:**
   - [ ] AWS (5 min)
   - [ ] RunPod (2 min)
   - [ ] Airtable (3 min)
   - [ ] Make.com webhook (5 min)
3. **Update local configs** with new credentials
4. **Update RunPod endpoint** with new env vars
5. **Update Make.com** connections
6. **Clean git history** and force push
7. **Verify everything works** with test

---

## Files I Will Create

1. `READY_TO_LAUNCH.md` (sanitized - NO credentials)
2. `SESSION_HANDOFF.md` (sanitized - NO credentials)
3. `docker/config.yaml.example` (template with placeholders)
4. `config/config.yaml.example` (template with placeholders)
5. Updated `.gitignore` (comprehensive)

---

## What to Keep Private (NEVER COMMIT)

**Always keep private:**
- `config/config.yaml` ✅ (already in .gitignore)
- `docker/config.yaml` ❌ (needs to be added)
- `*.env` ✅ (already in .gitignore)
- Any file with actual API keys/secrets

**Safe to commit:**
- `config/config.yaml.example` (template)
- `docker/config.yaml.example` (template)
- Documentation (after sanitizing)
- Code files (without secrets)

---

## After Cleanup Checklist

- [ ] No credentials in any committed files
- [ ] All credentials rotated
- [ ] `.gitignore` updated
- [ ] Git history cleaned
- [ ] Force pushed to GitHub
- [ ] RunPod updated with new credentials
- [ ] Make.com updated with new keys
- [ ] Test end-to-end pipeline
- [ ] Verify no AWS quarantine warnings

---

## Prevention for Future

**NEVER put credentials in:**
- Markdown files (docs, README, etc.)
- YAML files that get committed
- Code files
- Scripts (unless .gitignored)

**ALWAYS use:**
- Environment variables in RunPod
- `.gitignore` for config files
- `.example` template files (without real values)
- Separate config files (gitignored)

---

## Ready to Start?

**Say "YES" and I will:**
1. Sanitize all files (remove credentials)
2. Update .gitignore
3. Create template config files
4. Give you exact steps for credential rotation

**Then you:**
1. Rotate all credentials (15-20 min)
2. Update local configs
3. Update RunPod
4. Update Make.com
5. Force push cleaned repo
6. Test!

---

**Time: ~30 minutes total**
**Difficulty: Easy (step-by-step)**
**Urgency: HIGH (credentials are public!)**
