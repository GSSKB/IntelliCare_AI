# Deploying IntelliCare AI to Render (Free Tier)

This guide will help you deploy both the frontend and backend services to Render using the **free tier**.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)
3. Google API Key (optional, for enhanced AI responses)

## Deployment Steps

### Option 1: Using render.yaml (Recommended)

1. **Push your code to GitHub/GitLab/Bitbucket**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Connect your repository to Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your Git repository
   - Render will automatically detect `render.yaml` and create both services

3. **Configure Environment Variables**
   
   **For Backend Service:**
   - Go to your backend service settings
   - Add environment variable:
     - `GOOGLE_API_KEY` (optional): Your Google AI API key
     - `ALLOWED_ORIGINS`: Your frontend URL (e.g., `https://intellicare-ai-frontend.onrender.com`)
   
   **For Frontend Service:**
   - Go to your frontend service settings
   - Add environment variable:
     - `VITE_API_URL`: Your backend URL (e.g., `https://intellicare-ai-backend.onrender.com`)

### Option 2: Manual Setup

#### Backend Service

1. **Create a new Web Service**
   - Go to Render Dashboard → "New +" → "Web Service"
   - Connect your repository
   - Configure:
     - **Name**: `intellicare-ai-backend`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r backend/requirements.txt`
     - **Start Command**: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`
     - **Root Directory**: Leave empty (or set to project root)

2. **Set Environment Variables**
   - `PYTHON_VERSION`: `3.12.0`
   - `GOOGLE_API_KEY`: (optional) Your Google AI API key
   - `ALLOWED_ORIGINS`: Your frontend URL

#### Frontend Service

1. **Create a new Static Site or Web Service**
   - Go to Render Dashboard → "New +" → "Static Site" (or Web Service)
   - Connect your repository
   - Configure:
     - **Name**: `intellicare-ai-frontend`
     - **Environment**: `Node`
     - **Build Command**: `npm install && npm run build`
     - **Publish Directory**: `dist`
     - **Root Directory**: Leave empty

2. **Set Environment Variables**
   - `NODE_VERSION`: `18.x`
   - `VITE_API_URL`: Your backend service URL (e.g., `https://intellicare-ai-backend.onrender.com`)

## Free Tier Limitations

**Important Notes about Render Free Tier:**
- Services spin down after 15 minutes of inactivity
- First request after spin-down may take 30-60 seconds to wake up
- 750 hours/month of free usage (enough for always-on single service)
- Build time limits apply
- File size limits: 100MB per service

**Recommendations:**
- Both services will auto-spin down when not in use
- First user after inactivity will experience a cold start delay
- Consider upgrading to Starter plan ($7/month) for always-on services

## Important Notes

### Backend Service

- The backend uses port `$PORT` (provided by Render)
- Services on free tier will spin down after inactivity
- Make sure all model files are committed to your repository:
  - `backend/ml_models/saved_models/*.pkl`
  - `backend/risk_model.pkl`
  - `backend/cleaned_rag.txt`
  - `backend/vector_store/` (if it contains files)
- **File Size Warning**: If your ML models exceed 100MB, consider using Git LFS or external storage

### Frontend Service

- The frontend is built as a static site using Vite
- API calls will use the `VITE_API_URL` environment variable in production
- If `VITE_API_URL` is not set, it will try to use `/api` (which won't work on a static site)

### CORS Configuration

- Update `ALLOWED_ORIGINS` in backend to include your frontend URL
- Format: `https://your-frontend.onrender.com` (no trailing slash)

### File Size Limits

- Render has file size limits for free tier
- If your ML models are too large, consider:
  - Using Git LFS for large files
  - Storing models in cloud storage (S3, etc.) and downloading on startup
  - Using smaller model files

## Post-Deployment

1. **Test the Backend**
   - Visit: `https://your-backend.onrender.com/docs`
   - You should see the FastAPI Swagger documentation
   - Test the `/chat` endpoint

2. **Test the Frontend**
   - Visit your frontend URL
   - Try sending a message in the chat
   - Check browser console for any errors

3. **Update Environment Variables**
   - If you need to change the API URL, update `VITE_API_URL` in frontend
   - If you need to allow a new origin, update `ALLOWED_ORIGINS` in backend

## Troubleshooting

### Backend Issues

- **Import errors**: Make sure all dependencies are in `backend/requirements.txt`
- **Port errors**: Ensure you're using `$PORT` in the start command
- **Model file errors**: Verify all `.pkl` files are committed to the repository

### Frontend Issues

- **API connection errors**: Check that `VITE_API_URL` is set correctly
- **Build errors**: Check that all dependencies are in `package.json`
- **CORS errors**: Verify `ALLOWED_ORIGINS` includes your frontend URL

### Common Solutions

1. **Check build logs** in Render dashboard
2. **Check runtime logs** for error messages
3. **Verify environment variables** are set correctly
4. **Ensure all files are committed** to your repository

## Custom Domain (Optional)

1. Go to your service settings
2. Click "Custom Domains"
3. Add your domain
4. Follow DNS configuration instructions

## Monitoring

- Render provides basic monitoring for free tier
- Check service health in the dashboard
- Set up alerts for service downtime

