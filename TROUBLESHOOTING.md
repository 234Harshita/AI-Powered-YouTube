# 🔧 AI YouTube Analytics - Troubleshooting Guide

## Table of Contents
1. [Quick Start](#quick-start)
2. [Backend Issues](#backend-issues)
3. [Frontend Issues](#frontend-issues)
4. [Connection Issues](#connection-issues)
5. [Common Errors](#common-errors)
6. [Debugging Tips](#debugging-tips)

---

## Quick Start

### Windows
```batch
cd c:\Users\ViHarshita tripathi\Desktop\AI-Powered-YouTube
start_backend.bat
```

### macOS/Linux
```bash
cd ~/Desktop/AI-Powered-YouTube
bash start_backend.sh
```

### Manual Start
```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## Backend Issues

### ❌ "Backend connection failed"
**Cause:** Backend server is not running

**Solutions:**
1. Start the backend using one of the methods above
2. Verify the backend is running at http://localhost:8000/health
3. Check if port 8000 is already in use (see Port Conflict section)

---

### ❌ "Model not ready" or "Model not found"
**Cause:** ML model files are missing

**Solutions:**
1. Ensure model files exist:
   - `backend/models/model.pkl`
   - `backend/models/features.pkl`

2. If missing, train the model:
   ```bash
   python backend/train_model.py
   ```

3. Check the dataset exists at:
   - `Dataset/youtube.csv` or `Dataset/youtube_growth_dataset.xlsx`

---

### ❌ "Database initialization failed"
**Cause:** Database file is locked or corrupted

**Solutions:**
1. Delete the old database and let it recreate:
   ```bash
   rm youtube.db
   # or
   del youtube.db  # Windows
   ```

2. Restart the backend - it will create a fresh database

3. Check file permissions in the backend directory

---

### ❌ "Failed to save prediction to database"
**Cause:** Database file is locked (another process is using it)

**Solutions:**
1. Close any file explorers viewing the backend directory
2. Ensure only one backend instance is running
3. Delete and recreate the database (see above)

---

## Frontend Issues

### ❌ Frontend shows "🔴 Backend Disconnected"
**Cause:** Frontend cannot reach the backend

**Check:**
1. Backend is running: `http://localhost:8000/health`
2. No firewall blocking port 8000
3. Both running on localhost

**Fix:**
1. Start the backend first
2. Refresh the frontend page
3. Check browser console for detailed error messages (F12 → Console tab)

---

### ❌ Predictions fail even though backend is running
**Cause:** Model loading issue or database connection problem

**Check:**
1. Backend logs show any errors:
   - Look at `backend.log` file
   - Check terminal output

2. Model files are valid:
   ```bash
   python -c "import joblib; joblib.load('backend/models/model.pkl')"
   ```

**Fix:**
1. Restart the backend
2. Delete and recreate the database
3. Retrain the model

---

## Connection Issues

### 🔄 Frontend Auto-Reconnect
The frontend now automatically:
- ✅ Checks backend health every 10 seconds
- ✅ Retries failed requests with exponential backoff
- ✅ Shows connection status (🟢 Connected / 🔴 Disconnected)

**What to expect:**
- Stop backend → Frontend shows disconnected status
- Start backend → Frontend auto-reconnects (usually within 10 seconds)
- No page refresh needed!

---

### ❌ Port 8000 Already In Use
**Error:** `Address already in use`

**Solutions:**

1. **Find the process using port 8000:**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # macOS/Linux
   lsof -i :8000
   ```

2. **Kill the process:**
   ```bash
   # Windows
   taskkill /PID <PID> /F
   
   # macOS/Linux
   kill -9 <PID>
   ```

3. **Or use a different port:**
   ```bash
   python -m uvicorn backend.app:app --host 0.0.0.0 --port 8001 --reload
   ```

---

## Common Errors

### "ValueError: could not convert string to float"
**Cause:** Invalid input data (non-numeric values in numeric fields)

**Fix:**
- Ensure all form fields contain valid numbers
- Check field constraints in the form

---

### "KeyError: 'Predicted Views'"
**Cause:** Backend response format is incorrect

**Fix:**
1. Restart the backend
2. Check model is loaded correctly
3. Review backend logs

---

### "SyntaxError" in JavaScript
**Cause:** Browser doesn't support modern JavaScript

**Fix:**
- Use a modern browser (Chrome, Firefox, Safari, Edge - all recent versions)
- Update your browser

---

## Debugging Tips

### 1. **Check Backend Logs**
```bash
# View real-time logs
tail -f backend.log

# Or search for errors
grep ERROR backend.log
```

### 2. **Check Frontend Browser Console**
```
Press F12 → Console tab
Look for error messages and warnings
```

### 3. **Test API Endpoints Directly**
```bash
# Health check
curl http://localhost:8000/health

# Get history
curl http://localhost:8000/history

# Make a prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "title_length": 50,
    "upload_hour": 12,
    "category": "Tech",
    "tags_count": 10,
    "duration_min": 15,
    "thumbnail_score": 8,
    "seo_score": 7,
    "ctr_percent": 5.5,
    "likes": 500,
    "comments": 100,
    "subscriber_count": 50000,
    "viral_score": 8
  }'
```

### 4. **Check Database**
```bash
# Verify database exists and is accessible
ls -la youtube.db  # macOS/Linux
dir youtube.db     # Windows
```

### 5. **Enable Verbose Backend Logging**
Edit `backend/app.py` and look for LOG_LEVEL setting (already configured)

---

## Lifecycle - What Happens When

### ✅ Healthy Scenario
1. Backend starts → Creates database, loads model
2. Frontend loads → Checks health endpoint
3. Frontend shows "🟢 Backend Connected"
4. User submits prediction → Frontend retries if needed
5. Backend receives request → Loads model, makes prediction, saves to DB
6. Frontend displays result

### ⚠️ Backend Restart Scenario
1. Backend stops → Existing connections close
2. Frontend detects disconnect → Shows "🔴 Backend Disconnected"
3. Frontend checks every 10 seconds → Finds new backend
4. User makes prediction → Frontend auto-retries
5. Backend restarts → Loads fresh database connection
6. Prediction succeeds ✅

### ❌ Model Loading Failure
**Old behavior:** Backend crashes completely, never recovers
**New behavior:** 
- Backend starts but shows error on prediction attempts
- Frontend retries with exponential backoff
- Clear error message guides user to retrain model

---

## Performance Tips

1. **Reduce model loading overhead:**
   - Model now loads on-demand (lazy loading)
   - No performance penalty if not used

2. **Database optimization:**
   - WAL (Write-Ahead Logging) enabled for better concurrency
   - Connection pooling ready for future scaling

3. **Network optimization:**
   - Retry logic uses exponential backoff to avoid overwhelming server
   - Health checks cached between requests

---

## Getting Help

1. **Check logs:** `backend.log`
2. **Check browser console:** F12 → Console tab
3. **Test endpoints:** Use curl or Postman
4. **Review this guide:** Most issues are covered above

---

## Summary of Improvements

✅ **Health Check Endpoint** - Frontend can verify backend is ready
✅ **Auto-Reconnect** - Frontend automatically detects and reconnects
✅ **Retry Logic** - Requests retry with exponential backoff
✅ **Lazy Loading** - Model loads on-demand, not on startup
✅ **Better Logging** - All operations logged to backend.log
✅ **Connection Status** - Visual indicator in frontend
✅ **Error Handling** - Clear, actionable error messages
✅ **Startup Scripts** - Easy start with proper validation

---

**Last Updated:** 2024
**Version:** 1.0
