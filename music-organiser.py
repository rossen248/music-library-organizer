#!/usr/bin/env python3
"""
Music Library Organizer
A Python script that automatically organizes music files into artist/album folders based on metadata.
"""

import os
import sys
import argparse
from mutagen import File
import shutil
from pathlib import Path
import re
from typing import Tuple, Set


class MusicOrganizer:
    """Main class for organizing music files."""

    def __init__(self, source_dir: str, destination_dir: str):
        self.source_dir = Path(source_dir)
        self.destination_dir = Path(destination_dir)
        self.music_extensions = {'.mp3', '.m4a', '.flac', '.wav', '.ogg', '.wma'}

        # Statistics
        self.stats = {
            'processed': 0,
            'duplicates': 0,
            'spotdl_deleted': 0,
            'errors': 0
        }

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """
        Sanitizes a string to be used as a directory name.

        Args:
            name: The string to sanitize

        Returns:
            Sanitized string safe for use as directory name
        """
        if not name or not name.strip():
            return "Unknown"

        # Remove invalid characters for cross-platform compatibility
        invalid_chars_pattern = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars_pattern, '_', name)

        # Remove leading/trailing whitespace and dots (Windows compatibility)
        sanitized = sanitized.strip(' .')

        # Truncate if too long (common filesystem limit)
        if len(sanitized) > 200:
            sanitized = sanitized[:200].rstrip()

        return sanitized or "Unknown"

    def extract_metadata(self, file_path: Path) -> Tuple[str, str]:
        """
        Extracts artist and album information from music file metadata.

        Args:
            file_path: Path to the music file

        Returns:
            Tuple of (artist, album)
        """
        try:
            audio = File(str(file_path), easy=True)

            if audio is None:
                return "Unknown Artist", "Unknown Album"

            # Prioritize albumartist over artist for better compilation handling
            artist = ""
            if 'albumartist' in audio and audio['albumartist'][0]:
                artist = str(audio['albumartist'][0])
            elif 'artist' in audio and audio['artist'][0]:
                artist = str(audio['artist'][0])

            album = ""
            if 'album' in audio and audio['album'][0]:
                album = str(audio['album'][0])

            # Sanitize the extracted metadata
            artist = self.sanitize_filename(artist) or "Unknown Artist"
            album = self.sanitize_filename(album) or "Unknown Album"

            return artist, album

        except Exception as e:
            print(f"Warning: Couldn't read metadata for {file_path.name}: {e}")
            return "Unknown Artist", "Unknown Album"

    def is_music_file(self, file_path: Path) -> bool:
        """Check if file is a supported music format."""
        return file_path.suffix.lower() in self.music_extensions

    def handle_spotdl_file(self, file_path: Path) -> bool:
        """
        Handles .spotdl files by deleting them.

        Returns:
            True if successfully deleted, False otherwise
        """
        try:
            file_path.unlink()
            print(f"✓ Deleted .spotdl file: {file_path.name}")
            self.stats['spotdl_deleted'] += 1
            return True
        except Exception as e:
            print(f"✗ Error deleting .spotdl file {file_path.name}: {e}")
            self.stats['errors'] += 1
            return False

    def organize_file(self, file_path: Path) -> bool:
        """
        Organizes a single music file.

        Returns:
            True if successfully organized, False otherwise
        """
        try:
            # Extract metadata
            artist, album = self.extract_metadata(file_path)

            # Create destination path
            artist_path = self.destination_dir / artist
            album_path = artist_path / album
            destination_file = album_path / file_path.name

            # Check for duplicates
            if destination_file.exists():
                file_path.unlink()  # Remove source file
                print(f"⚠ Duplicate removed: {file_path.name} (exists in {artist}/{album}/)")
                self.stats['duplicates'] += 1
                return True

            # Create directory structure
            album_path.mkdir(parents=True, exist_ok=True)

            # Copy file to new location
            shutil.copy2(file_path, destination_file)
            file_path.unlink()  # Remove source after successful copy

            print(f"✓ Organized: {file_path.name} → {artist}/{album}/")
            self.stats['processed'] += 1
            return True

        except Exception as e:
            print(f"✗ Error processing {file_path.name}: {e}")
            self.stats['errors'] += 1
            return False

    def cleanup_empty_directories(self) -> None:
        """Remove empty directories from source path."""
        try:
            for root, dirs, files in os.walk(self.source_dir, topdown=False):
                for dir_name in dirs:
                    dir_path = Path(root) / dir_name
                    try:
                        if not any(dir_path.iterdir()):  # Directory is empty
                            dir_path.rmdir()
                            print(f"✓ Removed empty directory: {dir_path}")
                    except Exception as e:
                        print(f"⚠ Couldn't remove directory {dir_path}: {e}")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def organize(self) -> None:
        """Main organization method."""
        # Validate directories
        if not self.source_dir.exists():
            print(f"✗ Source directory doesn't exist: {self.source_dir}")
            return

        # Create destination directory
        self.destination_dir.mkdir(parents=True, exist_ok=True)

        print(f"🎵 Starting music organization...")
        print(f"📁 Source: {self.source_dir}")
        print(f"📁 Destination: {self.destination_dir}")
        print("-" * 50)

        # Process all files
        for root, _, files in os.walk(self.source_dir):
            root_path = Path(root)

            for filename in files:
                file_path = root_path / filename

                if filename.endswith('.spotdl'):
                    self.handle_spotdl_file(file_path)
                elif self.is_music_file(file_path):
                    self.organize_file(file_path)

        # Cleanup empty directories
        print("\n🧹 Cleaning up empty directories...")
        self.cleanup_empty_directories()

        # Print summary
        self.print_summary()

    def print_summary(self) -> None:
        """Print organization statistics."""
        print("\n" + "=" * 50)
        print("🎉 Organization Complete!")
        print("=" * 50)
        print(f"✅ Files organized: {self.stats['processed']}")
        print(f"🔄 Duplicates removed: {self.stats['duplicates']}")
        print(f"🗑️  .spotdl files deleted: {self.stats['spotdl_deleted']}")
        print(f"❌ Errors encountered: {self.stats['errors']}")

        total_processed = sum(self.stats.values()) - self.stats['errors']
        if total_processed > 0:
            print(f"\n📊 Success rate: {((total_processed - self.stats['errors']) / total_processed * 100):.1f}%")


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Organize music files into Artist/Album folder structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python music_organizer.py ~/Downloads/Music ~/Music/Library
  python music_organizer.py "C:\\Downloads" "C:\\Music" --dry-run
        """
    )

    parser.add_argument('source', help='Source directory containing music files')
    parser.add_argument('destination', help='Destination directory for organized library')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be done without making changes')

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No files will be moved or deleted")
        print("This feature is not yet implemented. Remove --dry-run to proceed.")
        return

    try:
        organizer = MusicOrganizer(args.source, args.destination)
        organizer.organize()

    except KeyboardInterrupt:
        print("\n\n⚠️  Organization cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # If no command line arguments, use the original hardcoded paths for backwards compatibility
    if len(sys.argv) == 1:
        source_directory = "~/Downloads/Music"
        destination_directory = "~/Music/Library"

        print("🎵 Using default directories...")
        organizer = MusicOrganizer(source_directory, destination_directory)
        organizer.organize()
        input("\n⏎ Press Enter to exit...")
    else:
        main()
