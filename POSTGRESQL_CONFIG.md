# 🗄️ PostgreSQL Configuration Guide

This document explains how the SIEM Copilot application uses PostgreSQL on Render (formerly used Supabase).

---

## 📋 Current Database Setup

### **Local Development**
```env
# Uses SQLite by default
# Located at: data/siem_copilot.db
DATABASE_URL= (leave empty)
```

### **Render Deployment**
```env
# Automatically provided by Render PostgreSQL service
DATABASE_URL=postgresql://user:password@pghost:5432/siem_copilot
```

---

## 🔄 Migration from Supabase to PostgreSQL

### What Changed?
✅ Database provider changed from Supabase → Render PostgreSQL  
✅ Connection method: Same (both use PostgreSQL)  
✅ Code: No changes needed (already supports both)

### Database Configuration in Code

**File**: `backend/db/database.py`

```python
# Automatically detects database type:
# 1. If DATABASE_URL starts with "postgresql://" → Uses PostgreSQL
# 2. If DATABASE_URL is empty → Uses SQLite locally

DB_URL = settings.DATABASE_URL or f"sqlite:///data/{DB_NAME}"

engine = create_engine(
    DB_URL,
    connect_args=connect_args,
    pool_size=15 if not DB_URL.startswith("sqlite") else None,
    pool_pre_ping=True  # Ensures stable connections
)
```

---

## 🚀 Database URL Formats

### PostgreSQL (Render)
```
postgresql://username:password@db.onrender.com:5432/siem_copilot
```

**Parts**:
- `username` - Database user
- `password` - Database password  
- `db.onrender.com` - Render database host
- `5432` - PostgreSQL port
- `siem_copilot` - Database name

### PostgreSQL (Local)
```
postgresql://postgres:password@localhost:5432/siem_copilot
```

### SQLite (Local Development)
```
sqlite:///data/siem_copilot.db
# or
(leave DATABASE_URL empty)
```

---

## ✅ Configuration Checklist

### ✓ Local Development
- [ ] `DATABASE_URL` not set (uses SQLite)
- [ ] `data/` directory exists
- [ ] `siem_copilot.db` created on first run

### ✓ Render Deployment
- [ ] PostgreSQL service created (`siem-postgres`)
- [ ] `DATABASE_URL` environment variable set
- [ ] Database name: `siem_copilot`
- [ ] Connection successful

---

## 🔧 Environment Variables

### Required for Render
```env
# Database (auto-filled from Render PostgreSQL)
DATABASE_URL=postgresql://...

# AI Provider
GROQ_API_KEY=gsk_...

# Application Configuration
ENVIRONMENT=production
PYTHONUNBUFFERED=1
CORS_ORIGINS=https://siem-copilot-frontend.onrender.com
```

### Optional for Local Development
```env
# Leave empty to use SQLite
# DATABASE_URL=

# Or specify PostgreSQL connection
# DATABASE_URL=postgresql://user:pass@localhost:5432/siem_copilot
```

---

## 🔍 How It Works

### Connection Flow

```
┌─────────────────────────────────────────────┐
│ backend/config.py                           │
│ Reads DATABASE_URL from environment         │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│ backend/db/database.py                      │
│ Creates database engine                     │
│ - PostgreSQL if URL provided                │
│ - SQLite if URL empty (local dev)           │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│ SQLAlchemy ORM                              │
│ Manages database connections & queries      │
└─────────────────────────────────────────────┘
```

---

## 🧪 Testing Database Connection

### Verify PostgreSQL URL on Render
```python
# In backend logs, you'll see:
# "Database URL: postgresql://user:*****@db.onrender.com:5432/siem_copilot"
```

### Check SQLite (Local)
```bash
# Verify database file exists
ls -la data/siem_copilot.db
```

### Test Connection
```bash
# Backend will test on startup
# Check logs for: "✅ Database infrastructure ready."
```

---

## 🚨 Common Issues & Solutions

### Issue: "No database URL provided"
**Solution**: Leave `DATABASE_URL` empty for local SQLite development

### Issue: "PostgreSQL connection refused"
**Solution**: Verify `DATABASE_URL` is correctly formatted and Render PostgreSQL is running

### Issue: "Database doesn't exist"
**Solution**: Render auto-creates `siem_copilot` database from blueprint

### Issue: "Connection pool exhausted"
**Solution**: Render configuration has pool_size=15, sufficient for most use cases

---

## 📊 Database Comparison

| Feature | SQLite (Local) | PostgreSQL (Render) |
|---------|---|---|
| **Setup** | ✅ Automatic | ✅ Auto-created |
| **Data Persistence** | ✅ File-based | ✅ Cloud-hosted |
| **Concurrency** | ⚠️ Limited | ✅ Excellent |
| **Backup** | Manual | ✅ Automatic daily |
| **Cost** | Free | Free tier / $10.50/mo |
| **Cold Starts** | No impact | Yes (free tier only) |

---

## 🔐 Security Notes

**Never commit**:
- ❌ Real `DATABASE_URL` with credentials
- ❌ `.env` file with secrets
- ✅ Use environment variables on Render instead

**Already safe**:
- ✅ `.env` is in `.gitignore`
- ✅ Secrets not committed to GitHub
- ✅ Render provides clean DATABASE_URL

---

## 📚 Related Files

- [render.yaml](../render.yaml) - Database service definition
- [backend/config.py](../backend/config.py) - Configuration loading
- [backend/db/models.py](../backend/db/models.py) - Database schema
- [.env.render.example](../.env.render.example) - Environment template

---

## 🎯 Next Steps

1. ✅ **Local Development**: Uses SQLite (no setup needed)
2. 🚀 **Render Deployment**: PostgreSQL auto-configured via blueprint
3. 📂 **Backup**: Render handles automatic daily backups
4. 📈 **Scaling**: Upgrade plan if database grows beyond free limits

---

**Last Updated**: May 26, 2026  
**Status**: ✅ Migrated from Supabase to PostgreSQL  
**Database**: Ready for both local and cloud deployment
