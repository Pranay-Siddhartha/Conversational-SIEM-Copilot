# 🚀 Render Deployment Quick Start

## One-Click Deployment (Recommended)

### Using Blueprint (Infrastructure as Code)
```bash
1. Commit all changes to GitHub (including render.yaml)
2. Go to: https://dashboard.render.com
3. Click "New +" → "Blueprint"
4. Select your GitHub repository
5. Render automatically deploys all services
```

## Manual Step-by-Step Setup

### Prerequisites
✅ Render account  
✅ GitHub repository  
✅ Groq API key  

### 1️⃣ Create PostgreSQL Database
```
Render Dashboard → "New +" → "PostgreSQL"
- Name: siem-postgres
- Database: siem_copilot
- Region: [Your region]
- Copy internal connection string
```

### 2️⃣ Deploy Backend Service
```
"New +" → "Web Service" → GitHub repo
- Name: siem-copilot-backend
- Runtime: Python
- Root: .
- Build: pip install -r requirements.txt
- Start: python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT

Environment Variables:
DATABASE_URL=<from PostgreSQL>
GROQ_API_KEY=<your key>
ENVIRONMENT=production
PYTHONUNBUFFERED=1
CORS_ORIGINS=https://<frontend-url>.onrender.com
```

### 3️⃣ Deploy Frontend Service  
```
"New +" → "Web Service" → GitHub repo
- Name: siem-copilot-frontend
- Runtime: Node
- Root: .
- Build: npm install && npm run build
- Start: npm start

Environment Variables:
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://<backend-url>/api
```

## ✅ Verification Checklist

- [ ] PostgreSQL created and running
- [ ] Backend service deployed (check logs for errors)
- [ ] Frontend service deployed
- [ ] Can access frontend URL in browser
- [ ] Backend API endpoint responds at `/api/health`
- [ ] No CORS errors in browser console
- [ ] Can upload sample logs
- [ ] Chat functionality works

## 🔍 Monitoring

**Backend Logs**: Services → siem-copilot-backend → Logs  
**Frontend Logs**: Services → siem-copilot-frontend → Logs  
**Database Logs**: PostgreSQL → Logs  

## 🆘 Troubleshooting

### CORS Errors
→ Update `CORS_ORIGINS` to match your frontend URL exactly

### Database Connection Failed
→ Verify `DATABASE_URL` format and PostgreSQL is running

### Build Failed
→ Check build logs in Render dashboard

### API Not Responding
→ Check backend service health at `/health` endpoint

## 📚 Documentation

- **Full Guide**: [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
- **Migration Checklist**: [MIGRATION_CHECKLIST.md](MIGRATION_CHECKLIST.md)
- **Render Docs**: https://render.com/docs

## 🔄 Continuous Deployment

Auto-deploy is enabled. When you push to `main`:
1. Render detects changes
2. Rebuilds services
3. Deploys automatically
4. Notifies on success/failure

## 💰 Pricing Estimate

- **Backend**: $7/month (standard)
- **Frontend**: $7/month (standard)
- **Database**: $15/month (standard, 2GB)
- **Total**: ~$29/month (start)

Scales as needed.

---

**Need help?** Check the logs or see [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)
