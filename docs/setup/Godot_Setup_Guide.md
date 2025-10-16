# Godot 4 Setup Guide for BF6 Portal SDK

> Multi-platform guide for installing Godot 4 and opening Portal SDK projects for map development

**Last Updated:** October 2025

---

## Platform-Specific Guides

This project provides detailed, platform-specific installation guides for the best experience:

### 📘 [macOS Setup Guide](./Godot_Setup_Guide_macOS.md)

Complete installation and configuration guide for macOS users, including:
- Direct download, Homebrew, and Steam installation options
- Gatekeeper bypass instructions
- macOS-specific troubleshooting (quarantine flags, permissions, Metal rendering)
- Trackpad navigation shortcuts
- Performance optimization for Retina displays

**→ [View macOS Guide](./Godot_Setup_Guide_macOS.md)**

---

### 📗 [Windows Setup Guide](./Godot_Setup_Guide_Windows.md)

Complete installation and configuration guide for Windows users, including:
- Direct download, Steam, and Scoop package manager options
- Windows Defender SmartScreen workarounds
- DirectX 12 optimization
- Windows-specific troubleshooting
- PowerShell validation commands

**→ [View Windows Guide](./Godot_Setup_Guide_Windows.md)**

---

### 📙 Linux Setup Guide

*Coming soon - For now, see the [Godot Linux Download Page](https://godotengine.org/download/linux/)*

Basic installation:
```bash
# Flatpak
flatpak install flathub org.godotengine.Godot

# Snap
snap install godot-4

# Manual Download
wget https://downloads.tuxfamily.org/godotengine/4.3/Godot_v4.3_linux.x86_64.zip
unzip Godot_v4.3_linux.x86_64.zip
chmod +x Godot_v4.3_linux.x86_64
./Godot_v4.3_linux.x86_64
```

---

## Quick Reference

### Key Requirements (All Platforms)

- **Godot Version:** 4.3+ (Standard edition, NOT .NET/Mono)
- **Why Standard?** Portal SDK uses GDScript only (not C#)
- **Project Location:** `PortalSDK/GodotProject/project.godot`

### Universal First Steps

1. Install Godot 4.3+ Standard (see platform guide above)
2. Launch Godot → Import → Navigate to `PortalSDK/GodotProject/`
3. Select `project.godot` → Import & Edit
4. Wait for initial asset import (2-5 minutes)
5. Verify BFPortal tab appears in editor

---

## Additional Resources

- **Godot Documentation**: https://docs.godotengine.org/en/stable/
- **Portal SDK Docs**: [README.html](../../README.html)
- **Conversion Tools**: [docs/architecture/](../architecture/)
- **Testing Guide**: [Testing_Guide.md](../../Testing_Guide.md)

---

**Platform Support:** Windows, macOS, Linux
**Godot Version:** 4.3+
**SDK Compatibility:** BF6 Portal SDK (2025)

**See Also:**
- [Main README](../../README.md) - Project overview
- [Testing_Guide.md](../../Testing_Guide.md) - Testing procedures
