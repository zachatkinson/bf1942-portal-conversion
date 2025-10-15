# Create Clean Terrain Version (MP_Tungsten_Terrain_Clean)

## Manual Steps in Godot Editor

Since Godot scenes must be created interactively, follow these steps:

### Step 1: Open the Terrain Scene
1. Open Godot project: `GodotProject/`
2. In FileSystem panel, navigate to: `res://static/MP_Tungsten_Terrain.tscn`
3. Double-click to open the scene

### Step 2: Make Instance Editable
1. In Scene tree, select the "Mesh" node (child of MP_Tungsten_Terrain)
2. Right-click → "Editable Children" (or click the chain link icon in toolbar)
3. This allows you to see and edit the GLB's internal structure

### Step 3: Identify and Delete Unwanted Structures
The terrain GLB likely contains nodes like:
- Electric towers/power lines
- Apartment buildings
- Houses
- Industrial structures
- Other map-specific objects

To find them:
1. Expand the "Mesh" node in Scene tree
2. Look for child nodes with names like:
   - `ElectricTower*`
   - `Apartment*`
   - `Building*`
   - `House*`
   - `Industrial*`
   - `PowerLine*`
   - Or any other obvious structure names

3. **Keep these** (terrain elements):
   - Nodes named "Terrain", "Ground", "Landscape"
   - Nodes with "Heightmap" or "Mesh" in the name
   - Natural terrain features (hills, valleys)

4. **Delete these** (built-in structures):
   - Man-made buildings, towers, structures
   - Anything that looks map-specific

### Step 4: Save as Clean Version
1. Scene → Save Scene As
2. Save to: `res://static/MP_Tungsten_Terrain_Clean.tscn`
3. This creates a reusable clean terrain

### Step 5: Update Kursk to Use Clean Terrain
1. Open `res://levels/Kursk.tscn`
2. In Scene tree, select "MP_Tungsten_Terrain" node (under Static)
3. In Inspector, look for the "Scene File Path" property
4. Change from `res://static/MP_Tungsten_Terrain.tscn`
   To: `res://static/MP_Tungsten_Terrain_Clean.tscn`
5. Save the scene

### Step 6: Re-export
1. Use plugin button "Export to Spatial.json"
2. Or run: `python3 tools/export_to_portal.py Kursk`
3. Regenerate experience: `python3 tools/create_multi_map_experience.py ...`

---

## Alternative: Python-Assisted Approach

If you'd like me to help identify what structures are in the terrain, you can:

1. Open the terrain in Godot
2. Make "Mesh" node editable
3. Copy the Scene tree hierarchy (right-click root → Copy Node Path for each child)
4. Send me the list, and I'll help identify what to keep vs delete

---

## Future Automation

Once you have the clean terrain created, I can update the conversion tools to:
- Use `MP_Tungsten_Terrain_Clean.tscn` by default for BF1942 maps
- Add a `--clean-terrain` flag to portal_convert.py
- Update the plugin to offer terrain options

Would you like me to implement these automation updates after you create the clean terrain?
