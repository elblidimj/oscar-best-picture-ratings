# Build the table of Best Picture nominees (ceremonies 1996 to 2017) with their MovieLens movieId.
# Run from the project root: python src/build_nominees_table.py

import duckdb

OSCARS_FILE = "data/raw/oscar_archive_1927_2025/full_data.csv"
LINKS_FILE = "data/raw/ml-32m/links.csv"
OUTPUT_FILE = "data/processed/best_picture_nominees_1996_2017.csv"

con = duckdb.connect()

# full_data.csv: tab-separated, and rows have a variable number of fields
# (empty trailing fields are missing), so we pad them with NULL. All columns are read as text.
con.sql(f"""
CREATE VIEW oscars_full AS
SELECT * FROM read_csv('{OSCARS_FILE}',
                       delim='\t', quote='', escape='', header=true, all_varchar=true, null_padding=true)
""")

# The 142 Best Picture nominees of the ceremonies 1996 to 2017 (ceremony numbers 68 to 89),
# each linked to its MovieLens movieId through the IMDb id.
# MovieLens writes the IMDb id without the "tt" prefix, so we add it.
nominees_query = f"""
SELECT
    CAST(o.Year AS INTEGER) + 1 AS ceremony_year,
    CAST(o.Year AS INTEGER) AS film_year,
    o.Film AS title,
    COALESCE(o.Winner = 'True', false) AS is_winner,
    l.movieId
FROM oscars_full o
LEFT JOIN (SELECT movieId, 'tt' || imdbId AS FilmId FROM '{LINKS_FILE}') l
    ON o.FilmId = l.FilmId
WHERE o.CanonicalCategory = 'BEST PICTURE'
  AND CAST(o.Ceremony AS INTEGER) BETWEEN 68 AND 89
ORDER BY ceremony_year, is_winner DESC, title
"""

con.sql(f"COPY ({nominees_query}) TO '{OUTPUT_FILE}' (HEADER, DELIMITER ',')")

# Checks on the file we just wrote: the script stops with a clear message if something is wrong.
n_rows, n_winners, n_with_movieid = con.sql(f"""
SELECT COUNT(*),
       SUM(CASE WHEN is_winner THEN 1 ELSE 0 END),
       COUNT(movieId)
FROM '{OUTPUT_FILE}'
""").fetchone()

assert n_rows == 142, f"Expected 142 nominees, found {n_rows}"
assert n_winners == 22, f"Expected 22 winners, found {n_winners}"
assert n_with_movieid == n_rows, f"{n_rows - n_with_movieid} nominees have no movieId"

print(f"OK: {n_rows} nominees, {n_winners} winners, all linked to a MovieLens movieId.")
print(f"Table written to {OUTPUT_FILE}")
