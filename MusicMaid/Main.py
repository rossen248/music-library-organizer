#!/usr/bin/env python3
# musicmaid.py - Your music library's cleaning service
# Organizes music files into artist/album folders based on metadata

import os
from mutagen import File
import shutil
from pathlib import Path


def organize_music(source_dir, destination_dir):
    """
    Organizes music files by artist and album based on metadata.

    Args:
        source_dir (str): Directory containing the music files
        destination_dir (str): Base directory where organized folders will be created
    """
    # Create destination directory if it doesn't exist
    Path(destination_dir).mkdir(parents=True, exist_ok=True)

    # Supported music file extensions
    music_extensions = {'.mp3', '.m4a', '.flac', '.wav', '.ogg'}

    # Walk through the source directory
    for root, _, files in os.walk(source_dir):
        for filename in files:
            if any(filename.lower().endswith(ext) for ext in music_extensions):
                file_path = os.path.join(root, filename)

                try:
                    # Extract metadata
                    audio = File(file_path, easy=True)

                    if audio is None:
                        print(f"Couldn't read metadata for: {filename}")
                        continue

                    # Get artist and album info, use defaults if not found
                    artist = str(audio.get('artist', ['Unknown Artist'])[0])
                    album = str(audio.get('album', ['Unknown Album'])[0])

                    # Clean up folder names to avoid invalid characters
                    artist = "".join(c for c in artist if c.isalnum() or c in (' ', '-', '_'))
                    album = "".join(c for c in album if c.isalnum() or c in (' ', '-', '_'))

                    # Create artist and album directories
                    artist_path = Path(destination_dir) / artist
                    album_path = artist_path / album

                    # Create directories if they don't exist
                    album_path.mkdir(parents=True, exist_ok=True)

                    # Create destination path
                    destination_file = album_path / filename

                    # Copy the file to its new location
                    shutil.copy2(file_path, destination_file)
                    print(f"Organized: {filename} -> {artist}/{album}/")

                except Exception as e:
                    print(f"Error processing {filename}: {str(e)}")


if __name__ == "__main__":
    source_directory = "./downloads"  # Directory containing your downloaded music
    destination_directory = "./organized_music"  # Where you want the organized folders

    organize_music(source_directory, destination_directory)