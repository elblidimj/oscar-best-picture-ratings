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

- MovieLens 32M: download from https://grouplens.org/datasets/movielens/ (to be completed)
- Best Picture nominees and winners: source to be decided

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
