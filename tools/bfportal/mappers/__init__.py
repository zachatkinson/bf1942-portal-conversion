"""Mapper modules for BF1942 to Portal conversion.

This package contains mapping systems that convert BF1942 data to Portal equivalents:
- Vehicle type mappings (BF1942 vehicles → BF6 VehicleType enum)
- Asset mappings (BF1942 objects → Portal assets)
- Team mappings (BF1942 teams → Portal team IDs)
"""

from .vehicle_mapper import VehicleMapper, VehicleMapping

__all__ = ["VehicleMapper", "VehicleMapping"]
