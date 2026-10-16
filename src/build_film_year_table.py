# Build the table "one row per nominee and per year of rating" inside the analysis window.
# Window: from the ceremony year to the ceremony year + 5 (6 calendar years), the same for every film.
# Run from the project root, after src/build_nominees_table.py:
#   python src/build_film_year_table.py

import duckdb

NOMINEES_FILE = "data/processed/best_picture_nominees_1996_2017.csv"
RATINGS_FILE = "data/raw/ml-32m/ratings.csv"
OUTPUT_FILE = "data/processed/film_year_window.csv"
OUTPUT_FILE_LONG = "data/processed/film_year_until_2022.csv"
YEARS_AFTER_CEREMONY = 5
LAST_FULL_YEAR = 2022   # the ratings stop on 2023-10-13, so 2023 is an incomplete year

con = duckdb.connect()

# For each nominee and each year of rating (UTC): number of ratings and average rating.
# Then we keep only the years we want and add the number of years since the ceremony.
def film_year_query(year_filter):
    return f"""
SELECT *, rating_year - ceremony_year AS years_since_ceremony
FROM (
    SELECT n.ceremony_year, n.title, n.is_winner, n.movieId,
           year(to_timestamp(r.timestamp) AT TIME ZONE 'UTC') AS rating_year,
           COUNT(*) AS nb_ratings,
           ROUND(AVG(r.rating), 2) AS avg_rating
    FROM '{NOMINEES_FILE}' n
    JOIN '{RATINGS_FILE}' r ON n.movieId = r.movieId
    GROUP BY n.ceremony_year, n.title, n.is_winner, n.movieId, rating_year
)
WHERE {year_filter}
ORDER BY ceremony_year, title, rating_year
"""

# Main window: from the ceremony year to the ceremony year + 5.
con.sql(f"COPY ({film_year_query(f'rating_year BETWEEN ceremony_year AND ceremony_year + {YEARS_AFTER_CEREMONY}')}) TO '{OUTPUT_FILE}' (HEADER, DELIMITER ',')")

# Complementary analysis: from the ceremony year to the last complete year (2022).
con.sql(f"COPY ({film_year_query(f'rating_year BETWEEN ceremony_year AND {LAST_FULL_YEAR}')}) TO '{OUTPUT_FILE_LONG}' (HEADER, DELIMITER ',')")

# Checks on the file we just wrote: the script stops with a clear message if something is wrong.
n_rows, n_films, n_years = con.sql(f"""
SELECT COUNT(*), COUNT(DISTINCT movieId), COUNT(DISTINCT years_since_ceremony)
FROM '{OUTPUT_FILE}'
""").fetchone()

assert n_films == 142, f"Expected 142 films, found {n_films}"
assert n_years == YEARS_AFTER_CEREMONY + 1, f"Expected {YEARS_AFTER_CEREMONY + 1} years per film, found {n_years}"
assert n_rows == n_films * (YEARS_AFTER_CEREMONY + 1), f"Expected {n_films * (YEARS_AFTER_CEREMONY + 1)} rows, found {n_rows}"

n_rows_long, n_films_long, last_year = con.sql(f"""
SELECT COUNT(*), COUNT(DISTINCT movieId), MAX(rating_year) FROM '{OUTPUT_FILE_LONG}'
""").fetchone()
assert n_films_long == 142, f"Expected 142 films in the long table, found {n_films_long}"
assert last_year == LAST_FULL_YEAR, f"Expected the last year to be {LAST_FULL_YEAR}, found {last_year}"

print(f"OK: {n_rows} rows ({n_films} films x {n_years} years).")
print(f"Table written to {OUTPUT_FILE}")
print(f"OK: {n_rows_long} rows, ceremony year to {last_year}.")
print(f"Table written to {OUTPUT_FILE_LONG}")
