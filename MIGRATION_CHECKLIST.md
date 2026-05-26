# Railway to Render Migration Checklist

## ✅ Pre-Migration Preparation

- [ ] Export all data from Railway PostgreSQL
- [ ] Document current environment variables
- [ ] Note any custom domain configurations
- [ ] Backup your Railway project
- [ ] Have GitHub repository credentials ready

## ✅ Render Setup

### Create Render Account & Connect Repository
- [ ] Sign up at https://render.com
- [ ] Connect GitHub account
- [ ] Grant Render access to your repository

### Create PostgreSQL Database
- [ ] Create new PostgreSQL instance on Render
- [ ] **Database name**: `siem_copilot`
- [ ] **Region**: Select geo-location closest to users
- [ ] **Backup frequency**: Select preference (default: daily)
- [ ] Copy internal connection string
- [ ] Enable connection pooling (optional, for high traffic)
- [ ] Note down credentials securely

### Deploy Backend Service
- [ ] Create new Web Service
- [ ] Connect to your GitHub repo
- [ ] **Name**: `siem-copilot-backend`
- [ ] **Runtime**: Python
- [ ] **Build Command**: `pip install -r requirements.txt`
- [ ] **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- [ ] Set environment variables (see below)
- [ ] Enable auto-deploy
- [ ] Verify service is running (check logs)

### Deploy Frontend Service
- [ ] Create new Web Service
- [ ] Connect to your GitHub repo
- [ ] **Name**: `siem-copilot-frontend`
- [ ] **Runtime**: Node
- [ ] **Build Command**: `npm install && npm run build`
- [ ] **Start Command**: `npm start`
- [ ] Set environment variables (see below)
- [ ] Enable auto-deploy
- [ ] Verify service is running

## ✅ Environment Variables

### Backend Service Variables
```
DATABASE_URL = <PostgreSQL internal connection string>
GROQ_API_KEY = <your Groq API key>
ENVIRONMENT = production
PYTHONUNBUFFERED = 1
CORS_ORIGINS = https://<frontend-render-url>.onrender.com
```

### Frontend Service Variables
```
NODE_ENV = production
NEXT_PUBLIC_API_URL = https://<backend-render-url>.onrender.com/api
```

## ✅ Post-Migration Verification

- [ ] Frontend loads without errors
- [ ] Backend API is accessible (check `/docs` endpoint)
- [ ] CORS errors don't appear in browser console
- [ ] Log in functionality works
- [ ] Can upload sample logs
- [ ] Chat interface connects to backend
- [ ] Database queries execute correctly
- [ ] No "Connection refused" errors in logs

## ✅ Custom Domain Setup (Optional)

- [ ] Point DNS records to Render
- [ ] Configure custom domain in service settings
- [ ] Wait for SSL certificate (auto-issued)
- [ ] Test HTTPS connection
- [ ] Update `CORS_ORIGINS` if using custom domain

## ✅ Monitoring & Maintenance

- [ ] Set up error alerts (if available on Render plan)
- [ ] Monitor database connection limits
- [ ] Check disk usage on PostgreSQL
- [ ] Review backend logs regularly
- [ ] Update `CORS_ORIGINS` if adding new domains

## ⚠️ Common Migration Issues & Solutions

### Issue: CORS Errors After Migration
**Solution**: Verify `CORS_ORIGINS` in backend environment matches your frontend URL exactly

### Issue: Database Connection Fails
**Solution**: Confirm `DATABASE_URL` format is correct: `postgresql://user:password@host:5432/dbname`

### Issue: Frontend Can't Connect to API
**Solution**: Check `NEXT_PUBLIC_API_URL` is correctly set and backend service is running

### Issue: Application Crashes on Startup
**Solution**: Check backend logs for missing dependencies; may need to update `requirements.txt`

## 📊 Performance Considerations

- **Backend Plan**: Start with Standard; upgrade to Pro for high traffic
- **Database Plan**: Standard (2GB) for small deployments; upgrade as needed
- **Frontend Plan**: Standard sufficient for most use cases
- **Caching**: Render handles static content caching automatically

## 🔄 Rollback Plan

If issues occur with Render:
- [ ] Previous deployments stored in Render (can be accessed via Events)
- [ ] Can redeploy previous version with one click
- [ ] Keep Railway account active for X days as fallback

## 📝 Documentation References

- [Render Deployment Guide](./RENDER_DEPLOYMENT.md)
- [Render Python Docs](https://render.com/docs/python)
- [Render PostgreSQL Docs](https://render.com/docs/databases)
- [Render Custom Domains](https://render.com/docs/custom-domains)

---

**Migration Date**: ________________  
**Completed By**: ________________  
**Notes**: 
