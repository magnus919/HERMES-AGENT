---
name: clawhub-skill-install
description: Install skills from ClawHub (clawhub.ai). Use when user asks to install a skill from clawhub or provides a clawhub.ai URL.
tags: [clawhub, skills, installation]
author: hermes
---

# Install Skills from ClawHub

ClawHub (clawhub.ai) is a registry for Claude Code/Agent skills. This skill covers the installation process.

## Installation Process

### Step 1: Download the skill ZIP
```bash
curl -sL "https://wry-manatee-359.convex.site/api/v1/download?slug=<SLUG>" -o /tmp/skill.zip
```
Where `<SLUG>` is the skill identifier from the clawhub URL.

Example URLs:
- `https://clawhub.ai/steipete/gog` → slug = `gog`
- `https://clawhub.ai/jx-76/jx76-gog` → slug = `jx76-gog`
- `https://clawhub.ai/dilomcfly/n8n-automation` → slug = `n8n-automation`

### Step 2: Extract and install
```bash
cd /tmp && unzip -o skill.zip -d skill_extract
mkdir -p ~/.hermes/skills/<skill-name>
cp -r skill_extract/* ~/.hermes/skills/<skill-name>/
```

### Step 3: Install binary dependencies (if any)
Check the SKILL.md for required binaries. Common install methods:
```bash
# via npm
npm install -g <package>

# via brew
brew install <formula>

# via direct download
curl -sL "<download-url>" -o /tmp/bin && chmod +x /tmp/bin && sudo mv /tmp/bin /usr/local/bin/
```

## ClawHub Skill Structure
A clawhub skill ZIP typically contains:
- `SKILL.md` - Main skill file with frontmatter
- `_meta.json` - Skill metadata
- `references/` - Additional documentation
- Other supporting files

## Notes
- Skills go in `~/.hermes/skills/<skill-name>/`
- After installing, the skill is available immediately (no restart needed)
- Some skills require additional setup (OAuth credentials, API keys, etc.) - check SKILL.md
