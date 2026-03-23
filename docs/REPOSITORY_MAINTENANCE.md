# Repository Maintenance

## Branching Strategy

### Branch Overview

| Branch | Purpose | Lifetime | Protected | Deploy Target |
|--------|---------|----------|-----------|---------------|
| `main` | Stable codebase, base for all branches | Permanent | Yes | None (no auto-deploy) |
| `release/X.Y.Z` | Release preparation and QA | Temporary | No | Staging (auto on push) |
| `hotfix/X.Y.Z` | Urgent production fixes | Temporary | No | Staging (auto on push) |
| `feature/*` | Feature development | Temporary | No | None (build only) |
| `bugfix/*` | Non-critical bug fixes | Temporary | No | None (build only) |
| **Tags: vX.Y.Z** | **Production releases** | **Permanent** | **N/A** | **Production (auto)** |

### Workflow

#### Feature Development

1. Create feature branch from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/my-feature
    ```
2. Develop, commit, and push:
   ```bash
   git add .
   git commit -m "feat: implement my feature"
   git push origin feature/my-feature
   ```

3. Create Pull Request: `feature/my-feature` → `main`

4. After approval and merge, changes are integrated into `main` (no auto-deployment)

### Release Process

1. Create release branch from `main` (this also bumps version):
   ```bash
   # Recommended: Using script (bumps version on main, then creates release branch)
   .github/scripts/create_release.sh minor  # or 'major' for breaking changes
   # This will:
   # 1. Bump VERSION on main (e.g., 2.1.0 → 2.2.0)
   # 2. Commit and push to main
   # 3. Create release/2.2.0 branch from main
   # 4. Push release branch
   # 5. Auto-deploy to staging
   
   # Manual alternative:
   git checkout main
   git pull origin main
   .github/scripts/bump_version.sh minor
   git checkout -b release/2.2.0
   git push origin release/2.2.0
   ```

2. Push triggers auto-deployment to **staging** for QA

3. Fix any bugs directly on release branch:
   ```bash
   git checkout release/2.2.0
   git pull origin release/2.2.0
   # Make fixes
   git push origin release/2.2.0
   # Re-deploys to staging automatically
   ```

4. When QA passes, create git tag:
   ```bash
   git checkout release/2.2.0
   git tag -a v2.2.0 -m "Release v2.2.0"
   git push origin v2.2.0
   # Tag creation triggers production deployment
   ```

5. After production deployment succeeds, merge release branch to `main`:
   ```bash
   git checkout main
   git merge --no-ff release/2.2.0 -m "Merge release/2.2.0"
   git push origin main
   
   # Delete release branch
   git branch -d release/2.2.0
   git push origin --delete release/2.2.0
   ```

### Hotfix Process

1. Create hotfix branch (bumps version on main first):
   ```bash
   git checkout main
   git pull origin main
   .github/scripts/bump_version.sh patch
   # VERSION bumped on main (e.g., 2.2.0 → 2.2.1), committed, and pushed
   git checkout -b hotfix/2.2.1
   git push origin hotfix/2.2.1
   # Auto-deploys to staging
   ```

2. Make urgent fixes:
   ```bash
   git add .
   git commit -m "fix: critical production issue"
   git push origin hotfix/2.2.1
   # Auto-deploys to staging
   ```

3. Test on staging and when ready, create tag:
   ```bash
   git checkout hotfix/2.2.1
   git tag -a v2.2.1 -m "Hotfix v2.2.1"
   git push origin v2.2.1
   # Tag triggers production deployment
   ```

4. After production deployment, merge to main:
   ```bash
   git checkout main
   git merge --no-ff hotfix/2.2.1 -m "Merge hotfix/2.2.1"
   git push origin main
   
   # Delete hotfix branch
   git branch -d hotfix/2.2.1
   git push origin --delete hotfix/2.2.1
   ```

### Branch Naming Conventions

- **Features:** `feature/short-description` (e.g., `feature/user-authentication`)
- **Bug fixes:** `bugfix/issue-123` or `bugfix/short-description`
- **Releases:** `release/X.Y.Z` (e.g., `release/2.2.0`)
- **Hotfixes:** `hotfix/X.Y.Z` (e.g., `hotfix/2.2.1`)

### Branch Lifecycle

- **feature/*** and **bugfix/*** branches: Delete after merge to main
- **release/*** branches: Delete after tag creation and merge to main
- **hotfix/*** branches: Delete after tag creation and merge to main
- **main**: Never delete (permanent branch)

## Version Management Scripts

The repository includes utility scripts for version and release management located in `.github/scripts/`:

**Key Principle**: Version bumping happens on `main` branch **before** creating release/hotfix branches. This ensures main always reflects the "next" version.

### bump_version.sh

Automates version bumping according to semantic versioning.

**Usage:**
```bash
.github/scripts/bump_version.sh <type>
```

**Types:**
- `major` - Breaking changes (e.g., 2.1.0 → 3.0.0)
- `minor` - New features (e.g., 2.1.0 → 2.2.0)
- `patch` - Bug fixes (e.g., 2.1.0 → 2.1.1)

**What it does:**
1. Reads current version from VERSION file
2. Increments the specified component (major/minor/patch)
3. Updates VERSION file with new version
4. Commits with message: `chore: bump version to X.Y.Z`
5. Pushes to current branch automatically

**Typical workflow:**
```bash
# Bump version on main before creating release/hotfix branch
git checkout main
git pull origin main
.github/scripts/bump_version.sh minor
# VERSION file updated to 2.2.0, committed, and pushed to main

# Then create release branch
git checkout -b release/2.2.0
git push origin release/2.2.0
```

**When to use:**
- **Before creating release branches**: Use `minor` or `major` while on main
- **Before creating hotfix branches**: Use `patch` while on main
- **Important**: Typically run on main branch before creating release/hotfix branches

### create_release.sh

**Status**: ✅ Fully implemented

Automates the complete release branch creation workflow.

**Usage:**
```bash
.github/scripts/create_release.sh <type>
```

**Types:**
- `major` - Breaking changes (e.g., 2.1.0 → 3.0.0)
- `minor` - New features (e.g., 2.1.0 → 2.2.0)
- `patch` - Bug fixes (e.g., 2.1.0 → 2.1.1)

**What it does:**
1. Ensures you're on main branch (switches if needed)
2. Pulls latest changes from origin/main
3. Calls `bump_version.sh` to increment version on main
4. Creates release branch with the new version (e.g., `release/2.2.0`)
5. Pushes release branch to origin
6. Provides next steps for QA and production deployment

**Example:**
```bash
.github/scripts/create_release.sh minor
# Output:
# 📦 Bumping version from 2.1.0 to 2.2.0...
# ✅ Version bumped to 2.2.0
# 🚀 Creating release branch: release/2.2.0...
# ✅ Release branch release/2.2.0 created successfully!
```

**Benefits:**
- Validates VERSION file format (X.Y.Z)
- Checks for existing release branches (prevents duplicates)
- Atomic operation - version bump and branch creation together
- Clear next steps printed after completion

---

### Version Numbers

We follow **Semantic Versioning** (semver):

- **MAJOR.MINOR.PATCH** (e.g., 2.1.0)
- **MAJOR:** Breaking changes
- **MINOR:** New features (backwards-compatible)
- **PATCH:** Bug fixes (backwards-compatible)

### VERSION File Strategy

The `VERSION` file on the `main` branch represents the **next planned release** version:

**Version Bumping Flow:**
1. **Before creating a release/hotfix branch**: Bump version on `main` first
2. **Main branch**: Always contains the next version number
3. **Release/Hotfix branches**: Inherit the version from `main` when created
4. **After merging back**: Main already has the correct version for next release

**Example Timeline:**
```bash
# Main is at 2.1.0 (current production version)
# Ready to start 2.2.0 release

# Step 1: Bump version on main
git checkout main
.github/scripts/bump_version.sh minor  # Main now at 2.2.0

# Step 2: Create release branch (inherits 2.2.0)
git checkout -b release/2.2.0

# Step 3: After release/2.2.0 goes to production and merges back to main
# Main is still at 2.2.0

# Step 4: When ready for next release
.github/scripts/bump_version.sh minor  # Main now at 2.3.0
```

**Benefits of this approach:**
- Clear indication of what's being worked on
- Feature branches use meaningful version tags (`v2.3.0-abc1234`)
- No version conflicts when merging releases back to main
- Main branch always represents "next" state