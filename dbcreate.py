"""
Create a database from audio files, with attributes
	path, artist, title, lyrics
"""

import audio_metadata

import os
from collections import defaultdict
import sqlite3
from pprint import pprint
import argparse

dbname = "lyrics.db"

def walk(path: str, exts=[".mp3", ".flac", ".m4a"]) -> list:
	"""
	Returns a list of audio filenames (with dir names)
	"""

	print(f"Walking: {path}")

	audios = []
	ignored_counter = defaultdict(int)

	for dirname, _, filenames in os.walk(path):
		for filename in filenames:
			#Find the ext
			ploc = filename.rfind('.')
			if ploc != -1:
				fileext = filename[ploc:].lower()
			else:
				fileext = filename

			fullpath = os.path.join(dirname, filename) #need not be the abs path

			if any(map(fileext.__eq__, exts)):
				audios.append(fullpath)
			else:
				ignored_counter[fileext] += 1

	print(f"Found {len(audios)} audio files")
	print(f"Ignored exts: {dict(ignored_counter)}")

	return audios

def get_artist_title(path: str) -> tuple:
	"""
	Uses audio_metadata
	"""

	metadata = audio_metadata.load(path)
	
	artist = metadata.tags["artist"][0] #.artist does not work in m4a?
	title = metadata.tags["title"][0]

	return artist, title

def create_db():
	if os.path.exists(dbname):
		raise ValueError(f"Already exists: {dbname}")

	conn = sqlite3.connect(dbname)
	curs = conn.cursor()

	#(artist, title) can be null if its metadata couldn't be read
	curs.execute("""
		CREATE TABLE lyrics (
			path VARCHAR(256) PRIMARY KEY,
			artist VARCHAR(64),
			title VARCHAR(64),

			lyrics TEXT
		);
	""")

	curs.close()
	conn.close()

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("dir", help="target directory")
	args = parser.parse_args()

	excs = {}

	if not os.path.exists(dbname):
		create_db()
	conn = sqlite3.connect(dbname)
	curs = conn.cursor()

	for filename in walk(args.dir):		
		artist, title = None, None
		try:
			artist, title = get_artist_title(filename)
		except Exception as exc:
			excs[filename] = exc

		curs.execute("INSERT INTO lyrics(path, artist, title) VALUES (?, ?, ?)", (filename, artist, title))

	conn.commit()

	curs.close()
	conn.close()		

	print(f"{len(excs)} files couldn't be read:")
	pprint(excs)