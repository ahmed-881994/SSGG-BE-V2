#!/bin/bash
set -e

# Usage: ./create_release.sh
# Reads version from VERSION file and creates release branch

# Check if VERSION file exists
if [ ! -f "VERSION" ]; then
    echo "❌ Error: VERSION file not found"
    echo "   Make sure you're in the repository root directory"
    exit 1
fi

# Read version from VERSION file
VERSION=$(cat VERSION | tr -d '[:space:]')

# Validate version format (X.Y.Z)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Error: VERSION file contains invalid format: ${VERSION}"
    echo "   Expected format: X.Y.Z (e.g., 2.1.0)"
    exit 1
fi

RELEASE_BRANCH="release/${VERSION}"

echo "📦 Version detected: ${VERSION}"
echo "🚀 Creating release branch: ${RELEASE_BRANCH}..."

# Ensure we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Currently on branch: ${CURRENT_BRANCH}"
    echo "   Switching to main branch..."
    git checkout main
fi

git pull origin main

# Check if release branch already exists
if git show-ref --verify --quiet refs/heads/${RELEASE_BRANCH}; then
    echo "❌ Error: Branch ${RELEASE_BRANCH} already exists locally"
    exit 1
fi

if git ls-remote --heads origin ${RELEASE_BRANCH} | grep -q ${RELEASE_BRANCH}; then
    echo "❌ Error: Branch ${RELEASE_BRANCH} already exists on remote"
    exit 1
fi

# Create release branch (VERSION is already correct, no need to update)
git checkout -b "${RELEASE_BRANCH}"

# Push release branch
git push origin "${RELEASE_BRANCH}"

echo "✅ Release branch ${RELEASE_BRANCH} created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. CI will automatically deploy to staging"
echo "2. Perform QA testing on staging: https://api.stg.sportingscout.org"
echo "3. When ready for production, create and push tag:"
echo "   git tag -a v${VERSION} -m 'Release v${VERSION}'"
echo "   git push origin v${VERSION}"
echo "4. After production deployment, merge to main:"
echo "   git checkout main"
echo "   git merge --no-ff ${RELEASE_BRANCH}"
echo "   git push origin main"