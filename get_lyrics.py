"""
Get the the lyrics from (artist, title) tuple
"""

from dbcreate import dbname

import sqlite3
from bs4 import BeautifulSoup as Soup
import requests

headers = {
	"User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
	"Accept-Encoding": "gzip, deflate",
	"Accept-Language": "en-US;en;q=0.9",
	"Connection": "keep-alive"
}

def getlyrics(session, artist: str, title: str) -> str:
	def normalize(string):
		string = string.replace(' ', '-')
		string = ''.join(c for c in string if c.isalnum() or c == '-')
		return string
	
	artist = normalize(artist)
	title = normalize(title)

	url = f"https://genius.com/{artist}-{title}-lyrics"
	print('*'*64)
	print(f"On {url}")
	print()

	req = session.get(url, headers=headers)
	page_obj = Soup(req.text, "html.parser")

	"""
	<div id="lyrics">
	</div>

	<div id="lyrics-root">
		<div class="Lyrics__Container-sc-..." data-lyrics-container="true">
			...
		</div>
	</div>
	"""

	"""
	with open("tmp.html", "wt", encoding="utf-8") as fout:
		fout.write(req.text)
	"""

	lyrics_div = page_obj.find("div", id="lyrics")
	lyrics_root = page_obj.find("div", id="lyrics-root")

	if lyrics_div is None:
		print("Couldn't fetch.")
		return None
	elif lyrics_root is None:
		return "[Instrumental]"

	lyrics = ""
	for container in lyrics_root.find_all("div", {"data-lyrics-container": "true"}):
		for br in container.find_all("br"):
			br.replace_with("\n")

		lyrics += container.get_text()
		lyrics += '\n'

	return lyrics

if __name__ == "__main__":
	print("Please read the README.md file")

	conn = sqlite3.connect(dbname)
	curs = conn.cursor()

	session = requests.session()

	for artist, title in curs.execute("""
		SELECT artist, title 
		FROM lyrics 
		WHERE lyrics IS NULL AND title IS NOT NULL;
	""").fetchall():
		lyrics = getlyrics(session, artist, title)
		print(lyrics)
		print()

		if lyrics is None:
			continue

		curs.execute("""
			UPDATE lyrics
			SET lyrics = ?
			WHERE artist = ? AND title = ?;
		""",
		(lyrics, artist, title))
		conn.commit()

	curs.close()
	conn.close()