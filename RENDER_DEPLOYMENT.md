# Deploying to Render - Google Cloud TTS Setup Guide

## Step 1: Prepare Your Credentials

1. Open your `credentials.json` file
2. Copy the **entire JSON content** (all of it, from `{` to `}`)

## Step 2: Deploy to Render

### Option A: Using Render Dashboard (Recommended)

1. **Create a new Web Service** on Render
   - Connect your GitHub repository
   - Select the `backend` directory as the root

2. **Configure Build Settings:**
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variable:**
   - Go to **Environment** tab
   - Click **Add Environment Variable**
   - **Key:** `GOOGLE_CREDENTIALS_JSON`
   - **Value:** Paste the entire contents of your `credentials.json` file (the whole JSON object)
   
   Example:
   ```json
   {"type":"service_account","project_id":"fresh-thinker-475110-r3","private_key_id":"d9b77b4721920c024918b00166b190d9ad30b368",...}
   ```

4. **Deploy** - Render will automatically deploy your application

### Option B: Using render.yaml (Infrastructure as Code)

Create a `render.yaml` file in your project root:

```yaml
services:
  - type: web
    name: movment-backend
    env: python
    region: oregon
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GOOGLE_CREDENTIALS_JSON
        sync: false  # Set this manually in dashboard for security
```

Then set the `GOOGLE_CREDENTIALS_JSON` variable in the Render dashboard.

## Step 3: Verify Deployment

1. Once deployed, visit your Render service URL: `https://your-app.onrender.com/lecture`
2. You should see the lecture response with audio URLs
3. Check the logs to ensure no credential errors

## Important Notes

> [!WARNING]
> **Never commit credentials.json to your repository!** The `.gitignore` file already excludes it.

> [!TIP]
> **Testing locally:** Your local setup will continue using `credentials.json` file. The environment variable is only needed for Render.

> [!IMPORTANT]
> **JSON Formatting:** When pasting the credentials into Render, make sure it's valid JSON. You can verify at jsonlint.com if needed.

## Troubleshooting

### Issue: "Google Cloud credentials not found"
**Solution:** Make sure the environment variable name is exactly `GOOGLE_CREDENTIALS_JSON` (case-sensitive)

### Issue: "Invalid JSON"
**Solution:** Ensure you copied the entire JSON object including all braces. Test it with `python -c "import json; json.loads('YOUR_JSON_HERE')"`

### Issue: "Unable to create temporary file"
**Solution:** Render's filesystem should allow temp file creation. Check service logs for permission issues.

## Environment Variables Summary

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_CREDENTIALS_JSON` | Yes | Full JSON content from credentials.json |
| `PORT` | Auto-set by Render | Port for the web service |

## Additional Configuration (Optional)

You can also set these environment variables if needed:

```bash
# Python environment
PYTHONUNBUFFERED=1

# Production mode
ENVIRONMENT=production
```

---

## Quick Command Reference

**Local Development:**
```bash
uvicorn main:app --reload
```

**Production (Render):**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Test credentials locally with environment variable:**
```bash
# Windows PowerShell
$env:GOOGLE_CREDENTIALS_JSON = Get-Content credentials.json -Raw
uvicorn main:app --reload

# Linux/Mac
export GOOGLE_CREDENTIALS_JSON=$(cat credentials.json)
uvicorn main:app --reload
```
