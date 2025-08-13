# 🚀 Production Deployment Guide - DigitalOcean App Platform

## 📋 Prerequisites

1. **DigitalOcean Account** with App Platform access
2. **GitHub Repository** with your code
3. **Google AI API Key** for Gemini
4. **doctl CLI** (DigitalOcean command-line tool)

## 🔧 Step-by-Step Deployment

### **Step 1: Install doctl CLI**

```bash
# macOS
brew install doctl

# Windows (with Chocolatey)
choco install doctl

# Linux
snap install doctl

# Or download from: https://github.com/digitalocean/doctl/releases
```

### **Step 2: Authenticate with DigitalOcean**

```bash
doctl auth init
# Enter your DigitalOcean API token when prompted
```

### **Step 3: Prepare Your Repository**

1. **Push your code to GitHub** (if not already done)
2. **Update the `.do/app.yaml` file** with your repository details:
   ```yaml
   github:
     repo: your-username/your-repo-name
     branch: main
   ```

### **Step 4: Deploy via DigitalOcean Console**

1. **Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)**
2. **Click "Create App"**
3. **Choose "GitHub" as source**
4. **Select your repository and branch**
5. **Configure the app:**

#### **App Configuration:**
- **Name**: `financial-analysis-api`
- **Environment**: `Python`
- **Build Command**: Leave empty (auto-detected)
- **Run Command**: `python start_prod.py`
- **Instance Size**: `Basic XXS` (for testing) or `Basic XS` (for production)

#### **Environment Variables:**
```
GOOGLE_API_KEY=your_actual_google_api_key
PORT=8000
ENVIRONMENT=production
DEBUG=false
```

#### **Health Check:**
- **Path**: `/health`
- **Initial Delay**: `30 seconds`
- **Interval**: `10 seconds`
- **Timeout**: `5 seconds`

### **Step 5: Deploy and Test**

1. **Click "Create Resources"**
2. **Wait for deployment to complete**
3. **Test your API endpoints**

## 🌐 **Accessing Your Deployed API**

After deployment, you'll get a URL like:
```
https://financial-analysis-api-abc123.ondigitalocean.app
```

### **Test Endpoints:**
```bash
# Health check
curl https://your-app-url.ondigitalocean.app/health

# API info
curl https://your-app-url.ondigitalocean.app/

# Documentation
# Visit: https://your-app-url.ondigitalocean.app/docs
```

## 🔄 **Updating Your App**

### **Option 1: Via Console (Manual)**
1. Push changes to GitHub
2. Go to App Platform console
3. Click "Deploy" to trigger new deployment

### **Option 2: Via CLI (Automated)**
```bash
# Get your app ID
doctl apps list

# Update the app
doctl apps update YOUR_APP_ID --spec .do/app.yaml
```

### **Option 3: Auto-deploy (Recommended)**
1. Enable auto-deploy in App Platform console
2. Every push to main branch triggers deployment

## 📊 **Monitoring and Scaling**

### **View Logs:**
```bash
doctl apps logs YOUR_APP_ID
```

### **Monitor Performance:**
- Go to App Platform console
- Click on your app
- View metrics and logs

### **Scale Your App:**
- Increase instance count for more concurrent users
- Upgrade instance size for better performance
- Enable auto-scaling based on metrics

## 🔒 **Security Best Practices**

### **Environment Variables:**
- ✅ Never commit API keys to Git
- ✅ Use DigitalOcean's encrypted environment variables
- ✅ Rotate API keys regularly

### **Network Security:**
- ✅ Use HTTPS (automatically provided by App Platform)
- ✅ Consider adding custom domain with SSL
- ✅ Implement rate limiting if needed

### **API Security:**
- ✅ Add authentication for production use
- ✅ Validate all input files
- ✅ Implement request size limits

## 🐛 **Troubleshooting**

### **Common Issues:**

#### **1. Build Failures**
```bash
# Check build logs
doctl apps logs YOUR_APP_ID --type build
```

#### **2. Runtime Errors**
```bash
# Check runtime logs
doctl apps logs YOUR_APP_ID --type run
```

#### **3. Health Check Failures**
- Verify your `/health` endpoint works locally
- Check environment variables are set correctly
- Ensure the app starts within the initial delay period

#### **4. API Key Issues**
- Verify `GOOGLE_API_KEY` is set correctly
- Check the key has proper permissions
- Ensure the key is valid and not expired

### **Debug Commands:**
```bash
# Get app status
doctl apps get YOUR_APP_ID

# View app spec
doctl apps spec YOUR_APP_ID

# Check app logs
doctl apps logs YOUR_APP_ID --follow
```

## 💰 **Cost Optimization**

### **Instance Sizing:**
- **Basic XXS**: $5/month (good for testing)
- **Basic XS**: $12/month (good for production)
- **Basic S**: $24/month (high performance)

### **Auto-scaling:**
- Enable auto-scaling to handle traffic spikes
- Set minimum instances to 0 for cost savings
- Use scheduled scaling for predictable workloads

## 🚀 **Next Steps After Deployment**

1. **Test all API endpoints** with your ERP system
2. **Set up monitoring** and alerting
3. **Configure custom domain** (optional)
4. **Set up CI/CD** for automated deployments
5. **Implement backup strategies** for your data

## 📞 **Support**

- **DigitalOcean Support**: Available in your account
- **App Platform Docs**: [https://docs.digitalocean.com/products/app-platform/](https://docs.digitalocean.com/products/app-platform/)
- **Community**: [DigitalOcean Community](https://www.digitalocean.com/community)

---

**Happy Deploying! 🎉**
