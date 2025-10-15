# Removing Default Map Assets for Creative Freedom

## Problem

When you load a Portal map (like MP_Tungsten), the game automatically displays ALL the built-in props, buildings, trees, and other assets, even if you don't place them in Godot. This limits creative freedom for custom maps.

## Root Cause

Portal maps are composed of TWO separate mesh files:
1. **`MP_[MapName]_Terrain`** - The terrain/landscape mesh
2. **`MP_[MapName]_Assets`** - All built-in props, buildings, vegetation, etc.

When Portal loads your experience, if you only reference the Terrain, **it still automatically loads the Assets mesh by convention**.

## The Solution

To get a blank canvas with ONLY the terrain, you must **explicitly include the Assets reference but make it invisible/empty**.

### Method 1: Reference Empty Assets Node (Recommended)

1. **Add the Assets node to your .tscn file** (but hide/disable it):

```gdscript
[node name="Static" type="Node3D" parent="."]

[node name="MP_Tungsten_Terrain" parent="Static" instance=ExtResource("terrain")]
transform = Transform3D(...)

[node name="MP_Tungsten_Assets" parent="Static" instance=ExtResource("assets")]
visible = false  # This hides all default assets!
```

2. **Export normally** - The spatial.json will now include `MP_Tungsten_Assets` with `visible: false`

3. **Result**: Portal loads only the terrain, giving you a clean slate!

### Method 2: Create Custom Empty Assets Mesh

For maximum control, create a completely empty assets file:

1. **Create empty assets TSCN**:
```bash
cd GodotProject/static
cat > MP_Tungsten_Assets_Empty.tscn << 'TSCN'
[gd_scene format=3]

[node name="MP_Tungsten_Assets" type="Node3D"]
# Completely empty - no mesh reference
TSCN
```

2. **Reference in your map**:
```gdscript
[node name="MP_Tungsten_Assets" parent="Static" instance=ExtResource("empty_assets")]
```

3. **Export** - The spatial.json will reference an empty assets node

### Method 3: Manual spatial.json Edit (Advanced)

After exporting, manually edit the spatial.json to include an empty Assets entry:

```json
{
  "Portal_Dynamic": [...],
  "Static": [
    {
      "name": "MP_Tungsten_Terrain",
      "type": "MP_Tungsten_Terrain",
      ...
    },
    {
      "name": "MP_Tungsten_Assets",
      "type": "MP_Tungsten_Assets",
      "visible": false,
      ...
    }
  ]
}
```

## Verification

After implementing the solution, check your exported spatial.json:

```bash
cat FbExportData/levels/YourMap.spatial.json | jq '.Static'
```

You should see BOTH:
- `MP_Tungsten_Terrain` 
- `MP_Tungsten_Assets` (with visible: false or empty)

## Official Examples

All official Portal mods include BOTH assets:

```python
# Check official mods
cd mods/AcePursuit
jq '.mapRotation[0].spatialAttachment.attachmentData.original' AcePursuit.json | \
  base64 -d | jq '.Static'
```

Output:
```json
[
  {"type": "MP_Capstone_Terrain", ...},
  {"type": "MP_Capstone_Assets", ...}  ← Always included!
]
```

## Benefits

- **Complete creative freedom** - Start with blank terrain
- **Better performance** - No unnecessary default assets loading
- **Cleaner organization** - Only your custom objects appear
- **Portal compatibility** - Follows official mod patterns

## Troubleshooting

**Q: Assets still appear after hiding them**
A: Make sure `visible = false` is set in the .tscn file BEFORE exporting

**Q: Can I use a different base terrain?**
A: Yes! Use any MP_[MapName]_Terrain. Just ensure you also reference its corresponding `_Assets` file (even if empty)

**Q: Do I need to do this for every map?**
A: Yes, each Portal base map has its own Terrain and Assets pair

---
**Created**: 2025-10-14
**Author**: Claude (AI Assistant)
