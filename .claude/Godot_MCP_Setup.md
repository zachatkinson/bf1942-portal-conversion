# Godot MCP Setup for Claude Code CLI

**Date:** 2025-10-11
**Purpose:** Enable Claude Code CLI to interact directly with Godot Engine

---

## Overview

**What This Enables:**

With Godot MCP installed, I (Claude) can:
- ✅ Launch Godot editor for your project
- ✅ Run Godot projects and capture output
- ✅ Get debug logs in real-time
- ✅ List project files and scenes
- ✅ Analyze scene structure
- ✅ Control Godot execution (start/stop)

**Benefit for Phase 4:**
- I can launch Godot with Kursk.tscn for you
- I can capture any errors or warnings
- Interactive testing workflow instead of manual back-and-forth

---

## Prerequisites

Before starting, ensure you have:

- [ ] **Godot 4 Standard installed** (see Godot_Setup_Guide.md)
- [ ] **Node.js and npm installed**
- [ ] **Claude Code CLI** (you're already using this!)

### Check Prerequisites

```bash
# Check Node.js (need v16+)
node --version

# Check npm
npm --version

# Check Godot (if in PATH)
godot --version

# Check Claude Code
claude --version
```

**If Node.js is missing:**
```bash
# Install via Homebrew
brew install node

# Or download from: https://nodejs.org/
```

---

## Installation Steps

### Step 1: Clone and Build Godot MCP

```bash
# Navigate to a good location (e.g., your Downloads or a tools directory)
cd ~/Downloads

# Clone the Godot MCP server
git clone https://github.com/Coding-Solo/godot-mcp.git
cd godot-mcp

# Install dependencies
npm install

# Build the server
npm run build
```

**Expected output:**
```
✓ Built successfully
build/index.js created
```

### Step 2: Configure for Claude Code CLI

**Add the MCP server using the `claude mcp add` command:**

```bash
# Basic configuration
claude mcp add --transport stdio godot \
  --env GODOT_PATH=/Applications/Godot.app/Contents/MacOS/Godot \
  -- node ~/Downloads/godot-mcp/build/index.js

# With debug logging enabled
claude mcp add --transport stdio godot \
  --env GODOT_PATH=/Applications/Godot.app/Contents/MacOS/Godot \
  --env DEBUG=true \
  -- node ~/Downloads/godot-mcp/build/index.js
```

**Important Notes:**
- Replace `~/Downloads/godot-mcp` with your actual path if you cloned elsewhere
- Use `--` to separate Claude CLI flags from the server command
- The `GODOT_PATH` should point to your Godot executable

**Alternative: If Godot is in your PATH:**
```bash
claude mcp add --transport stdio godot \
  -- node ~/Downloads/godot-mcp/build/index.js
```

### Step 3: Verify Installation

```bash
# List configured MCP servers
claude mcp list

# Should show:
# godot - stdio - node ~/Downloads/godot-mcp/build/index.js
```

**In Claude Code session:**
```
/mcp
```

This command shows the status of all MCP servers. You should see `godot` listed.

---

## Usage in Claude Code

Once installed, you can ask me to do things like:

### Launch Godot Editor

**You say:**
> "Launch Godot with the Portal SDK project"

**I can execute:**
- Open Godot editor
- Load the PortalSDK project
- Open Kursk.tscn automatically

### Run and Capture Output

**You say:**
> "Run Kursk.tscn and show me any errors"

**I can:**
- Launch Godot with Kursk scene
- Capture console output
- Report any warnings or errors
- Show debug logs

### Analyze Scene

**You say:**
> "List all nodes in Kursk.tscn"

**I can:**
- Query the scene structure
- Show the node hierarchy
- Report node properties

### Interactive Testing

**You say:**
> "Check if the HQs are positioned correctly"

**I can:**
- Load the scene
- Inspect HQ node positions
- Compare with expected coordinates
- Report any discrepancies

---

## Available MCP Tools

The Godot MCP provides these tools (once configured):

### Core Tools

```
launch_editor        - Launch Godot editor
run_project         - Run a Godot project
get_project_info    - Get information about the project
list_scenes         - List all scene files
get_scene_info      - Get information about a specific scene
```

### Advanced Tools (Godot 4.4+ with UID support)

```
get_resource_by_uid - Get resource information by UID
list_resources      - List all resources in project
```

---

## Configuration Options

### Environment Variables

**GODOT_PATH** (Required if Godot not in PATH)
```bash
--env GODOT_PATH=/Applications/Godot.app/Contents/MacOS/Godot
```

**DEBUG** (Optional - Enable verbose logging)
```bash
--env DEBUG=true
```

**PROJECT_PATH** (Optional - Default project location)
```bash
--env PROJECT_PATH=/Users/zach/Downloads/PortalSDK/GodotProject
```

### Scope Options

```bash
# User scope (available in all projects)
claude mcp add --scope user --transport stdio godot ...

# Project scope (only this project)
claude mcp add --scope project --transport stdio godot ...

# Local scope (default - current directory)
claude mcp add --transport stdio godot ...
```

**Recommended:** Use `--scope user` so Godot MCP is available everywhere.

---

## Troubleshooting

### "MCP server not found"

**Cause:** Server not configured or wrong scope

**Fix:**
```bash
# Check if server exists
claude mcp list

# If missing, add it again
claude mcp add --scope user --transport stdio godot \
  --env GODOT_PATH=/Applications/Godot.app/Contents/MacOS/Godot \
  -- node ~/Downloads/godot-mcp/build/index.js
```

### "Godot executable not found"

**Cause:** `GODOT_PATH` incorrect or Godot not installed

**Fix:**
```bash
# Find Godot location
which godot

# Or if using .app bundle
ls /Applications/Godot.app/Contents/MacOS/Godot

# Update GODOT_PATH when adding server
claude mcp add --transport stdio godot \
  --env GODOT_PATH=/correct/path/to/Godot \
  -- node ~/Downloads/godot-mcp/build/index.js
```

### "Node.js version too old"

**Cause:** Need Node.js v16+

**Fix:**
```bash
# Update Node.js
brew upgrade node

# Or install from nodejs.org
```

### "Permission denied"

**Cause:** Build directory not executable or wrong permissions

**Fix:**
```bash
cd ~/Downloads/godot-mcp
chmod +x build/index.js
npm run build
```

### MCP Server Crashes

**Cause:** Various (project path wrong, Godot not responding, etc.)

**Debug:**
```bash
# Test server manually
node ~/Downloads/godot-mcp/build/index.js

# Check logs with DEBUG enabled
claude mcp remove godot
claude mcp add --transport stdio godot \
  --env DEBUG=true \
  --env GODOT_PATH=/Applications/Godot.app/Contents/MacOS/Godot \
  -- node ~/Downloads/godot-mcp/build/index.js
```

---

## Testing the Setup

### Quick Test

Once configured, test in a Claude Code session:

1. **Check MCP status:**
   ```
   /mcp
   ```
   Should show `godot` server connected.

2. **Ask me to interact with Godot:**
   > "Can you launch Godot editor for the Portal SDK?"

3. **I should be able to:**
   - Execute the MCP tool
   - Launch Godot
   - Report success or any errors

### Full Integration Test

**Test workflow:**
1. You: "Launch Godot with PortalSDK and open Kursk.tscn"
2. Me: Uses MCP to launch Godot, open project, load scene
3. You: Observe Godot window opens with Kursk
4. You: "Capture any console output from Godot"
5. Me: Uses MCP to get console logs, reports findings

---

## Comparison: Manual vs MCP Workflow

### Manual Workflow (No MCP)

**Phase 4 testing:**
1. You: Manually open Godot
2. You: Import PortalSDK project
3. You: Open Kursk.tscn
4. You: Check for issues
5. You: Describe issues to me
6. Me: Suggest fixes
7. You: Test fixes
8. Repeat

**Pros:**
- Simple, no setup
- Full visual control

**Cons:**
- Manual back-and-forth
- Slower iteration
- I rely on your descriptions

### MCP Workflow (With Godot MCP)

**Phase 4 testing:**
1. You: "Test Kursk.tscn in Godot"
2. Me: Launch Godot, open scene, capture logs
3. Me: Report findings automatically
4. You: Review my analysis
5. Me: Suggest and test fixes directly
6. Iterate rapidly

**Pros:**
- Faster iteration
- I see actual output
- More interactive
- Less manual work for you

**Cons:**
- Initial setup time (~15 min)
- Requires Node.js
- Another dependency

---

## My Recommendation

### For Phase 4 Only: **Skip MCP** ⭐

**Reasoning:**
- Phase 4 is one-time testing
- Manual workflow is proven
- ~15 min setup not worth it for single use
- You'll need to visually inspect anyway

**Better Use Case for MCP:**
- Multiple map conversions (El Alamein, Wake Island, etc.)
- Ongoing development
- Frequent Godot testing
- If you're already comfortable with MCPs

### For Future Maps: **Consider MCP**

If you plan to convert more BF1942 maps, MCP becomes valuable:
- Automate testing across multiple maps
- Faster iteration cycles
- I can help debug issues directly
- Worth the one-time setup

---

## Quick Setup Commands (Copy-Paste Ready)

**Full installation in one go:**

```bash
# 1. Install Node.js (if needed)
brew install node

# 2. Clone and build Godot MCP
cd ~/Downloads
git clone https://github.com/Coding-Solo/godot-mcp.git
cd godot-mcp
npm install
npm run build

# 3. Add to Claude Code CLI
claude mcp add --scope user --transport stdio godot \
  --env GODOT_PATH=/Applications/Godot.app/Contents/MacOS/Godot \
  --env PROJECT_PATH=/Users/zach/Downloads/PortalSDK/GodotProject \
  -- node ~/Downloads/godot-mcp/build/index.js

# 4. Verify
claude mcp list
```

**Test in Claude Code:**
```
/mcp
```

Then ask me: "Launch Godot for the Portal SDK project"

---

## Removing Godot MCP

If you want to remove it later:

```bash
# Remove the MCP server
claude mcp remove godot

# Verify removal
claude mcp list

# Optionally delete the cloned repo
rm -rf ~/Downloads/godot-mcp
```

---

## Summary

**To Answer Your Question:**

**YES** - We CAN set up Godot MCP for Claude Code CLI!

**How:**
1. Install Node.js (if needed)
2. Clone and build Godot MCP
3. Add to Claude Code with `claude mcp add`
4. I can then interact with Godot directly

**Should You?**

**For Phase 4 only:** Probably not worth it (manual is fine)
**For multiple maps:** Yes, definitely worth it!

**Time Investment:**
- Setup: ~15 minutes
- Learning: ~5 minutes
- **Total: 20 minutes**

**Your Decision:**
- Want to try MCP? → Follow the quick setup commands above
- Prefer manual? → Skip it, use manual workflow (totally fine!)

Either way works for Phase 4. The choice is yours!

---

*Last Updated:* 2025-10-11
*For:* Optional MCP Integration
*Project:* BF1942 → BF6 Portal Conversion
