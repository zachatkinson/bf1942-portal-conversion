#!/usr/bin/env python3
"""Validation error message constants.

Single Responsibility: Define standardized validation error messages.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-13
"""

# ==============================================================================
# Validation Messages
# ==============================================================================

ERROR_MISSING_TEAM1_HQ = "Missing Team 1 HQ"
ERROR_MISSING_TEAM2_HQ = "Missing Team 2 HQ"
ERROR_INSUFFICIENT_TEAM1_SPAWNS = "Team 1 needs at least {min} spawns, got {actual}"
ERROR_INSUFFICIENT_TEAM2_SPAWNS = "Team 2 needs at least {min} spawns, got {actual}"
ERROR_FILE_NOT_FOUND = "File not found: {path}"
