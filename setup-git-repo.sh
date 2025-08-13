#!/bin/bash

# Redis Enterprise Web Application - Git Repository Setup Script
# This script initializes and pushes the project to GitHub

set -e

echo "🚀 Setting up Redis Enterprise Web Application Git Repository"
echo "============================================================"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -f "redis-app.py" ]; then
    echo "❌ Error: Please run this script from the redis-enterprise-web-app directory"
    exit 1
fi

# Initialize git repository
echo "📁 Initializing Git repository..."
git init

# Add all files
echo "📝 Adding files to Git..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Redis Enterprise Web Application

Features:
- Flask web application with beautiful UI
- TLS-enabled Redis Enterprise Database connection
- Multiple data type generators (strings, hashes, sets, lists, sorted sets)
- Real-time database statistics
- Kubernetes deployment manifests
- Comprehensive documentation

Components:
- Python Flask application
- Redis Enterprise Database with TLS + mTLS
- Kubernetes LoadBalancer service
- Client certificate authentication
- Responsive web interface"

# Set up remote repository
echo "🔗 Setting up remote repository..."
echo "Please enter your GitHub username (default: naresh29s):"
read -r github_username
github_username=${github_username:-naresh29s}

echo "Please enter the repository name (default: redis-enterprise-web-app):"
read -r repo_name
repo_name=${repo_name:-redis-enterprise-web-app}

# Add remote origin
git remote add origin "https://github.com/${github_username}/${repo_name}.git"

echo "📤 Repository configured for: https://github.com/${github_username}/${repo_name}"
echo ""
echo "Next steps:"
echo "1. Create the repository on GitHub: https://github.com/new"
echo "2. Repository name: ${repo_name}"
echo "3. Make it public or private as needed"
echo "4. Don't initialize with README (we already have one)"
echo "5. Run: git push -u origin main"
echo ""
echo "Or run this command to push now:"
echo "git push -u origin main"

echo ""
echo "✅ Git repository setup complete!"
echo "📁 Repository: https://github.com/${github_username}/${repo_name}"
