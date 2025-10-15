/**
 * Capture Point Label Template
 *
 * This TypeScript code sets up WorldIcon labels for capture points (A, B, C, etc.).
 * Copy this code into your Portal experience TypeScript editor.
 *
 * Background:
 * - CapturePoint nodes in Portal SDK do NOT have a Label property
 * - Labels must be set via WorldIcon nodes using TypeScript
 * - This pattern is from the official BombSquad example mod
 *
 * Usage:
 * 1. Ensure your .tscn file has WorldIcon nodes as children of each CapturePoint
 * 2. WorldIcons should have ObjIds starting at 20 (20, 21, 22, etc.)
 * 3. Copy this code into your Portal web editor TypeScript section
 * 4. Adjust NUM_CAPTURE_POINTS to match your map (Kursk = 2)
 */

import * as mod from 'bf2042-portal-extensions';

// ==============================================================================
// CONFIGURATION - Adjust for your map
// ==============================================================================

const NUM_CAPTURE_POINTS = 2;  // Change this to match your map's CP count
const WORLD_ICON_OBJID_START = 20;  // First WorldIcon ObjId (Portal convention)

// ==============================================================================
// Capture Point Label Setup
// ==============================================================================

/**
 * Initialize capture point labels when the game starts.
 *
 * This function:
 * - Gets WorldIcon references by ObjId (20, 21, 22...)
 * - Sets text labels (A, B, C...)
 * - Enables text visibility
 * - Disables icon images (labels only)
 */
export function OnGameModeStarted(): void {
    // Generate labels A, B, C, D, etc.
    const labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];

    for (let i = 0; i < NUM_CAPTURE_POINTS; i++) {
        const objId = WORLD_ICON_OBJID_START + i;
        const label = labels[i];

        // Get WorldIcon by ObjId
        const worldIcon = mod.GetWorldIcon(objId);

        if (worldIcon) {
            // Set label text
            mod.SetWorldIconText(worldIcon, mod.Message(label));

            // Enable text visibility
            mod.EnableWorldIconText(worldIcon, true);

            // Disable image (we only want text labels)
            mod.EnableWorldIconImage(worldIcon, false);

            console.log(`✅ Capture Point ${label} label set (ObjId: ${objId})`);
        } else {
            console.error(`❌ WorldIcon not found for CP ${label} (ObjId: ${objId})`);
        }
    }
}

// ==============================================================================
// OPTIONAL: Advanced Label Customization
// ==============================================================================

/**
 * Alternative: Use custom label names instead of A, B, C
 *
 * Example:
 *   setCustomCapturePointLabels(['North Base', 'Central Hill', 'South Village']);
 */
export function setCustomCapturePointLabels(customLabels: string[]): void {
    for (let i = 0; i < customLabels.length && i < NUM_CAPTURE_POINTS; i++) {
        const objId = WORLD_ICON_OBJID_START + i;
        const label = customLabels[i];

        const worldIcon = mod.GetWorldIcon(objId);
        if (worldIcon) {
            mod.SetWorldIconText(worldIcon, mod.Message(label));
            mod.EnableWorldIconText(worldIcon, true);
            mod.EnableWorldIconImage(worldIcon, false);
        }
    }
}

/**
 * Alternative: Show CP labels with custom colors
 *
 * Colors: RGB values from 0.0 to 1.0
 * Example: Red = (1.0, 0.0, 0.0), Green = (0.0, 1.0, 0.0), Blue = (0.0, 0.0, 1.0)
 */
export function setCapturePointLabelColor(cpIndex: number, r: number, g: number, b: number): void {
    const objId = WORLD_ICON_OBJID_START + cpIndex;
    const worldIcon = mod.GetWorldIcon(objId);

    if (worldIcon) {
        mod.SetWorldIconColor(worldIcon, mod.Vector(r, g, b));
    }
}

// ==============================================================================
// TROUBLESHOOTING
// ==============================================================================

/**
 * Debug function to list all WorldIcons in the scene.
 * Call this if labels aren't showing up.
 */
export function debugWorldIcons(): void {
    console.log('=== WorldIcon Debug Info ===');

    for (let i = 0; i < NUM_CAPTURE_POINTS; i++) {
        const objId = WORLD_ICON_OBJID_START + i;
        const worldIcon = mod.GetWorldIcon(objId);

        if (worldIcon) {
            console.log(`✅ WorldIcon ${objId}: EXISTS`);
        } else {
            console.error(`❌ WorldIcon ${objId}: NOT FOUND`);
        }
    }

    console.log('=========================');
}

// ==============================================================================
// EXAMPLE: Complete Kursk Experience
// ==============================================================================

/**
 * For Kursk (2 capture points):
 *
 * export function OnGameModeStarted(): void {
 *     // Set CP labels A and B
 *     const labelA = mod.GetWorldIcon(20);
 *     const labelB = mod.GetWorldIcon(21);
 *
 *     if (labelA) {
 *         mod.SetWorldIconText(labelA, mod.Message('A'));
 *         mod.EnableWorldIconText(labelA, true);
 *         mod.EnableWorldIconImage(labelA, false);
 *     }
 *
 *     if (labelB) {
 *         mod.SetWorldIconText(labelB, mod.Message('B'));
 *         mod.EnableWorldIconText(labelB, true);
 *         mod.EnableWorldIconImage(labelB, false);
 *     }
 * }
 */
