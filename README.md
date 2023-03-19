# Lyrics Embedder

Reads the metadata from audio files, then scrapes the lyrics from the web and embeds them on the files.

## Steps

### dbcreate.py

Walking through the given path, this script finds the audio files.
Then it creates a SQLite database of attributes (`path`, `artist`, `title`, `lyrics`),
where `artist` and `title` are read from the metadata using the [audio_metadata](https://github.com/thebigmunch/audio-metadata) library.
(The embedding script uses different library since this doesn't support writing the metadata yet)

### metadata_from_path.py

An auxilary script for setting (`artist`, `title`) set that could not be read from the script above.
The track number on the filename is stripped using regex.

### get_lyrics.py

Inserts the lyrics scraped from the web to the database. It parses `genius.com`.

### apply_lyrics.py

Embeds the lyrics from the database (from the script or put manually) to the files.
This uses [music_tag](https://github.com/KristoforMaynard/music-tag) library.