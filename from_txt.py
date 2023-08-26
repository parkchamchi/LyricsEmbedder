import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input",
	default="lang2.txt",
)
parser.add_argument("--dry",
	action="store_true",
)
args = parser.parse_args()

txt = args.input

with open(txt, "rt", encoding="utf-8") as fin:
	txt = fin.read()

fout = open("out.txt", "wt", encoding="utf-8")

#Split the text with `
songs = txt.split("\n`\n")
print(f"len(songs): {len(songs)}")

formatteds = []

for i, song in enumerate(songs):
	num = i + 1 #To match the DB

	paragraphs = re.split(r"\n\s*\n", song)

	"""
	Cut of the training blank lines
	Since we want the initial blank (e.g. "\n the space left\n"), we won't use lstrip() here.
	"""
	for j in range(len(paragraphs)):
		paragraphs[j] = '\n'.join([
			line
			for line in
			paragraphs[j].splitlines()
			if line.strip() != ""
		])
	paragraphs = [p for p in paragraphs if p.strip() != ""]

	#Split the lang1 and lang2
	try:
		delimiter_idx = paragraphs.index("#")
	except ValueError:
		raise RuntimeError(f"Malformatted text file: {paragraphs}")

	lang1, lang2 = paragraphs[:delimiter_idx], paragraphs[delimiter_idx+1:]
	no_lang2 = (lang2 == ["..."])

	if len(lang1) != len(lang2) and not no_lang2:
		print(f"{num}")

		print(lang1)
		print('*'*16)
		print(lang2)
	
	#Format
	formatted = ""

	if no_lang2:
		formatted = '\n\n'.join(lang1)
	else:
		for p1, p2 in zip(lang1, lang2):
			formatted += p1
			formatted += "\n\n"

			formatted += '\n'.join([
				"> " + line
				for line in
				p2.split('\n')
			])
			formatted += '\n\n'
		
		formatted = formatted[:-2] #Remove the last newlines

		fout.write(formatted)
		fout.write("\n----------------\n")

	formatteds.append(formatted)

if not args.dry:
	from dbcreate import dbname
	
	import sqlite3

	conn = sqlite3.connect(dbname)
	curs = conn.cursor()

	paths = [p[0] for p in curs.execute("SELECT path FROM lyrics;").fetchall()]
	for path, formatted in zip(paths, formatteds):
		curs.execute("""
			UPDATE lyrics
			SET lyrics = ?
			WHERE path = ?;
		""", (formatted, path))
		conn.commit()

	curs.close()
	conn.close()

if fout:
	fout.close()