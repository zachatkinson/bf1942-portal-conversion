#!/usr/bin/env python3
"""Battlefield 1942 RFA (Refractor Archive) Extraction Tool.

This module provides functionality to extract files from Battlefield 1942's
RFA archive format. The RFA format uses LZO compression and contains game
assets like maps, textures, and configuration files.

Usage:
    python rfa_extractor.py <input.rfa> <output_dir>

References:
    - https://github.com/yann-papouin/bga (BGA tool)
    - https://bfmods.com (BF1942 modding community)
"""

import struct
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class RFAHeader:
    """RFA archive header structure."""

    def __init__(self, data: bytes):
        """Parse RFA header from bytes.

        Args:
            data: Raw header bytes from RFA file
        """
        # RFA files start with a magic signature
        self.magic = struct.unpack('<I', data[0:4])[0]
        self.version = struct.unpack('<I', data[4:8])[0]
        logger.debug(f"RFA Magic: {hex(self.magic)}, Version: {self.version}")


class RFAFileEntry:
    """Represents a single file entry in the RFA archive."""

    def __init__(self, filename: str, offset: int, size: int, compressed_size: int):
        """Create file entry.

        Args:
            filename: Path to file within archive
            offset: Byte offset in archive where file data starts
            size: Uncompressed file size
            compressed_size: Compressed file size (0 if uncompressed)
        """
        self.filename = filename
        self.offset = offset
        self.size = size
        self.compressed_size = compressed_size
        self.is_compressed = compressed_size > 0

    def __repr__(self) -> str:
        comp_str = f" (compressed: {self.compressed_size})" if self.is_compressed else ""
        return f"<RFAFileEntry: {self.filename} @ {self.offset}, size: {self.size}{comp_str}>"


class RFAExtractor:
    """Extracts files from Battlefield 1942 RFA archives."""

    def __init__(self, rfa_path: str):
        """Initialize extractor for RFA file.

        Args:
            rfa_path: Path to .rfa file

        Raises:
            FileNotFoundError: If RFA file doesn't exist
        """
        self.rfa_path = Path(rfa_path)
        if not self.rfa_path.exists():
            raise FileNotFoundError(f"RFA file not found: {rfa_path}")

        self.file_entries: List[RFAFileEntry] = []
        self.header: Optional[RFAHeader] = None

    def _read_header(self, f) -> RFAHeader:
        """Read and parse RFA header.

        Args:
            f: File object positioned at start

        Returns:
            Parsed RFA header
        """
        header_data = f.read(256)  # Read enough for header analysis
        return RFAHeader(header_data)

    def _parse_file_table(self, f):
        """Parse the file table to get list of files and offsets.

        This is a simplified implementation. The actual RFA format is more complex
        and may require reverse engineering or using existing tools like BGA.

        Args:
            f: File object
        """
        # Note: This is a placeholder implementation
        # The actual RFA file table format needs to be reverse engineered
        # For now, we'll use external tools or libraries
        logger.warning("RFA file table parsing not yet implemented")
        logger.info("Consider using external tool like BGA or python-lzo with full format spec")

    def extract_all(self, output_dir: str) -> bool:
        """Extract all files from RFA archive.

        Args:
            output_dir: Directory to extract files to

        Returns:
            True if extraction succeeded, False otherwise
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Extracting {self.rfa_path} to {output_dir}")

        with open(self.rfa_path, 'rb') as f:
            self.header = self._read_header(f)
            self._parse_file_table(f)

        if not self.file_entries:
            logger.warning("No file entries found (file table parsing not implemented)")
            logger.info("Recommendation: Use external BGA tool for extraction")
            return False

        # Extract each file
        with open(self.rfa_path, 'rb') as f:
            for entry in self.file_entries:
                self._extract_file(f, entry, output_path)

        logger.info(f"Extraction complete: {len(self.file_entries)} files")
        return True

    def _extract_file(self, f, entry: RFAFileEntry, output_path: Path):
        """Extract a single file from the archive.

        Args:
            f: File object
            entry: File entry to extract
            output_path: Base output directory
        """
        file_output = output_path / entry.filename
        file_output.parent.mkdir(parents=True, exist_ok=True)

        f.seek(entry.offset)
        data = f.read(entry.compressed_size if entry.is_compressed else entry.size)

        if entry.is_compressed:
            try:
                import lzo
                data = lzo.decompress(data, entry.size)
            except ImportError:
                logger.error("python-lzo not installed. Install with: pip install python-lzo")
                logger.error("On Linux: sudo apt-get install liblzo2-dev")
                return
            except Exception as e:
                logger.error(f"Failed to decompress {entry.filename}: {e}")
                return

        with open(file_output, 'wb') as out:
            out.write(data)

        logger.debug(f"Extracted: {entry.filename}")

    def list_files(self) -> List[str]:
        """List all files in the archive.

        Returns:
            List of file paths within archive
        """
        with open(self.rfa_path, 'rb') as f:
            self.header = self._read_header(f)
            self._parse_file_table(f)

        return [entry.filename for entry in self.file_entries]


def use_external_tool(rfa_path: str, output_dir: str, tool: str = "bga") -> bool:
    """Use an external tool to extract RFA.

    Since implementing a full RFA parser is complex, this function suggests
    using established tools like BGA or providing instructions.

    Args:
        rfa_path: Path to RFA file
        output_dir: Output directory
        tool: Tool to suggest ("bga" or "winrfa")

    Returns:
        False (not implemented, just provides instructions)
    """
    logger.info("=" * 70)
    logger.info("RFA EXTRACTION - EXTERNAL TOOL REQUIRED")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Full RFA parsing is complex. Recommended approaches:")
    logger.info("")
    logger.info("1. BGA (Battlefield Game Archive):")
    logger.info("   - Download from: https://github.com/yann-papouin/bga")
    logger.info("   - Windows tool with GUI and command-line support")
    logger.info("")
    logger.info("2. Manual extraction with existing tools:")
    logger.info("   - WinRFA (Windows)")
    logger.info("   - rfaUnpack.exe (command-line)")
    logger.info("")
    logger.info("3. Alternative: We can wrap these tools with Python")
    logger.info("")
    logger.info(f"Once extracted, place contents in: {output_dir}")
    logger.info("")
    logger.info("=" * 70)

    return False


def main():
    """Command-line entry point."""
    if len(sys.argv) < 3:
        print("Usage: python rfa_extractor.py <input.rfa> <output_dir>")
        print("")
        print("Example:")
        print("  python rfa_extractor.py Kursk.rfa ./extracted/Kursk")
        sys.exit(1)

    rfa_path = sys.argv[1]
    output_dir = sys.argv[2]

    # For now, provide guidance on using external tools
    # In Phase 3, we can integrate BGA or implement full RFA parsing
    use_external_tool(rfa_path, output_dir)

    # Attempt extraction (will show warning about unimplemented parsing)
    # extractor = RFAExtractor(rfa_path)
    # success = extractor.extract_all(output_dir)
    # sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
