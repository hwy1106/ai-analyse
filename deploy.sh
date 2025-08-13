#!/bin/bash

# DigitalOcean App Platform Deployment Script
echo "🚀 Deploying Financial Analysis API to DigitalOcean App Platform..."

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl CLI is not installed. Please install it first:"
    echo "   https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if user is authenticated
if ! doctl account get &> /dev/null; then
    echo "❌ Please authenticate with DigitalOcean first:"
    echo "   doctl auth init"
    exit 1
fi

# Set your app ID (you'll get this after first deployment)
APP_ID="your-app-id-here"

# Update the app
echo "📤 Deploying to DigitalOcean App Platform..."
doctl apps update $APP_ID --spec .do/app.yaml

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌍 Your API will be available at the URL shown in the DigitalOcean console"
    echo "📊 Monitor deployment: doctl apps get $APP_ID"
else
    echo "❌ Deployment failed!"
    exit 1
fi
