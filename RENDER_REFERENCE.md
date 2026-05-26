# 🎯 Render Deployment Quick Reference Card

## Deploy in 3 Steps

### Step 1: Push Code
```bash
git add .
git commit -m "Port to Render"
git push origin main
```

### Step 2: Create Render Blueprint
```
https://dashboard.render.com
→ "New +" → "Blueprint"
→ Select Repository
```

### Step 3: Set Environment Variables
```
GROQ_API_KEY = your_api_key
DATABASE_URL = (auto-filled from PostgreSQL)
CORS_ORIGINS = https://your-frontend.onrender.com
```

---

## 🔗 Important URLs

| Service | URL |
|---------|-----|
| **Render Dashboard** | https://dashboard.render.com |
| **GitHub** | https://github.com |
| **Groq Console** | https://console.groq.com |
| **App Frontend** | https://siem-copilot-frontend.onrender.com |
| **App Backend** | https://siem-copilot-backend.onrender.com |
| **API Docs** | https://siem-copilot-backend.onrender.com/docs |
| **API Health** | https://siem-copilot-backend.onrender.com/api/health |

---

## 📋 Environment Variables

### Backend (`siem-copilot-backend`)
```env
DATABASE_URL = postgresql://user:pass@host/siem_copilot
GROQ_API_KEY = gsk_xxxxxxxxxxxxx
ENVIRONMENT = production
PYTHONUNBUFFERED = 1
CORS_ORIGINS = https://siem-copilot-frontend.onrender.com
```

### Frontend (`siem-copilot-frontend`)
```env
NODE_ENV = production
NEXT_PUBLIC_API_URL = https://siem-copilot-backend.onrender.com/api
```

### Database (`siem-postgres`)
```
Database Name: siem_copilot
User: (auto-generated)
Password: (auto-generated)
```

---

## 🐛 Troubleshooting

### CORS Error in Browser
**Problem**: "CORS policy: blocked"  
**Solution**: Update `CORS_ORIGINS` env var to match your frontend URL

### Backend Not Responding
**Problem**: 502 Bad Gateway or timeout  
**Solution**: 
1. Check backend logs in Render dashboard
2. Verify `DATABASE_URL` is correct
3. Check `GROQ_API_KEY` is set

### Database Connection Failed
**Problem**: "could not connect to server"  
**Solution**:
1. Verify PostgreSQL service is running
2. Check `DATABASE_URL` format
3. Confirm database exists: `siem_copilot`

### Frontend Build Failed
**Problem**: "Build failed" in Render logs  
**Solution**:
1. Check for TypeScript errors
2. Verify dependencies in package.json
3. Check build log for specific error

---

## 📊 Service Status

### Health Check Endpoints
```bash
# Backend health check
curl https://siem-copilot-backend.onrender.com/api/health

# Expected response:
{
  "status": "operational",
  "service": "SIEM Copilot Enterprise API",
  "environment": "production"
}
```

### Verify Services Running
```
Render Dashboard:
  → Services
  → siem-copilot-backend (should show "Live")
  → siem-copilot-frontend (should show "Live")
  → PostgreSQL (should show running)
```

---

## 🔄 Common Tasks

### Restart a Service
```
Render Dashboard → Service → Manual Deploy
```

### View Logs
```
Render Dashboard → Service → Logs tab
```

### Update Environment Variables
```
Render Dashboard → Service → Environment
(Changes auto-trigger redeploy)
```

### Check Database
```
Render Dashboard → PostgreSQL → Database tab
```

### Add Custom Domain
```
Render Dashboard → Service → Custom Domain
(Follow DNS setup instructions)
```

---

## 💾 Database Management

### Connect to PostgreSQL Locally
```bash
psql "postgresql://user:password@host:5432/siem_copilot"
```

### Backup Database
Automatic daily backups enabled on Render

### Database Info
```
Name: siem_copilot
Location: Render servers
Backup: Daily automatic
SSL/TLS: Enabled
```

---

## 🚨 Critical Checklist Before Going Live

- [ ] Backend service deployed and running
- [ ] Frontend service deployed and loading
- [ ] PostgreSQL database created
- [ ] All environment variables set
- [ ] CORS properly configured
- [ ] Can access `/api/health` endpoint
- [ ] Log in functionality works
- [ ] Chat feature connects to API
- [ ] No errors in browser console
- [ ] No errors in backend logs

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| **render.yaml** | Infrastructure config |
| **RENDER_DEPLOYMENT.md** | Detailed setup guide |
| **RENDER_QUICKSTART.md** | Quick reference |
| **MIGRATION_CHECKLIST.md** | Step-by-step verification |
| **MIGRATION_SUMMARY.md** | What was changed |
| **.env.render.example** | Environment variables |

---

## 🎓 Learning Resources

- [Render Docs](https://render.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Next.js Docs](https://nextjs.org/docs)
- [PostgreSQL Docs](https://www.postgresql.org/docs)

---

## 💬 Support

- **Render Support**: https://support.render.com
- **GitHub Issues**: Add `[render]` tag
- **Community**: Render Discord Community

---

**Keep this card handy for quick reference during deployment!**
