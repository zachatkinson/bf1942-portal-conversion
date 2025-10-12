# Godot 4 Setup Guide for BF6 Portal SDK

**Date:** 2025-10-11
**Purpose:** Guide for installing Godot 4 and optional MCP integration

---

## Do You Need Godot 4?

**YES** - The BF6 Portal SDK requires Godot 4.x

**Evidence:**
- `GodotProject/project.godot` has `config_version=5` (Godot 4.x format)
- Generated `Kursk.tscn` uses `format=3` (Godot 4 scene format)
- BF6 Portal plugins require Godot 4 features

**Current Status:** Godot is NOT installed on your Mac

---

## Option 1: Install Godot 4 (Required for Phase 4)

### Download Godot 4

**Official Website:** https://godotengine.org/download/macos/

**Recommended Version:** Godot 4.3 or later (Stable)

**⚠️ IMPORTANT: Download the STANDARD version, NOT .NET/Mono**

The Portal SDK uses **GDScript only** (not C#). You do NOT need the .NET version.

**macOS Installation Options:**

1. **Direct Download (.dmg)** ⭐ Recommended
   - Download **Godot 4.3 Standard** (NOT Mono/.NET)
   - Look for: "Godot Engine - Standard version"
   - Avoid: "Godot Engine - .NET version"
   - Open the .dmg file
   - Drag Godot.app to Applications folder

2. **Homebrew** (if you use Homebrew):
   ```bash
   brew install godot
   ```

3. **Steam** (if you prefer):
   - Search for "Godot Engine" on Steam
   - Free download

### First Launch

1. Open Godot 4
2. Click "Import" on the project manager
3. Navigate to `/Users/zach/Downloads/PortalSDK/GodotProject/`
4. Select the `project.godot` file
5. Click "Import & Edit"

**Expected Result:**
- Godot loads the Portal SDK project
- You'll see the BFPortal plugin tabs in the editor
- You can open `levels/Kursk.tscn` in the scene tree

---

## Option 2: Use Godot MCP Server (Enhanced AI Integration)

### What is a Godot MCP?

**MCP (Model Context Protocol)** allows me (Claude) to directly interact with Godot:
- Launch the Godot editor
- Run projects
- Capture debug output
- Create/modify scenes
- Add/edit nodes
- Load sprites

**Benefit:** I can help you test and refine Kursk.tscn interactively without you manually running commands.

### Available Godot MCP Servers

I found 3 active Godot MCP servers:

#### 1. **Coding-Solo/godot-mcp** ⭐ Most Popular
- **Stars:** 964 on GitHub
- **Released:** March 2025
- **Language:** TypeScript
- **Status:** Actively maintained

**Features:**
- Launch Godot editor
- Run projects
- Capture debug output
- Scene management
- UID management (Godot 4.4+)

**GitHub:** https://github.com/Coding-Solo/godot-mcp

#### 2. **bradypp/godot-mcp** ⭐ Comprehensive
- **Features:** Full scene/node manipulation
- **Status:** Active
- **GitHub:** https://github.com/bradypp/godot-mcp

#### 3. **ee0pdt/Godot-MCP** ⭐ Script Integration Focus
- **Features:** Code assistance, scene manipulation
- **GitHub:** https://github.com/ee0pdt/Godot-MCP

### Installing a Godot MCP (Coding-Solo - Recommended)

**Prerequisites:**
- Godot 4 installed (see Option 1)
- Node.js and npm installed

**Installation Steps:**

```bash
# 1. Clone the MCP server
cd ~/Downloads
git clone https://github.com/Coding-Solo/godot-mcp.git
cd godot-mcp

# 2. Install dependencies
npm install

# 3. Build the server
npm run build
```

**Configuration for Claude Desktop (if using Claude Desktop app):**

Add to your Claude Desktop MCP settings:
```json
{
  "mcpServers": {
    "godot": {
      "command": "node",
      "args": [
        "/Users/zach/Downloads/godot-mcp/build/index.js"
      ],
      "env": {
        "GODOT_PATH": "/Applications/Godot.app/Contents/MacOS/Godot"
      }
    }
  }
}
```

**Note:** Claude Code (CLI) support for MCP is currently limited. MCPs work best with:
- Claude Desktop app
- Cline (VS Code extension)
- Cursor IDE

### Using Godot MCP with Claude Code

**Current Limitation:** Claude Code CLI has some MCP support but not full integration like Claude Desktop.

**Workarounds:**
1. Use Claude Desktop for Godot interactions
2. Use Cline in VS Code for AI + Godot integration
3. Continue manual Godot workflow (still very effective!)

---

## Recommended Approach for Phase 4

### Option A: Manual Godot Testing (Simplest)

**Steps:**
1. Install Godot 4 (Option 1 above)
2. Open Portal SDK project
3. Load `levels/Kursk.tscn`
4. Manually verify placements
5. Use BFPortal export panel
6. Share results with me for analysis

**Pros:**
- No additional setup
- Full control
- Official workflow

**Cons:**
- Manual back-and-forth communication
- You need to describe what you see

### Option B: Godot + MCP Integration (Advanced)

**Steps:**
1. Install Godot 4 (Option 1)
2. Install Godot MCP (Option 2)
3. Configure MCP in Claude Desktop
4. Use Claude Desktop for interactive Godot commands

**Pros:**
- I can directly launch Godot
- I can capture debug output
- More interactive workflow

**Cons:**
- Requires Claude Desktop (not Claude Code CLI)
- Additional setup time
- May have compatibility issues

### My Recommendation: **Option A (Manual Testing)**

**Reasoning:**
- You're already familiar with Godot
- Claude Code CLI doesn't fully support MCP yet
- Manual workflow is proven and reliable
- We can iterate based on your observations
- Less setup friction

**How We'd Work:**
1. You: Install Godot 4, open Kursk.tscn
2. You: Share screenshots or describe what you see
3. Me: Analyze issues, suggest fixes
4. You: Test fixes
5. Repeat until satisfied

---

## Phase 4 Checklist (Manual Workflow)

### Before Opening Godot

- [ ] Install Godot 4.3+ for macOS
- [ ] Verify installation: `godot --version` (if added to PATH)

### Opening the Project

- [ ] Launch Godot 4
- [ ] Import project: `/Users/zach/Downloads/PortalSDK/GodotProject/`
- [ ] Wait for initial asset import (may take a few minutes)
- [ ] Check that BFPortal plugin tabs appear

### Loading Kursk

- [ ] Open Scene: `res://levels/Kursk.tscn`
- [ ] Verify scene tree shows:
  - Root node: "Kursk"
  - TEAM_1_HQ with 8 spawn points
  - TEAM_2_HQ with 8 spawn points
  - 4 CapturePoints
  - 18 VehicleSpawners
  - CombatArea
  - Static layer

### Visual Inspection

- [ ] Switch to 3D viewport
- [ ] Check HQ positions (Axis vs Allies separation)
- [ ] Verify vehicle spawner placements
- [ ] Check terrain loads (MP_Outskirts)
- [ ] Inspect combat area boundary (should be visible)

### Testing Spawn Points

- [ ] Select TEAM_1_HQ in scene tree
- [ ] Verify 8 child SpawnPoint nodes
- [ ] Check they're in circular pattern
- [ ] Repeat for TEAM_2_HQ

### Testing Vehicle Spawners

- [ ] Select any VehicleSpawner node
- [ ] Check Inspector panel:
  - Team = 1 or 2
  - ObjId unique
  - VehicleTemplate = valid vehicle name
- [ ] Verify rotation looks reasonable

### Export to .spatial.json

- [ ] Click BFPortal panel tab
- [ ] Click "Export Current Level"
- [ ] Choose output location
- [ ] Verify export completes without errors

### Share Results

- [ ] Take screenshots (3D view, scene tree)
- [ ] Note any warnings or errors
- [ ] Share .spatial.json file (optional)
- [ ] Describe any visual issues

---

## Troubleshooting

### Godot Won't Import Project

**Cause:** Missing or corrupt project.godot

**Fix:**
- Ensure you're selecting `GodotProject/project.godot`
- Not `PortalSDK/project.godot` (doesn't exist)

### Missing Textures/Assets

**Cause:** Asset import not complete

**Fix:**
- Wait for import progress bar to finish
- Check console for import errors
- Re-import if needed: Project → Reimport Assets

### BFPortal Tab Missing

**Cause:** Plugin not loaded

**Fix:**
- Project → Project Settings → Plugins
- Ensure "BF Portal" is enabled
- Restart Godot if needed

### Kursk.tscn Shows Errors

**Cause:** Missing external resources

**Fix:**
- Check that these exist:
  - `res://objects/HQ_PlayerSpawner.tscn`
  - `res://objects/VehicleSpawner.tscn`
  - `res://objects/CapturePoint.tscn`
  - `res://static/MP_Outskirts_Terrain.tscn`

### Terrain Not Visible

**Cause:** Large terrain mesh, slow loading

**Fix:**
- Wait for scene to fully load
- Check 3D viewport camera position
- Try View → Frame Selection (F key)

---

## Quick Command Reference

### Godot Installation Check

```bash
# Check if Godot is installed
which godot

# Check Godot version (if in PATH)
godot --version

# Expected: Godot Engine v4.3.x or later
```

### Open Project from Terminal

```bash
# If Godot is in PATH
godot /Users/zach/Downloads/PortalSDK/GodotProject/project.godot

# If using macOS .app bundle
/Applications/Godot.app/Contents/MacOS/Godot /Users/zach/Downloads/PortalSDK/GodotProject/project.godot
```

### Godot MCP Commands (if installed)

These work if you've set up a Godot MCP in Claude Desktop:

- "Launch Godot editor for my project"
- "Run Kursk.tscn and show any errors"
- "List all nodes in Kursk.tscn"
- "Capture debug output from Godot"

---

## Next Steps After Godot Setup

Once Godot is installed and working:

1. **Visual Verification**
   - Open Kursk.tscn
   - Check object placements match expected positions
   - Verify terrain loads correctly

2. **Identify Issues**
   - Note any Y-coordinate mismatches (elevation)
   - Check for missing assets
   - Look for rotation oddities

3. **Manual Refinements** (optional)
   - Adjust spawn point positions if needed
   - Add decorative props from unrestricted assets
   - Fine-tune capture point radii

4. **Export Testing**
   - Export to .spatial.json
   - Verify JSON structure
   - Check for export warnings

5. **Report Back**
   - Share findings with me
   - I can generate fixes if needed
   - Iterate until satisfied

---

## Summary

**To Answer Your Questions:**

1. **Do you need to install Godot 4?**
   - **YES** - Required for Phase 4 testing
   - Portal SDK needs Godot 4.x

2. **Is there a Godot MCP we can use?**
   - **YES** - 3 available Godot MCPs
   - **HOWEVER** - Claude Code CLI has limited MCP support
   - **BEST WITH** - Claude Desktop or Cline

3. **My Recommendation:**
   - Install Godot 4 (required)
   - Skip MCP for now (optional, better with Claude Desktop)
   - Use manual testing workflow (proven, effective)
   - We can iterate based on your observations

**Time Estimate:**
- Godot 4 installation: 5-10 minutes
- First project open: 5 minutes (asset import)
- Initial Kursk.tscn inspection: 10-15 minutes
- Total: ~30 minutes to get started with Phase 4

---

*Last Updated:* 2025-10-11
*For:* Phase 4 - Godot Testing
*Project:* BF1942 → BF6 Portal Conversion
