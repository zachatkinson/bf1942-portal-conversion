"""Portal asset indexer - creates searchable indexes from Portal SDK assets.

This module follows SOLID principles:
- Single Responsibility: Each class handles one aspect of indexing
- Open/Closed: Extend with new index types without modifying existing code
- Liskov Substitution: Index strategies are interchangeable
- Interface Segregation: Separate interfaces for reading, indexing, writing
- Dependency Inversion: Depends on abstractions (protocols), not concrete types
"""

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

# ============================================================================
# Domain Models (Value Objects)
# ============================================================================


@dataclass(frozen=True)
class PortalAsset:
    """Immutable Portal asset representation.

    Value object pattern - represents an asset from Portal SDK.
    """

    asset_type: str
    directory: str
    category: str
    level_restrictions: list[str]
    physics_cost: int
    mesh: str | None = None

    @property
    def is_unrestricted(self) -> bool:
        """Check if asset is available on all maps."""
        return len(self.level_restrictions) == 0

    @property
    def primary_category(self) -> str:
        """Get primary category from directory path."""
        return self.directory.split("/")[0] if "/" in self.directory else self.directory


@dataclass(frozen=True)
class IndexMetadata:
    """Metadata about the generated index."""

    source_file: str
    total_assets: int
    generated_date: str
    categories: dict[str, int]
    unrestricted_count: int


# ============================================================================
# Protocols (Interfaces)
# ============================================================================


class AssetReader(Protocol):
    """Protocol for reading Portal assets from a source."""

    def read(self) -> list[PortalAsset]:
        """Read and parse Portal assets from source."""
        ...


class AssetIndexer(Protocol):
    """Protocol for indexing assets by different criteria."""

    def index(self, assets: list[PortalAsset]) -> dict[str, Any]:
        """Create an index structure from assets."""
        ...


class IndexWriter(Protocol):
    """Protocol for writing index data to output."""

    def write(self, index_data: dict[str, Any]) -> None:
        """Write index data to output destination."""
        ...


# ============================================================================
# Asset Reader Implementation
# ============================================================================


class PortalSDKAssetReader:
    """Reads Portal assets from Portal SDK asset_types.json file.

    Single Responsibility: Parse Portal SDK format only.
    """

    def __init__(self, asset_types_path: Path) -> None:
        self.asset_types_path = asset_types_path

    def read(self) -> list[PortalAsset]:
        """Read and parse Portal assets from asset_types.json.

        Returns:
            List of parsed PortalAsset objects

        Raises:
            FileNotFoundError: If asset_types.json doesn't exist
            json.JSONDecodeError: If file is not valid JSON
        """
        if not self.asset_types_path.exists():
            raise FileNotFoundError(f"Portal SDK asset file not found: {self.asset_types_path}")

        with open(self.asset_types_path, encoding="utf-8") as f:
            data = json.load(f)

        asset_list = data.get("AssetTypes", [])
        return [self._parse_asset(asset_data) for asset_data in asset_list]

    def _parse_asset(self, asset_data: dict[str, Any]) -> PortalAsset:
        """Parse a single asset from Portal SDK format."""
        # Extract constants as a lookup dict
        constants = {const["name"]: const["value"] for const in asset_data.get("constants", [])}

        return PortalAsset(
            asset_type=asset_data.get("type", ""),
            directory=asset_data.get("directory", "Uncategorized"),
            category=constants.get("category", "unknown"),
            level_restrictions=asset_data.get("levelRestrictions", []),
            physics_cost=constants.get("physicsCost", 0),
            mesh=constants.get("mesh"),
        )


# ============================================================================
# Asset Indexer Implementations (Strategy Pattern)
# ============================================================================


class CategoryIndexer:
    """Index assets by primary category.

    Single Responsibility: Category-based indexing only.
    """

    def index(self, assets: list[PortalAsset]) -> dict[str, list[dict[str, Any]]]:
        """Create category-based index.

        Returns:
            Dict mapping category names to lists of asset data
        """
        by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for asset in assets:
            by_category[asset.primary_category].append(
                {
                    "type": asset.asset_type,
                    "directory": asset.directory,
                    "category": asset.category,
                    "unrestricted": asset.is_unrestricted,
                    "level_restrictions": asset.level_restrictions,
                    "physics_cost": asset.physics_cost,
                }
            )

        # Sort assets within each category by type name
        for category in by_category:
            by_category[category].sort(key=lambda x: x["type"])

        return dict(by_category)


class AvailabilityIndexer:
    """Index assets by map availability.

    Single Responsibility: Availability-based indexing only.
    """

    def index(self, assets: list[PortalAsset]) -> dict[str, list[str]]:
        """Create availability-based index.

        Returns:
            Dict mapping 'unrestricted' and map names to lists of asset types
        """
        by_availability: dict[str, list[str]] = defaultdict(list)

        for asset in assets:
            if asset.is_unrestricted:
                by_availability["unrestricted"].append(asset.asset_type)
            else:
                for map_name in asset.level_restrictions:
                    by_availability[map_name].append(asset.asset_type)

        # Sort asset lists
        for key in by_availability:
            by_availability[key].sort()

        return dict(by_availability)


class ThemeIndexer:
    """Index assets by theme keywords.

    Single Responsibility: Theme-based indexing using keyword heuristics.
    """

    # Theme keywords for classification
    THEME_KEYWORDS = {
        "military": ["military", "bunker", "trench", "tank", "weapon", "barracks"],
        "natural": ["tree", "rock", "plant", "vegetation", "cliff", "boulder"],
        "industrial": ["industrial", "factory", "warehouse", "crate", "barrel"],
        "urban": ["building", "house", "apartment", "street", "city"],
        "fortification": ["wall", "fence", "barrier", "sandbag", "gate"],
    }

    def index(self, assets: list[PortalAsset]) -> dict[str, list[str]]:
        """Create theme-based index.

        Returns:
            Dict mapping theme names to lists of asset types
        """
        by_theme: dict[str, list[str]] = defaultdict(list)

        for asset in assets:
            asset_lower = asset.asset_type.lower()
            dir_lower = asset.directory.lower()

            # Check each theme's keywords
            for theme, keywords in self.THEME_KEYWORDS.items():
                if any(kw in asset_lower or kw in dir_lower for kw in keywords):
                    by_theme[theme].append(asset.asset_type)

        # Sort asset lists
        for theme in by_theme:
            by_theme[theme].sort()

        return dict(by_theme)


# ============================================================================
# Index Writer Implementations
# ============================================================================


class JSONIndexWriter:
    """Write index data to JSON file.

    Single Responsibility: JSON output formatting only.
    """

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def write(self, index_data: dict[str, Any]) -> None:
        """Write index data to JSON file.

        Args:
            index_data: Complete index structure to write
        """
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)


class MarkdownCatalogWriter:
    """Write asset catalog as browsable markdown.

    Single Responsibility: Markdown catalog generation only.
    """

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path

    def write(self, index_data: dict[str, Any]) -> None:
        """Write asset catalog as markdown.

        Args:
            index_data: Complete index structure with metadata
        """
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w", encoding="utf-8") as f:
            self._write_header(f, index_data.get("_metadata", {}))
            self._write_summary(f, index_data.get("_metadata", {}))
            self._write_category_index(f, index_data.get("by_category", {}))
            self._write_availability_index(f, index_data.get("by_availability", {}))
            self._write_theme_index(f, index_data.get("by_theme", {}))

    def _write_header(self, f: Any, metadata: dict[str, Any]) -> None:
        """Write markdown header."""
        f.write("# Portal Asset Catalog\n\n")
        f.write("> Complete indexed catalog of Battlefield Portal assets\n\n")
        f.write(f"**Generated:** {metadata.get('generated_date', 'N/A')}  \n")
        f.write(f"**Source:** `{metadata.get('source_file', 'N/A')}`  \n")
        f.write(f"**Total Assets:** {metadata.get('total_assets', 0):,}\n\n")
        f.write("---\n\n")

    def _write_summary(self, f: Any, metadata: dict[str, Any]) -> None:
        """Write summary statistics."""
        f.write("## Summary\n\n")
        f.write(f"- **Total Assets:** {metadata.get('total_assets', 0):,}\n")
        f.write(f"- **Unrestricted Assets:** {metadata.get('unrestricted_count', 0):,}\n")
        f.write(f"- **Categories:** {len(metadata.get('categories', {}))}\n\n")

        # Category breakdown
        categories = metadata.get("categories", {})
        if categories:
            f.write("### Assets by Category\n\n")
            sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            for cat, count in sorted_cats:
                f.write(f"- **{cat}:** {count:,} assets\n")
            f.write("\n")

        f.write("---\n\n")

    def _write_category_index(self, f: Any, by_category: dict[str, list[dict]]) -> None:
        """Write category-based index."""
        f.write("## Assets by Category\n\n")

        for category in sorted(by_category.keys()):
            assets = by_category[category]
            f.write(f"### {category} ({len(assets)} assets)\n\n")

            for asset in assets[:50]:  # Limit to first 50 per category for readability
                restrictions = (
                    "All maps"
                    if asset["unrestricted"]
                    else f"{len(asset['level_restrictions'])} maps"
                )
                f.write(f"- **{asset['type']}** - {asset['directory']} ({restrictions})\n")

            if len(assets) > 50:
                f.write(f"\n*...and {len(assets) - 50} more assets*\n")

            f.write("\n")

        f.write("---\n\n")

    def _write_availability_index(self, f: Any, by_availability: dict[str, list[str]]) -> None:
        """Write availability-based index."""
        f.write("## Assets by Map Availability\n\n")

        # Unrestricted first
        if "unrestricted" in by_availability:
            unrestricted = by_availability["unrestricted"]
            f.write(f"### Unrestricted ({len(unrestricted)} assets)\n\n")
            f.write("Available on all Portal maps.\n\n")

        # Map-specific
        map_names = sorted([k for k in by_availability if k != "unrestricted"])
        f.write("### Map-Specific Assets\n\n")
        for map_name in map_names:
            assets = by_availability[map_name]
            f.write(f"- **{map_name}:** {len(assets)} exclusive assets\n")

        f.write("\n---\n\n")

    def _write_theme_index(self, f: Any, by_theme: dict[str, list[str]]) -> None:
        """Write theme-based index."""
        f.write("## Assets by Theme\n\n")

        for theme in sorted(by_theme.keys()):
            assets = by_theme[theme]
            f.write(f"### {theme.title()} ({len(assets)} assets)\n\n")

            # Show first 20 examples
            for asset_type in assets[:20]:
                f.write(f"- {asset_type}\n")

            if len(assets) > 20:
                f.write(f"\n*...and {len(assets) - 20} more assets*\n")

            f.write("\n")

        f.write("---\n\n")
        f.write("*This catalog was automatically generated from the Portal SDK asset database.*\n")


# ============================================================================
# Facade (Simplified Interface)
# ============================================================================


class PortalAssetIndexerFacade:
    """High-level facade for Portal asset indexing operations.

    Facade pattern - provides simple interface to complex subsystem.
    Single entry point for all indexing operations.
    """

    def __init__(
        self, asset_types_path: Path, json_output_path: Path, markdown_output_path: Path
    ) -> None:
        """Initialize the indexer facade.

        Args:
            asset_types_path: Path to Portal SDK asset_types.json
            json_output_path: Where to write JSON index
            markdown_output_path: Where to write markdown catalog
        """
        self.reader = PortalSDKAssetReader(asset_types_path)
        self.json_writer = JSONIndexWriter(json_output_path)
        self.markdown_writer = MarkdownCatalogWriter(markdown_output_path)

        # Indexers
        self.category_indexer = CategoryIndexer()
        self.availability_indexer = AvailabilityIndexer()
        self.theme_indexer = ThemeIndexer()

    def generate_indexes(self) -> dict[str, Any]:
        """Generate all indexes and write outputs.

        This is the main entry point - coordinates the entire indexing pipeline.

        Returns:
            Complete index data structure
        """
        from datetime import datetime

        # Step 1: Read assets
        print("📖 Reading Portal SDK assets...")
        assets = self.reader.read()
        print(f"   Loaded {len(assets)} assets")

        # Step 2: Generate indexes
        print("🔍 Generating indexes...")
        by_category = self.category_indexer.index(assets)
        by_availability = self.availability_indexer.index(assets)
        by_theme = self.theme_indexer.index(assets)

        # Step 3: Build metadata
        category_counts = {cat: len(assets) for cat, assets in by_category.items()}
        unrestricted_count = len(by_availability.get("unrestricted", []))

        metadata = {
            "source_file": str(self.reader.asset_types_path),
            "total_assets": len(assets),
            "generated_date": datetime.now().strftime("%Y-%m-%d"),
            "categories": category_counts,
            "unrestricted_count": unrestricted_count,
        }

        # Step 4: Combine into complete index
        index_data = {
            "_metadata": metadata,
            "by_category": by_category,
            "by_availability": by_availability,
            "by_theme": by_theme,
        }

        # Step 5: Write outputs
        print("💾 Writing JSON index...")
        self.json_writer.write(index_data)

        print("📄 Writing markdown catalog...")
        self.markdown_writer.write(index_data)

        return index_data
