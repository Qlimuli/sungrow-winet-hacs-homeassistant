# Deployment Guide

This guide explains how to deploy the Sungrow WINET-S integration to GitHub and make it available via HACS.

## Prerequisites

- GitHub account
- Git installed locally
- This repository ready to publish

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `sungrow-winet-s`
3. Description: `Home Assistant integration for Sungrow inverters via WINET-S`
4. Public repository
5. **Do NOT** initialize with README (we have one)
6. Click "Create repository"

## Step 2: Update URLs in Files

Before pushing, update these files with your GitHub username:

### `manifest.json`
```json
"documentation": "https://github.com/YOUR-USERNAME/sungrow-winet-s",
"issue_tracker": "https://github.com/YOUR-USERNAME/sungrow-winet-s/issues",
```

### README.md
Replace all instances of:
- `yourusername` → your GitHub username
- Update badge URLs

## Step 3: Initial Commit

From the `/app` directory:

```bash
# If not already initialized
git init

# Add files (custom_components is the important one)
git add custom_components/
git add README.md INSTALLATION.md QUICKSTART.md
git add CHANGELOG.md CONTRIBUTING.md PROJECT_STRUCTURE.md
git add LICENSE hacs.json pyproject.toml requirements.txt
git add .gitignore .github/
git add tests/

# Commit
git commit -m "Initial release v1.0.0

- Modbus TCP support for local communication
- HTTP API fallback
- iSolarCloud cloud API support
- 17+ sensor entities
- Energy Dashboard integration
- Config Flow setup
- Intelligent fallback logic
- Full documentation"

# Add remote (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/sungrow-winet-s.git

# Push
git branch -M main
git push -u origin main
```

## Step 4: Create First Release

1. Go to your repository on GitHub
2. Click "Releases" → "Create a new release"
3. Click "Choose a tag" → Type `v1.0.0` → "Create new tag"
4. Release title: `v1.0.0 - Initial Release`
5. Description:
   ```markdown
   ## Initial Release 🎉
   
   Complete Home Assistant integration for Sungrow inverters via WINET-S.
   
   ### Features
   - ✅ Modbus TCP support (local, fast)
   - ✅ HTTP API fallback (local)
   - ✅ iSolarCloud API (cloud, remote)
   - ✅ 17+ sensor entities
   - ✅ Energy Dashboard compatible
   - ✅ Config Flow UI setup
   - ✅ Intelligent fallback between methods
   
   ### Supported Models
   - SH5K, SH6K, SH8K, SH10RT series
   - Other WINET-S compatible inverters
   
   ### Installation
   See [INSTALLATION.md](INSTALLATION.md) for setup guide.
   
   ### Quick Start
   1. Install via HACS
   2. Add integration
   3. Configure connection (Modbus/HTTP/Cloud)
   4. Enjoy monitoring!
   
   For detailed documentation, see [README.md](README.md)
   ```
6. Click "Publish release"

## Step 5: Submit to HACS

### Option A: HACS Default Repository (Best)

Submit PR to HACS:
1. Fork: https://github.com/hacs/default
2. Edit `custom_components.json`
3. Add entry (alphabetically):
   ```json
   {
     "name": "Sungrow WINET-S Inverter",
     "domains": ["sensor"],
     "iot_class": "Local Polling",
     "render_readme": true
   }
   ```
4. Create PR with title: "Add Sungrow WINET-S Inverter integration"
5. Wait for review (can take weeks)

### Option B: Custom Repository (Immediate)

Users can add manually:
1. HACS → Integrations → ⋮ → Custom repositories
2. URL: `https://github.com/YOUR-USERNAME/sungrow-winet-s`
3. Category: Integration
4. Add

**Document this in your README!**

## Step 6: Configure GitHub Repository Settings

### About Section
- Description: `Home Assistant integration for Sungrow inverters with WINET-S`
- Website: (link to docs if you have them)
- Topics: `home-assistant`, `homeassistant`, `sungrow`, `inverter`, `solar`, `hacs`, `integration`

### Issues
- Enable Issues
- Create issue templates:
  - Bug report
  - Feature request
  - Question

### Discussions (Optional)
- Enable Discussions for Q&A

### Branch Protection (Recommended)
For `main` branch:
- Require PR reviews
- Require status checks (CI)
- No force pushes

## Step 7: CI/CD Setup

The `.github/workflows/ci.yml` will automatically:
- Run on every push/PR
- Check code quality (black, isort, mypy)
- Run tests
- Validate HACS compatibility
- Validate Home Assistant compatibility

**GitHub Actions** should be enabled by default.

## Step 8: Documentation Site (Optional)

Consider creating documentation site:

### GitHub Pages
1. Settings → Pages
2. Source: Deploy from branch → `main` → `/docs`
3. Create `/docs` folder with documentation

### ReadTheDocs
1. Connect GitHub repo
2. Auto-build on commits
3. Better for extensive docs

## Step 9: Community Announcement

Announce on:

1. **Home Assistant Community**
   - Forum: https://community.home-assistant.io/
   - Category: Third party integrations
   - Share link to README

2. **Reddit**
   - r/homeassistant
   - Title: "[Release] Sungrow WINET-S Integration v1.0.0"

3. **Discord**
   - Home Assistant Discord
   - #custom-integrations channel

## Maintenance Plan

### Version Updates

When releasing updates:

1. Update `manifest.json` version
2. Update `CHANGELOG.md`
3. Commit changes
4. Create new GitHub release
5. Tag with version (e.g., `v1.1.0`)

### Handling Issues

- Respond within 48 hours
- Label appropriately (bug, enhancement, question)
- Use issue templates
- Close resolved issues

### Pull Requests

- Review within 1 week
- Run CI checks
- Test locally if possible
- Merge and release

## Repository Quality Badges

Add to README.md:

```markdown
[![GitHub Release](https://img.shields.io/github/release/YOUR-USERNAME/sungrow-winet-s.svg)](https://github.com/YOUR-USERNAME/sungrow-winet-s/releases)
[![GitHub Stars](https://img.shields.io/github/stars/YOUR-USERNAME/sungrow-winet-s.svg)](https://github.com/YOUR-USERNAME/sungrow-winet-s/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/YOUR-USERNAME/sungrow-winet-s.svg)](https://github.com/YOUR-USERNAME/sungrow-winet-s/issues)
[![GitHub License](https://img.shields.io/github/license/YOUR-USERNAME/sungrow-winet-s.svg)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
```

## Marketing Tips

1. **Good README**: Clear, comprehensive, with examples
2. **Screenshots**: Add UI screenshots to README
3. **Video Tutorial**: Create YouTube setup guide
4. **Respond Quickly**: Fast issue/PR responses build trust
5. **Documentation**: Keep docs updated
6. **Changelog**: Always document changes

## Legal

- ✅ MIT License included
- ✅ No proprietary code
- ✅ Credits to Sungrow (not affiliated)
- ✅ Disclaimer included

## Checklist Before Publishing

- [ ] Updated all URLs with your username
- [ ] Tested locally in Home Assistant
- [ ] All tests passing
- [ ] Documentation complete
- [ ] LICENSE file present
- [ ] .gitignore configured
- [ ] CI/CD workflow working
- [ ] HACS files present (hacs.json)
- [ ] Version 1.0.0 set everywhere
- [ ] README badges updated

## Post-Launch

### Week 1
- Monitor issues
- Respond to questions
- Fix critical bugs

### Month 1
- Gather feedback
- Plan v1.1.0 features
- Improve documentation

### Ongoing
- Regular updates
- Community engagement
- Feature additions

## Resources

- [HACS Documentation](https://hacs.xyz/)
- [Home Assistant Dev Docs](https://developers.home-assistant.io/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Good luck with your release! 🚀**
