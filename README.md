# Do Oscar-Winning Movies Age Better?

A data science study based on MovieLens 32M ratings and Best Picture Oscar records.

## Research questions

1. Do Best Picture winners maintain their audience ratings better over time than nominated films that did not win?
2. Do Best Picture winners remain the highest-rated films among their fellow nominees years after the ceremony?

## Status

Work in progress: project setup done, data collection not started.

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
- Academy Awards nominees and winners: Kaggle dataset "The Oscar Award, 1927 - 2026" (`unanimad/the-oscar-award`, a scrape of the official Academy Awards Database), https://www.kaggle.com/datasets/unanimad/the-oscar-award. Downloaded on 2026-10-15 and unzipped into `data/raw/oscar_archive_1927_2025/` (files `the_oscar_award.csv` and `full_data.csv`). Content to be checked against the official database at https://awardsdatabase.oscars.org/.

## Project structure

```
data/raw/        original downloaded data, never modified
data/processed/  cleaned and merged data produced by our code
notebooks/       exploration
src/             reusable scripts
reports/figures/ final figures
```

## Limitations (to keep in mind)

MovieLens users are not representative of all moviegoers, and a rating timestamp records when a rating was submitted, not necessarily when the film was watched.
