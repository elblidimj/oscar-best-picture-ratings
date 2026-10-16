# Do Oscar-Winning Movies Age Better?

A data science study based on MovieLens 32M ratings and Best Picture Oscar records.

## Research questions

1. Do Best Picture winners maintain their audience ratings better over time than nominated films that did not win?
2. Does the position of the Best Picture winner among the nominees of its ceremony (ranked by average rating) improve, stay or get worse over the years after the ceremony?

## Status

Work in progress. Done: data exploration, link between the Oscar nominees and MovieLens movies, yearly rating table for the analysis window. To do: summary measure of each film's rating trajectory, comparison of winners with the other nominees (Q1), ranking within each ceremony (Q2), robustness checks, figures.

## Study design

- **Population**: all Best Picture nominees of the ceremonies 1996 to 2017 (142 films, 22 winners). MovieLens starts in 1995 and its last full year is 2022.
- **Link between the two sources**: each nominee is matched to its MovieLens `movieId` through its IMDb id (all 142 found), then checked against the titles and years.
- **Analysis window (under discussion)**: from the ceremony year to the ceremony year + 5 (6 calendar years). Every nominee was released the year before the ceremony, so the ceremony year is the first complete calendar year after release.
- **Measure**: average rating per film and per year of rating (UTC), with the number of ratings. The minimum number of ratings per film and year is under discussion (candidates: 50, with 100 as a robustness check).
- **Comparison**: each winner is compared with the nominees of the same ceremony, because the number of nominees changes from 5 to 10.

Working assumption: a rating given in year *t* is treated as a viewing in year *t* (see Limitations).

## Setup

Requires Python 3.9+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Data

The data is not stored in this repository (see `.gitignore`). Create the folder `data/raw/` and place the datasets there:

- MovieLens 32M: download `ml-32m.zip` from https://grouplens.org/datasets/movielens/ and unzip it so that the files are in `data/raw/ml-32m/` (e.g. `data/raw/ml-32m/ratings.csv`). Ratings range from 1995-01-09 to 2023-10-13.
- Academy Awards nominees and winners: Kaggle dataset "The Oscar Award, 1927 - 2026" (`unanimad/the-oscar-award`, a scrape of the official Academy Awards Database), https://www.kaggle.com/datasets/unanimad/the-oscar-award. Downloaded on 2026-10-15 and unzipped into `data/raw/oscar_archive_1927_2025/` (files `the_oscar_award.csv` and `full_data.csv`). Best Picture nominees were compared with the official database (ceremonies 1996 to 2015) and with Wikipedia (2016 and 2017).

## How to reproduce

Run the notebooks in this order from the `notebooks/` folder (each one is read-only on `data/raw/`):

| Notebook | What it does | Output |
|---|---|---|
| `01_explore_movielens.ipynb` | first look at MovieLens (size, period, scale, titles) | none |
| `02_explore_oscars.ipynb` | first look at the Oscars file, how Best Picture is labelled | none |
| `03_match_oscars_movielens.ipynb` | links the 142 nominees to MovieLens by IMDb id and checks the match | `data/processed/best_picture_nominees_1996_2017.csv` |
| `04_yearly_ratings.ipynb` | number of ratings and average rating per film and year (work in progress: the analysis window and the minimum number of ratings are being discussed again) | none for now |

## Scripts

From the project root, once the raw data is in `data/raw/`:

```bash
.venv/bin/python src/build_nominees_table.py    # writes data/processed/best_picture_nominees_1996_2017.csv
```

The script stops with an error message if the table does not have 142 nominees, 22 winners and a MovieLens `movieId` for every film. More scripts will be added as the steps of the notebooks become stable.

## Project structure

```
data/raw/        original downloaded data, never modified
data/processed/  tables produced by the notebooks
notebooks/       exploration and data preparation
src/             scripts that rebuild the processed tables
reports/figures/ final figures (empty for now)
```

## Limitations (to keep in mind)

- MovieLens users are not representative of all moviegoers.
- A rating timestamp records when a rating was submitted, not necessarily when the film was watched. Some users rate many films at the same second (bulk rating), which suggests ratings of films seen long before.
- The audience that rates a film changes over time, so a change in the average rating does not necessarily mean that the film changed.
- Only 22 winners are available, so the study has limited statistical power.
- A very popular film may be rated by a different audience than a little-known one. This is a bias, not noise, and weighting by the number of ratings does not remove it. Each winner is compared with the nominees of the same ceremony, and we check whether popularity (total number of ratings) explains the differences. It remains a limitation of the study.
