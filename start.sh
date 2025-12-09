#!/bin/bash

# Railway startup script for Streamlit Financial Analysis System

echo "🚀 Starting Financial Analysis System..."

# Set default port if not provided
export PORT=${PORT:-8501}

echo "📊 Running on port $PORT"

# Run Streamlit with production settings
streamlit run streamlit_dashboard_PRODUCTION_FIXED.py \
  --server.port=$PORT \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --server.enableCORS=false \
  --server.enableXsrfProtection=false
