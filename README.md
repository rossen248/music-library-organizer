# Music Organizer

Automatically organizes music files into `Artist/Album/` folders based on metadata.

## Usage

1. Install dependencies:
```bash
pip install mutagen
```

2. Edit the paths in `music_organizer.py`:
```python
source_directory = "path/to/unsorted/music"
destination_directory = "path/to/organized/library"
```

3. Run:
```bash
python music_organizer.py
```

## Features

- Organizes music files by artist and album using metadata tags
- Removes duplicate files and `.spotdl` files  
- Supports MP3, FLAC, M4A, WAV, OGG formats
- Cleans up empty directories
- Cross-platform compatible

**Before**: Messy folders with random files  
**After**: Clean `Artist Name/Album Name/song.mp3` structure

⚠️ **Always backup your music collection first!**