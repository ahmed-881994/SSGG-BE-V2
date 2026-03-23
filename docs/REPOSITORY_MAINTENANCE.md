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

1. Create release branch from `main`:
   ```bash
   .github/scripts/create_release.sh
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

1. Create hotfix from main:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/2.2.1
   echo "2.2.1" > VERSION
   git commit -am "chore: bump version to 2.2.1"
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

### Version Numbers

We follow **Semantic Versioning** (semver):

- **MAJOR.MINOR.PATCH** (e.g., 2.1.0)
- **MAJOR:** Breaking changes
- **MINOR:** New features (backwards-compatible)
- **PATCH:** Bug fixes (backwards-compatible)