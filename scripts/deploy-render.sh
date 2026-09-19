#!/bin/bash
# Deployment helper script for Render migration
# This script provides guidance for deploying to Render

set -e

echo "🚀 SIEM Copilot - Render Deployment Helper"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Verify Prerequisites${NC}"
echo "  ✓ Render account (https://render.com)"
echo "  ✓ GitHub repository connected"
echo "  ✓ Groq API key ready"
echo ""

echo -e "${BLUE}Step 2: Create PostgreSQL Database on Render${NC}"
echo "  1. Go to Render Dashboard"
echo "  2. Click 'New +' → 'PostgreSQL'"
echo "  3. Set database name: 'siem_copilot'"
echo "  4. Copy the internal connection string"
echo ""

echo -e "${BLUE}Step 3: Deploy Backend Service${NC}"
echo "  1. Click 'New +' → 'Web Service'"
echo "  2. Select your GitHub repository"
echo "  3. Configure:"
echo "     - Name: siem-copilot-backend"
echo "     - Runtime: Python"
echo "     - Build: pip install -r requirements.txt"
echo "     - Start: python -m uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"
echo "  4. Add environment variables:"
echo "     - DATABASE_URL (from PostgreSQL)"
echo "     - GROQ_API_KEY"
echo "     - ENVIRONMENT: production"
echo "     - PYTHONUNBUFFERED: 1"
echo ""

echo -e "${BLUE}Step 4: Deploy Frontend Service${NC}"
echo "  1. Click 'New +' → 'Web Service'"
echo "  2. Select same repository"
echo "  3. Configure:"
echo "     - Name: siem-copilot-frontend"
echo "     - Runtime: Node"
echo "     - Build: npm install && npm run build"
echo "     - Start: npm start"
echo "  4. Add environment variables:"
echo "     - NODE_ENV: production"
echo "     - NEXT_PUBLIC_API_URL: https://<backend-url>/api"
echo ""

echo -e "${GREEN}✅ Follow these steps to complete your migration!${NC}"
echo ""
echo "For detailed instructions, see: RENDER_DEPLOYMENT.md"
