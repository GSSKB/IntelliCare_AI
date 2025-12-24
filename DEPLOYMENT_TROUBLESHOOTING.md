# Deployment Troubleshooting Guide

## Common Issues and Solutions

### Backend Deployment Issues

#### 1. Build Failures

**Issue:** Build command fails during pip install

**Solutions:**
- Check if all dependencies in `requirements.txt` are compatible
- Some packages like `torch` and `sentence-transformers` are large and may timeout
- Try building with: `pip install --upgrade pip && pip install -r requirements.txt`

#### 2. Module Not Found Errors

**Issue:** `ModuleNotFoundError` when starting the service

**Solutions:**
- Ensure `rootDir: backend` is set in render.yaml
- Check that all imports use relative paths correctly
- Verify all dependencies are in `requirements.txt`

#### 3. File Not Found Errors

**Issue:** `cleaned_rag.txt` or model files not found

**Solutions:**
- Ensure all necessary files are committed to the repository:
  - `backend/cleaned_rag.txt`
  - `backend/ml_models/saved_models/*.pkl`
  - `backend/risk_model.pkl`
- Check file paths in code - they should be relative to the backend directory

#### 4. Port Issues

**Issue:** Service fails to start or bind to port

**Solutions:**
- Ensure start command uses `$PORT` environment variable
- Use: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Don't hardcode port numbers

#### 5. Memory Issues

**Issue:** Service runs out of memory (common with large ML models)

**Solutions:**
- Free tier has 512MB RAM limit
- Consider using smaller models
- Use `faiss-cpu` instead of `faiss-gpu`
- Consider upgrading to paid tier if models are too large

### Frontend Deployment Issues

#### 1. Build Failures

**Issue:** `npm run build` fails

**Solutions:**
- Check Node version compatibility (should be 18.x)
- Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
- Check for TypeScript errors

#### 2. API Connection Errors

**Issue:** Frontend can't connect to backend

**Solutions:**
- Set `VITE_API_URL` environment variable to your backend URL
- Format: `https://your-backend-service.onrender.com`
- No trailing slash
- Check CORS settings in backend (`ALLOWED_ORIGINS`)

#### 3. Preview Server Issues

**Issue:** Preview server doesn't start

**Solutions:**
- Use: `npm run preview -- --host 0.0.0.0 --port ${PORT:-4173}`
- Ensure PORT environment variable is set
- Check that build completed successfully

### Environment Variables

**Required for Backend:**
- `PYTHON_VERSION`: `3.12.0`
- `ALLOWED_ORIGINS`: Your frontend URL (e.g., `https://intellicare-ai-frontend.onrender.com`)

**Required for Frontend:**
- `NODE_VERSION`: `18.x`
- `VITE_API_URL`: Your backend URL (e.g., `https://intellicare-ai-backend.onrender.com`)

**Optional:**
- `GOOGLE_API_KEY`: For enhanced AI responses

### Checking Logs

1. Go to your service in Render dashboard
2. Click on "Logs" tab
3. Check for:
   - Build errors
   - Runtime errors
   - Import errors
   - File not found errors

### Testing Locally Before Deployment

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
npm install
npm run build
npm run preview
```

### File Size Limits

- Free tier: 100MB per service
- If models exceed this, consider:
  - Using Git LFS for large files
  - Storing models in cloud storage (S3, etc.)
  - Downloading models on startup from external source

### Cold Start Issues

- Free tier services spin down after 15 minutes
- First request after spin-down takes 30-60 seconds
- This is normal behavior for free tier
- Consider upgrading to paid tier for always-on services

## Getting Help

1. Check Render documentation: https://render.com/docs
2. Check service logs in Render dashboard
3. Test locally first to isolate issues
4. Verify all environment variables are set correctly

