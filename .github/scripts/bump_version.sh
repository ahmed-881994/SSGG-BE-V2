#!/bin/bash
set -e

# Usage: ./bump_version.sh <type>
# Types: major, minor, patch

if [ -z "$1" ]; then
    echo "Usage: $0 <type>"
    echo "Types: major, minor, patch"
    echo "Example: $0 patch"
    exit 1
fi

TYPE=$1

# Read current version
CURRENT_VERSION=$(cat VERSION)

# Parse version components
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]}

# Bump based on type
case $TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
    *)
        echo "❌ Error: Invalid type. Use major, minor, or patch"
        exit 1
        ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"

echo "📦 Bumping version from ${CURRENT_VERSION} to ${NEW_VERSION}..."

# Update VERSION file
echo "${NEW_VERSION}" > VERSION

# Commit and tag
git add VERSION
git commit -m "chore: bump version to ${NEW_VERSION}"

echo "✅ Version bumped to ${NEW_VERSION}"
echo ""
echo "Next step: git push origin $(git branch --show-current)"