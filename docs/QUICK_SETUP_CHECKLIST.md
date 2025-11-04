# Quick Setup Checklist - UGC Face Swapper V1

**Current Status:**
- ✅ Airtable base created: `appHjohuWApnPJvd3`
- ✅ Config file created with Airtable credentials
- ⏳ AWS S3 setup (15 minutes)
- ⏳ Make.com setup (20 minutes)
- ⏳ Runpod setup (10 minutes)

---

## Step 1: AWS S3 Setup (15 minutes)

### 1.1 Create AWS Account
- Go to: https://aws.amazon.com/
- Click "Create an AWS Account"
- Use your email + credit card (needed for verification, won't be charged much)

### 1.2 Create S3 Bucket
1. Go to: https://s3.console.aws.amazon.com/s3/
2. Click **"Create bucket"**
3. Settings:
   - **Bucket name:** `faceswap-outputs-kasparas` (must be globally unique)
   - **Region:** US East (N. Virginia) us-east-1
   - **Block Public Access:** UNCHECK all boxes (we need public URLs)
   - Click "Create bucket"

4. Configure bucket for public access:
   - Click on your new bucket
   - Go to **Permissions** tab
   - Scroll to **Bucket Policy**
   - Click **Edit** and paste this:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::faceswap-outputs-kasparas/*"
    }
  ]
}
```
   - Replace `faceswap-outputs-kasparas` with YOUR bucket name
   - Click **Save changes**

### 1.3 Create IAM User and Get Access Keys
1. Go to: https://console.aws.amazon.com/iam/
2. Click **Users** → **Create user**
3. **User name:** `faceswapper-service`
4. Click **Next**
5. **Permissions:** Click "Attach policies directly"
6. Search and select: **AmazonS3FullAccess**
7. Click **Next** → **Create user**

8. Create access keys:
   - Click on the user you just created
   - Go to **Security credentials** tab
   - Scroll to **Access keys**
   - Click **Create access key**
   - Select **Application running outside AWS**
   - Click **Next** → **Create access key**
   - **COPY BOTH:**
     - Access key ID (starts with AKIA...)
     - Secret access key (long random string)
   - Click **Done**

### 1.4 Save Your AWS Credentials
**Bucket name:** `faceswap-outputs-kasparas`
**Access key ID:** `AKIA...`
**Secret access key:** `...`

---

## Step 2: Make.com Setup (20 minutes)

### 2.1 Create Make.com Account
- Go to: https://www.make.com/en/register
- Sign up for **Core plan** ($29/month) - needed for webhook + Airtable
- Verify email

### 2.2 Create Webhook Receiver Scenario
1. Click **Create a new scenario**
2. Add **Webhooks** module:
   - Search "Webhooks"
   - Select **Custom webhook**
   - Click **Add** to create new webhook
   - Name it: `Face Swap Completion`
   - Click **Save**
   - **COPY THE WEBHOOK URL** (starts with `https://hook.make.com/...`)

3. Add **Airtable** module:
   - Click the **+** icon after Webhooks
   - Search "Airtable"
   - Select **Update a Record**
   - Click **Add** to create connection
   - Enter your Airtable API key: `patlwJxGENTnKmGeF.48b68649086330d63c1496993b1fd91697eb7f41bc5887d08a00e45c63845395`
   - Click **Save**

4. Configure Airtable module:
   - **Base:** UGC Face Swap Pipeline
   - **Table:** Processing Queue
   - **Record ID:** Map from webhook: `video_id`
   - **Fields to update:**
     - `Status`: Map from webhook: `status`
     - `Output_Video_URL`: Map from webhook: `output_url`
     - `Error_Log`: Map from webhook: `error` (if present)

5. Click **Save** → Turn the scenario **ON**

### 2.3 Create Main Pipeline Scenario
1. Click **Create a new scenario**
2. Add **Airtable** trigger:
   - Search "Airtable"
   - Select **Watch Records**
   - Connection: Use existing
   - **Base:** UGC Face Swap Pipeline
   - **Table:** Processing Queue
   - **Trigger field:** Status
   - **Trigger value:** Pending
   - **Limit:** 1
   - Click **OK**

3. Add **HTTP** module:
   - Click **+** after Airtable
   - Search "HTTP"
   - Select **Make a request**
   - **URL:** `https://api.runpod.ai/v2/YOUR_TEMPLATE_ID/run` (we'll fill this later)
   - **Method:** POST
   - **Headers:**
     - `Authorization`: `Bearer YOUR_RUNPOD_API_KEY` (we'll fill this later)
     - `Content-Type`: `application/json`
   - **Body:**
```json
{
  "input": {
    "video_id": "{{1.id}}",
    "source_video_url": "{{1.Source_Video_URL}}",
    "avatar_image_url": "{{1.Avatar_Image_URL}}",
    "callback_url": "YOUR_WEBHOOK_URL_FROM_STEP_2.2"
  }
}
```

4. Add **Airtable** update module:
   - Click **+**
   - Search "Airtable"
   - Select **Update a Record**
   - **Base:** UGC Face Swap Pipeline
   - **Table:** Processing Queue
   - **Record ID:** `{{1.id}}`
   - **Fields:**
     - `Status`: Processing
     - `GPU_Instance_ID`: `{{2.id}}`

5. Click **Save** → Turn scenario **ON**
6. **Schedule:** Set to run every 5 minutes

### 2.4 Save Your Make.com Webhook URL
**Webhook URL:** `https://hook.make.com/...`

---

## Step 3: Runpod Setup (10 minutes)

### 3.1 Create Runpod Account
- Go to: https://www.runpod.io/
- Click **Sign Up**
- Complete registration

### 3.2 Add Credits
1. Click your profile (top right) → **Billing**
2. Click **Add Credits**
3. Add **$50** (enough for ~1000 videos)
4. Complete payment

### 3.3 Get API Key
1. Click your profile → **Settings**
2. Go to **API Keys** tab
3. Click **+ API Key**
4. Name: `Face Swapper Service`
5. Click **Create**
6. **COPY THE API KEY** (starts with `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### 3.4 Save Your Runpod API Key
**API Key:** `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

---

## Step 4: Update Config File

Once you have all credentials, update `/config/config.yaml`:

```yaml
storage:
  s3_bucket: "YOUR_BUCKET_NAME"
  s3_access_key: "YOUR_ACCESS_KEY"
  s3_secret_key: "YOUR_SECRET_KEY"

webhook:
  completion_url: "YOUR_WEBHOOK_URL"
```

---

## Step 5: Update Make.com with Runpod Details

After creating the Runpod template (next step), update the Make.com HTTP module with:
- Runpod API endpoint
- Runpod API key
- Template ID

---

## Next Steps After Account Setup

1. **Build Docker image** (with Wan2.2-Animate model)
2. **Push to Docker Hub**
3. **Create Runpod template**
4. **Test end-to-end** with a real video
5. **Start processing videos!**

---

**Estimated Total Setup Time:** 45 minutes
**Monthly Cost:** ~$174 for 100 videos/day
**Per Video Cost:** ~$0.058
