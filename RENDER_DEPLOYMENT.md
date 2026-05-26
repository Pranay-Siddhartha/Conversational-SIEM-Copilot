# Render Deployment Guide

This document provides step-by-step instructions for deploying the SIEM Copilot application to Render.

## Prerequisites

- Render account (https://render.com)
- GitHub repository connected to your account
- Environment variables configured on Render

## Deployment Steps

### 1. Connect GitHub Repository

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New +** > **Web Service**
3. Select your GitHub repository: `Conversational-SIEM-Copilot`
4. Authorize Render to access your repository

### 2. Create PostgreSQL Database

1. In Render Dashboard, click **New +** > **PostgreSQL**
2. Configure:
   - **Name**: `siem-postgres`
   - **Database**: `siem_copilot`
   - **User**: Use generated credentials (copy for later)
   - **Region**: Select closest to your users
   - **Plan**: Standard (or your preference)
3. Note the internal connection string (you'll need it)

### 3. Deploy Backend Service

1. Click **New +** > **Web Service**
2. Connect GitHub repository
3. Configure:
   - **Name**: `siem-copilot-backend`
   - **Runtime**: Python
   - **Root Directory**: `.` (root of repository)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Standard or higher (recommended for FastAPI)
   - **Region**: Same as database

4. Add Environment Variables:
   ```
   DATABASE_URL = <from PostgreSQL instance internal connection string>
   ENVIRONMENT = production
   PYTHONUNBUFFERED = 1
   GROQ_API_KEY = <your Groq API key>
   CORS_ORIGINS = <your frontend Render URL>
   ```

### 4. Deploy Frontend Service

1. Click **New +** > **Web Service**
2. Connect GitHub repository
3. Configure:
   - **Name**: `siem-copilot-frontend`
   - **Runtime**: Node
   - **Root Directory**: `.`
   - **Build Command**: `npm install && npm run build`
   - **Start Command**: `npm start`
   - **Plan**: Standard
   - **Region**: Same as other services

4. Add Environment Variables:
   ```
   NODE_ENV = production
   NEXT_PUBLIC_API_URL = https://<backend-service-url>/api
   ```

## Using render.yaml for Infrastructure as Code

Alternatively, you can use the included `render.yaml` file for automated deployment:

1. Commit `render.yaml` to your repository
2. Go to Render Dashboard
3. Click **New +** > **Blueprint**
4. Select your repository
5. Render will automatically read `render.yaml` and create all services

## Environment Variables

The application requires these environment variables:

### Backend
- `DATABASE_URL`: PostgreSQL connection string
- `GROQ_API_KEY`: Groq API key for AI features
- `ENVIRONMENT`: Set to `production`
- `PYTHONUNBUFFERED`: Set to `1`
- `CORS_ORIGINS`: Frontend URL (https://your-frontend.onrender.com)

### Frontend
- `NODE_ENV`: Set to `production`
- `NEXT_PUBLIC_API_URL`: Your Render backend URL

## Database Initialization

After deployment, the PostgreSQL database is automatically initialized. The backend migrations will run when the service starts.

## Monitoring and Debugging

### Logs
- Access logs from Render Dashboard: **Services** > **{service-name}** > **Logs**

### Health Checks
- Backend health check endpoint: `/docs` (FastAPI Swagger UI)
- Frontend will be accessible at your Render URL

## Common Issues & Solutions

### Application Not Starting
1. Check that `DATABASE_URL` is correctly set
2. Verify `GROQ_API_KEY` is valid
3. Check backend logs for errors

### CORS Errors
1. Verify `CORS_ORIGINS` includes your frontend URL
2. Ensure it's the full HTTPS URL with no trailing slash

### Database Connection Failures
1. Verify `DATABASE_URL` format: `postgresql://user:password@host:port/dbname`
2. Confirm PostgreSQL service is running
3. Check network access rules

## Scaling

- To scale backend: Increase the plan or add more instances via Render Dashboard
- Render automatically manages load balancing
- PostgreSQL can be upgraded to handle more connections

## Custom Domain

1. Go to service settings
2. Click **Custom Domain**
3. Follow instructions to point your domain
4. SSL certificate is automatically configured

## Rollback

If deployment fails:
1. Go to **Service** > **Events**
2. Previous deployments are visible
3. Click **Redeploy** on a previous version to rollback

## Continuous Deployment

The application is set to auto-deploy on every push to the main branch. To disable:
1. Go to **Service Settings**
2. Uncheck **Auto-Deploy**

---

For more information, refer to [Render Documentation](https://render.com/docs)
