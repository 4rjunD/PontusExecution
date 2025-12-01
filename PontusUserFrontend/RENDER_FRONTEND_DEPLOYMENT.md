# Deploy Frontend to Render

## Overview

The frontend is a Next.js application that needs to be deployed as a separate Web Service on Render, pointing to your backend API at `https://pontusexecution.onrender.com`.

## Step-by-Step Deployment

### 1. Create New Web Service in Render

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `4rjunD/PontusExecution`
3. Configure the service:

### 2. Basic Settings

- **Name:** `pontus-frontend` (or any name)
- **Environment:** Production
- **Region:** Oregon (US West) - same as backend
- **Branch:** `main`
- **Root Directory:** `PontusUserFrontend` ⚠️ **IMPORTANT**

### 3. Build & Start Commands

**Build Command:**
```bash
npm install && npm run build
```

**Start Command:**
```bash
npm start
```

### 4. Environment Variables

Add this environment variable:

**NEXT_PUBLIC_API_URL:**
- Key: `NEXT_PUBLIC_API_URL`
- Value: `https://pontusexecution.onrender.com`

This tells the frontend where to find your backend API.

### 5. Instance Type

- **Free** (for testing) - 512 MB RAM
- **Starter** ($7/month) - 512 MB RAM, 0.5 CPU (recommended)

### 6. Deploy

Click **"Create Web Service"** and wait for deployment (3-5 minutes).

## After Deployment

Your frontend will be available at:
- `https://pontus-frontend.onrender.com` (or your custom domain)

The frontend will automatically connect to your backend at `https://pontusexecution.onrender.com`.

## Troubleshooting

### Build Fails
- Check Root Directory is set to `PontusUserFrontend`
- Verify `package.json` exists in that directory
- Check build logs for specific errors

### Frontend Can't Connect to Backend
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running and accessible
- Check CORS settings on backend (should allow frontend domain)

### 404 Errors
- Next.js needs proper routing configuration
- Check `next.config.js` is correct

