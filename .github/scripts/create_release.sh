#!/bin/bash
set -e

# Usage: ./create_release.sh <version>
# Example: ./create_release.sh 2.2.0

if [ -z "$1" ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 2.2.0"
    exit 1
fi

VERSION=$1
RELEASE_BRANCH="release/${VERSION}"

# Validate version format (X.Y.Z)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Error: Version must be in format X.Y.Z (e.g., 2.1.0)"
    exit 1
fi

echo "🚀 Creating release ${VERSION}..."

# Ensure we're on main branch
git checkout main
git pull origin main

# Create release branch
git checkout -b "${RELEASE_BRANCH}"

# Update VERSION file
echo "${VERSION}" > VERSION

# Commit version bump
git add VERSION
git commit -m "chore: bump version to ${VERSION}"

# Push release branch
git push origin "${RELEASE_BRANCH}"

echo "✅ Release branch ${RELEASE_BRANCH} created successfully!"
echo ""
echo "Next steps:"
echo "1. CI will automatically deploy to staging"
echo "2. Perform QA testing on staging environment"
echo "3. When ready, create git tag: git tag -a v${VERSION} -m 'Release v${VERSION}' && git push origin v${VERSION}"
echo "4. Tag creation will trigger production deployment"
echo "5. After production deployment, merge ${RELEASE_BRANCH} to main"