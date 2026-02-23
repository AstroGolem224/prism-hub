#!/bin/bash
# PRISM Hub — Build & Deploy to GitHub (triggers Cloudflare Pages)
set -e

cd "$(dirname "$0")"

echo "🔮 Building static site..."
python3 build.py

echo "📦 Committing changes..."
git add -A
git diff --cached --quiet && echo "No changes to deploy." && exit 0

git commit -m "🔮 Auto-deploy $(date '+%Y-%m-%d %H:%M')"

echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Deployed! Cloudflare Pages will build automatically."
