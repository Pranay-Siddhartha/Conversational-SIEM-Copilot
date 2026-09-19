#!/bin/bash
set -e

echo "🔨 Render Build Script - SIEM Copilot"
echo "======================================="

# Detect if this is backend, frontend, or both
if [ -f "requirements.txt" ] && [ -d "backend" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ Python dependencies installed"
fi

if [ -f "package.json" ]; then
    echo "📦 Installing Node dependencies..."
    npm install
    echo "✅ Node dependencies installed"
    
    if [ -f "next.config.ts" ] || [ -f "next.config.js" ]; then
        echo "🏗️ Building Next.js frontend..."
        npm run build
        echo "✅ Frontend built successfully"
    fi
fi

echo "✅ Build complete!"
