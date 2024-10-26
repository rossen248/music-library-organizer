#!/usr/bin/env python3
# musicmaid.py - Your music library's cleaning service
# Organizes music files into artist/album folders based on metadata

import os
from mutagen import File
import shutil
from pathlib import Path
import re


def sanitize_filename(name):
    """
    Sanitizes a string to be used as a directory name.
    Replaces invalid characters with underscore, preserving existing underscores.

    Args:
        name (str): The string to sanitize

    Returns:
        str: Sanitized string safe for use as directory name
    """
    # Windows reserved characters
    invalid_chars_pattern = r'[<>:"/\\|?*]'

    # Replace invalid characters with underscore
    sanitized = re.sub(invalid_chars_pattern, '_', name)

    # Only remove leading/trailing whitespace
    sanitized = sanitized.strip()

    # If name would be empty after sanitization, use a default
    if not sanitized:
        return "Unknown"

    return sanitized


def organize_music(source_dir, destination_dir):
    """
    Organizes music files by album artist and album based on metadata.

    Args:
        source_dir (str): Directory containing the music files
        destination_dir (str): Base directory where organized folders will be created
    """
    # Create destination directory if it doesn't exist
    Path(destination_dir).mkdir(parents=True, exist_ok=True)

    # Supported music file extensions
    music_extensions = {'.mp3', '.m4a', '.flac', '.wav', '.ogg'}

    # Track statistics
    processed_files = 0
    deleted_duplicates = 0
    deleted_spotdl = 0
    error_files = 0

    # Walk through the source directory
    for root, _, files in os.walk(source_dir):
        for filename in files:
            file_path = os.path.join(root, filename)

            # Handle .spotdl files
            if filename.endswith('.spotdl'):
                try:
                    os.remove(file_path)
                    print(f"Deleted .spotdl file: {filename}")
                    deleted_spotdl += 1
                    continue
                except Exception as e:
                    print(f"Error deleting .spotdl file {filename}: {str(e)}")
                    error_files += 1
                    continue

            # Process music files
            if any(filename.lower().endswith(ext) for ext in music_extensions):
                try:
                    # Extract metadata
                    audio = File(file_path, easy=True)

                    if audio is None:
                        print(f"Couldn't read metadata for: {filename}")
                        error_files += 1
                        continue

                    # Try to get album artist first, fall back to artist if not available
                    artist = str(audio.get('albumartist', [''])[0])
                    if not artist:  # If album artist is empty, try regular artist
                        artist = str(audio.get('artist', ['Unknown Artist'])[0])

                    album = str(audio.get('album', ['Unknown Album'])[0])

                    # Sanitize artist and album names
                    artist = sanitize_filename(artist)
                    album = sanitize_filename(album)

                    # Create artist and album directories
                    artist_path = Path(destination_dir) / artist
                    album_path = artist_path / album

                    # Create destination path
                    destination_file = album_path / filename

                    # Check if file already exists in destination
                    if destination_file.exists():
                        # File is already organized, just delete the source
                        os.remove(file_path)
                        print(f"Deleted duplicate: {filename} (already exists in {artist}/{album}/)")
                        deleted_duplicates += 1
                        continue

                    # If file doesn't exist, create directories and copy
                    album_path.mkdir(parents=True, exist_ok=True)

                    # Copy the file to its new location
                    shutil.copy2(file_path, destination_file)

                    # Delete the source file after successful copy
                    os.remove(file_path)

                    print(f"Organized: {filename} -> {artist}/{album}/")
                    processed_files += 1

                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")
                    error_files += 1

    # Clean up empty directories in source
    for root, dirs, files in os.walk(source_dir, topdown=False):
        for dir_name in dirs:
            try:
                dir_path = os.path.join(root, dir_name)
                if not os.listdir(dir_path):  # if directory is empty
                    os.rmdir(dir_path)
                    print(f"Removed empty directory: {dir_path}")
            except Exception as e:
                print(f"Error removing directory {dir_path}: {str(e)}")

    # Print summary
    print("\nOrganization complete!")
    print(f"Successfully organized: {processed_files} files")
    print(f"Duplicates deleted: {deleted_duplicates} files")
    print(f".spotdl files deleted: {deleted_spotdl} files")
    print(f"Errors encountered: {error_files} files")


if __name__ == "__main__":
    source_directory = "C:/Users/rosse/Documents/projects/iPod/Unsorted"  # Directory containing your downloaded music
    destination_directory = "C:/Users/rosse/Documents/projects/iPod/Artists"  # Where you want the organized folders

    organize_music(source_directory, destination_directory)

    input("\nPress Enter to exit...")