#!/bin/bash
# One-time Railway setup: creates project, adds Postgres, sets SECRET_KEY, deploys.
# Run from your project root: bash scripts/railway_setup.sh

set -e

echo "==> Checking Railway CLI..."
if ! command -v railway &> /dev/null; then
  echo "Railway CLI not found. Installing..."
  npm install -g @railway/cli
fi

echo "==> Logging in to Railway (opens browser)..."
railway login

echo "==> Creating Railway project linked to this directory..."
railway init

echo "==> Adding PostgreSQL database..."
railway add --database postgresql

echo "==> Generating SECRET_KEY and setting variables..."
SECRET=$(openssl rand -hex 32)
railway variables set SECRET_KEY="$SECRET"
echo "    SECRET_KEY set."

echo "==> Linking DATABASE_URL from Postgres service..."
railway variables set DATABASE_URL="\${{Postgres.DATABASE_PRIVATE_URL}}"

echo "==> Deploying app..."
railway up --detach

echo "==> Generating public domain..."
railway domain

echo ""
echo "✓ Done! Your app is deploying."
echo "  Run 'railway open' to open the dashboard."
echo "  Run 'railway logs' to watch the build."
