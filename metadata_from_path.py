"""
Set the metadata from the path

assumes `.../artist/(album)/title.ext

where `title` can be
01 - actualtitle
01 actualtitle
"""

from dbcreate import dbname

import sqlite3
import re

def get_metadata_from_path(path) -> tuple:
	tokens = re.split(r"[/\\]", path)
    
	artist = tokens[-3]

	title = tokens[-1]
	title = title[:title.rfind('.')]
	title = re.sub(r"^\d+\s*-?\s*", "", title)

	return artist, title

if __name__ == "__main__":
	conn = sqlite3.connect(dbname)
	curs = conn.cursor()

	for (path,) in curs.execute("""
		SELECT path 
		FROM lyrics 
		WHERE artist IS NULL;
	""").fetchall():
		artist, title = get_metadata_from_path(path)
		print(path)
		print(artist, "-", title)

		curs.execute("""
			UPDATE lyrics
			SET artist = ?, title = ?
			WHERE path = ?
		""",
		(artist, title, path))
		conn.commit()

	curs.close()
	conn.close()