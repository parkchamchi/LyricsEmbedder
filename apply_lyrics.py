"""
Apply the scraped lyrics to the files.

Since the `audio_metadata` library does not support modifying the file right now, I'll use `music-tag` here...
"""

from dbcreate import dbname

import music_tag

import sqlite3

if __name__ == "__main__":
	conn = sqlite3.connect(dbname)
	curs = conn.cursor()

	for path, lyrics in curs.execute("""
		SELECT path, lyrics
		FROM lyrics
		WHERE lyrics IS NOT NULL;
	"""):
		print(f"On {path}")

		file = music_tag.load_file(path)
		file["lyrics"] = lyrics
		file.save()

	curs.close()
	conn.close()