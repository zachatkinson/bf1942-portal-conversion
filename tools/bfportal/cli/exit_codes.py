#!/usr/bin/env python3
"""Exit code constants for CLI tools.

Single Responsibility: Define standard exit codes for all CLI scripts.
Follows SOLID/DRY principles by centralizing exit code definitions.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-17
"""

# ==============================================================================
# Standard Exit Codes
# ==============================================================================

EXIT_SUCCESS = 0  # Command completed successfully
EXIT_ERROR = 1  # Generic error occurred
EXIT_FILE_NOT_FOUND = 2  # Required file not found
EXIT_VALIDATION_ERROR = 3  # Validation failed
EXIT_PARSE_ERROR = 4  # Parsing failed
EXIT_CONVERSION_ERROR = 5  # Conversion failed
EXIT_EXPORT_ERROR = 6  # Export failed
EXIT_INVALID_ARGS = 7  # Invalid command-line arguments
EXIT_TERRAIN_ERROR = 8  # Terrain processing error
EXIT_ASSET_ERROR = 9  # Asset mapping error
