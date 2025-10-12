#!/usr/bin/env python3
"""
Portal experience file builder utilities.

This module provides shared utilities for creating Portal experience files
with proper structure to ensure map rotation appears pre-populated in the
Portal web builder UI.
"""

from typing import Any


def create_spatial_attachment(
    map_id: str,
    map_name: str,
    spatial_base64: str,
    map_index: int = 0,
) -> dict[str, Any]:
    """
    Create a spatial attachment structure for Portal experiences.

    Portal requires spatial attachments to exist in TWO locations:
    1. Nested inside mapRotation entries (mapRotation[].spatialAttachment)
    2. In the root-level attachments array (attachments[])

    Without both, the map rotation UI appears empty after import.

    Args:
        map_id: Unique identifier for the map (e.g., "kursk")
        map_name: Display name for the map (e.g., "Kursk")
        spatial_base64: Base64-encoded spatial.json data
        map_index: Index of map in rotation (default: 0)

    Returns:
        Spatial attachment dictionary ready for use in both locations

    Example:
        >>> spatial_base64 = base64.b64encode(spatial_json.encode()).decode()
        >>> attachment = create_spatial_attachment(
        ...     map_id="kursk",
        ...     map_name="Kursk",
        ...     spatial_base64=spatial_base64,
        ...     map_index=0
        ... )
        >>> experience = {
        ...     "mapRotation": [{
        ...         "id": "MP_Tungsten-ModBuilderCustom0",
        ...         "spatialAttachment": attachment
        ...     }],
        ...     "attachments": [attachment]  # Same object in both places
        ... }
    """
    return {
        "id": f"{map_id}-bf1942-spatial",
        "filename": f"{map_name}.spatial.json",
        "metadata": f"mapIdx={map_index}",
        "version": "123",  # Portal expects "123" - this is the Portal SDK version format
        "isProcessable": True,
        "processingStatus": 2,  # 2 = processed/ready
        "attachmentData": {
            "original": spatial_base64,
            "compiled": "",  # Empty - Portal compiles server-side
        },
        "attachmentType": 1,  # 1 = spatial attachment
        "errors": [],
    }
