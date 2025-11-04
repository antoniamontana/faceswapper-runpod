# Fix Make.com Scenario - Missing Record ID

## The Problem

**Error:** `Missing value of required parameter 'id'`

**What happened:**
1. ✅ Airtable Search Records - Found your row
2. ✅ HTTP Request to RunPod - Sent the job
3. ❌ Airtable Update Record - Failed because no record ID

**Why:** The "Update a Record" module isn't receiving the record ID from step 1.

---

## The Fix (5 minutes)

### Step 1: Open the Scenario

1. Go to: https://make.com/scenarios
2. Click on **"Face Swap - Main Pipeline"**
3. Click the **"Edit"** button (pencil icon)

### Step 2: Fix Module 3 (Airtable - Update a Record)

1. Click on the **"Airtable - Update a Record"** module (step 3)
2. You'll see the configuration panel on the right

### Step 3: Map the Record ID

**In the module settings, find the "Record ID" field:**

Currently it's probably:
- Empty, or
- Has a broken mapping

**Fix it:**
1. Click in the **"Record ID"** field
2. You'll see a list of available data from previous steps
3. Look for **"Airtable - Search Records"** → **"id"**
4. Click to select it
5. It should now show something like: `{{1.id}}` or `{{module1.id}}`

**Visual guide:**
```
Module 3: Airtable - Update a Record
┌─────────────────────────────────┐
│ Base: [Your base]              │
│ Table: [Your table]            │
│ Record ID: {{1.id}} ← FIX THIS │
│                                 │
│ Fields to update:               │
│ - Status: Processing            │
│ - (other fields...)             │
└─────────────────────────────────┘
```

### Step 4: While You're Here - Check Other Fields

Make sure these are also mapped in the "Update a Record" module:

**Fields that should be mapped:**
- **Record ID:** `{{1.id}}` (from Search Records)
- **Status:** Set to "Processing" (manual text)
- **RunPod_Job_ID:** `{{2.id}}` (from HTTP request response)

### Step 5: Save and Test

1. Click **"OK"** to close the module
2. Click **"Save"** (bottom right)
3. Click **"Run once"** to test

---

## Alternative: Quick Fix Screenshot Guide

If the above is confusing, here's what to look for:

**Module 3 should look like this:**

```
Connection: [Your Airtable connection]
Base: appHjohuWApnPJvd3
Table: [Your table name]
Record ID: {{1.id}}  ← This is the key!

Fields to Update:
- Status = "Processing"
- RunPod_Job_ID = {{2.id}}
```

**The `{{1.id}}` comes from:**
- Module 1 (Airtable - Search Records)
- Field name: "id"
- This is the Airtable record ID

---

## After You Fix It

### Test Again:

1. In Airtable, change your test row Status back to "Pending"
2. The Make.com scenario should trigger automatically (or click "Run once")
3. Watch the execution history again

**Expected flow:**
1. Search Records → ✅ Found
2. HTTP Request → ✅ RunPod job created
3. Update Record → ✅ Status changed to "Processing"

---

## If You Still Get Errors

**Share with me:**
1. Screenshot of the "Airtable - Update a Record" module configuration
2. The new error message from Make.com History

---

## Why This Happened

The scenario was probably created without properly mapping the record ID from the search results. This is a common Make.com configuration issue.

**The fix is simple:** Just tell Make.com which record to update by passing the ID from step 1.

---

## Need Help?

If you can't find the "id" field to map:

1. Make sure Module 1 (Search Records) is actually finding records
2. Check that the search is configured correctly
3. Try clicking "Choose where to map" in the Record ID field
4. Look for data from "Airtable - Search Records" module

The ID should be there as `{{1.id}}` or similar.

---

**Fix this one field and your pipeline will work!**
