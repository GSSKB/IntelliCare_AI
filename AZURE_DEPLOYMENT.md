# Deploying IntelliCare AI to Azure (Free Tier)

This guide will help you deploy both the frontend and backend services to Azure using the free tier.

## Architecture

- **Frontend**: Azure Static Web Apps (Free tier - 100GB bandwidth/month)
- **Backend**: Azure App Service (Free tier - F1, 60 min/day compute)

## Prerequisites

1. Azure account (free account available at https://azure.microsoft.com/free/)
2. GitHub repository connected to Azure
3. Azure CLI installed (optional, for command-line deployment)

---

## Option 1: Deploy via Azure Portal (Easiest)

### Step 1: Deploy Backend (Azure App Service)

1. **Go to Azure Portal**: https://portal.azure.com

2. **Create App Service**:
   - Click "Create a resource" → "Web App"
   - Configure:
     - **Subscription**: Your subscription
     - **Resource Group**: Create new or use existing
     - **Name**: `intellicare-ai-backend` (must be unique)
     - **Publish**: Code
     - **Runtime stack**: Python 3.12
     - **Operating System**: Linux
     - **Region**: Choose closest to you
     - **Pricing Plan**: Free F1 (60 min/day)

3. **Click "Review + create"** → **"Create"**

4. **Configure Deployment**:
   - Go to your App Service → "Deployment Center"
   - Source: GitHub
   - Connect your GitHub account
   - Select repository: `GSSKB/IntelliCare_AI`
   - Branch: `main`
   - Build provider: GitHub Actions
   - Runtime stack: Python
   - Save

5. **Configure Startup Command**:
   - Go to "Configuration" → "General settings"
   - Startup Command: 
     ```
     gunicorn --bind=0.0.0.0 --timeout 600 --workers=2 --worker-class uvicorn.workers.UvicornWorker app:app
     ```
   - Save and restart

6. **Set Environment Variables**:
   - Go to "Configuration" → "Application settings"
   - Add:
     - `SCM_DO_BUILD_DURING_DEPLOYMENT`: `true`
     - `GOOGLE_API_KEY`: Your Google AI API key (optional)
     - `ALLOWED_ORIGINS`: Your frontend URL (set after frontend deployment)

7. **Set Working Directory** (Important!):
   - Go to "Configuration" → "Path mappings" or "General settings"
   - Or add application setting:
     - `WEBSITE_RUN_FROM_PACKAGE`: `0`
   - The backend code is in the `backend` folder

### Step 2: Deploy Frontend (Azure Static Web Apps)

1. **Create Static Web App**:
   - Go to Azure Portal → "Create a resource"
   - Search "Static Web Apps" → Create
   - Configure:
     - **Subscription**: Your subscription
     - **Resource Group**: Same as backend
     - **Name**: `intellicare-ai-frontend`
     - **Plan type**: Free
     - **Region**: Choose closest to you
     - **Source**: GitHub
     - Connect GitHub and select repository

2. **Build Configuration**:
   - **App location**: `/`
   - **Output location**: `dist`
   - **Build preset**: Custom
   - Click "Review + create" → "Create"

3. **Configure Environment Variables**:
   - Go to your Static Web App → "Configuration"
   - Add:
     - `VITE_API_URL`: Your backend URL (e.g., `https://intellicare-ai-backend.azurewebsites.net`)

4. **Update Backend CORS**:
   - Go back to your App Service
   - Add frontend URL to `ALLOWED_ORIGINS` environment variable

---

## Option 2: Deploy via Azure CLI

### Prerequisites
```bash
# Install Azure CLI
# macOS: brew install azure-cli
# Windows: Download from https://aka.ms/installazurecliwindows
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login
```

### Deploy Backend

```bash
# Set variables
RESOURCE_GROUP="intellicare-rg"
LOCATION="eastus"
BACKEND_NAME="intellicare-ai-backend"
PLAN_NAME="intellicare-plan"

# Create resource group
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service plan (Free tier)
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --sku F1 \
  --is-linux

# Create Web App
az webapp create \
  --name $BACKEND_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --runtime "PYTHON:3.12"

# Configure startup command
az webapp config set \
  --name $BACKEND_NAME \
  --resource-group $RESOURCE_GROUP \
  --startup-file "gunicorn --bind=0.0.0.0 --timeout 600 --workers=2 --worker-class uvicorn.workers.UvicornWorker app:app"

# Set environment variables
az webapp config appsettings set \
  --name $BACKEND_NAME \
  --resource-group $RESOURCE_GROUP \
  --settings SCM_DO_BUILD_DURING_DEPLOYMENT=true

# Deploy from GitHub (or use zip deploy)
cd backend
zip -r ../backend.zip . -x "venv/*" -x "__pycache__/*"
cd ..
az webapp deployment source config-zip \
  --name $BACKEND_NAME \
  --resource-group $RESOURCE_GROUP \
  --src backend.zip
```

### Deploy Frontend

```bash
# Install SWA CLI
npm install -g @azure/static-web-apps-cli

# Build frontend
npm install
npm run build

# Deploy to Azure Static Web Apps
swa deploy ./dist \
  --deployment-token <YOUR_DEPLOYMENT_TOKEN> \
  --env production
```

---

## Free Tier Limitations

### Azure App Service Free (F1)
- 60 CPU minutes/day
- 1 GB memory
- No custom domains (uses `.azurewebsites.net`)
- No SSL for custom domains
- App may sleep after inactivity

### Azure Static Web Apps Free
- 100 GB bandwidth/month
- 2 custom domains
- Free SSL
- Global CDN
- Unlimited staging environments

### Recommendations
- Free tier is good for demos and testing
- For production, consider Basic (B1) plan (~$13/month)
- Static Web Apps free tier is usually sufficient for frontend

---

## Environment Variables

### Backend (App Service)
| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_API_KEY` | Google AI API key (optional) | `AIza...` |
| `ALLOWED_ORIGINS` | Frontend URL for CORS | `https://your-frontend.azurestaticapps.net` |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | Enable build | `true` |

### Frontend (Static Web Apps)
| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://intellicare-ai-backend.azurewebsites.net` |

---

## Troubleshooting

### Backend Issues

**1. Application not starting**
- Check logs: App Service → "Log stream" or "Diagnose and solve problems"
- Verify startup command is correct
- Check if all dependencies are installed

**2. Import errors**
- Ensure `SCM_DO_BUILD_DURING_DEPLOYMENT=true` is set
- Check if working directory is correct (should be `backend`)

**3. CORS errors**
- Add frontend URL to `ALLOWED_ORIGINS` environment variable
- Restart the App Service after changing settings

**4. Timeout errors**
- Free tier has limited CPU time (60 min/day)
- ML model loading may take time on cold start
- Consider upgrading to Basic tier

### Frontend Issues

**1. Build failures**
- Check Node version (should be 18.x)
- Verify `npm run build` works locally
- Check build logs in GitHub Actions

**2. API connection errors**
- Verify `VITE_API_URL` is set correctly
- Check backend is running and accessible
- Check browser console for specific errors

**3. Routing issues**
- `staticwebapp.config.json` handles SPA routing
- Ensure navigation fallback is configured

---

## Accessing Your Apps

After deployment:
- **Frontend**: `https://<your-static-web-app-name>.azurestaticapps.net`
- **Backend**: `https://<your-app-service-name>.azurewebsites.net`
- **Backend API Docs**: `https://<your-app-service-name>.azurewebsites.net/docs`

---

## Monitoring

- **App Service**: Go to "Metrics" or "Log stream" in Azure Portal
- **Static Web Apps**: Check "Overview" for traffic statistics
- **Application Insights**: Enable for advanced monitoring (may incur costs)

---

## Upgrading from Free Tier

If you need more resources:

1. **App Service**: Scale up to B1 ($13/month) or higher
   ```bash
   az appservice plan update --name $PLAN_NAME --resource-group $RESOURCE_GROUP --sku B1
   ```

2. **Static Web Apps**: Standard plan ($9/month) for more features
   - More bandwidth
   - Password protection
   - Custom authentication

