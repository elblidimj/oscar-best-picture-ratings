# Make the two figures of the study from data/processed/film_year_window.csv.
# Run from the project root, after src/build_film_year_table.py:
#   python src/make_figures.py

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from scipy import stats

INPUT_FILE = "data/processed/film_year_window.csv"
FIGURE_1 = "reports/figures/q1_winner_vs_other_nominees.png"
FIGURE_2 = "reports/figures/q2_rank_of_the_winner.png"

# Colours: paper background, dark ink, one warm and one cool colour (checked for colour-blind readers)
PAPER, INK, MUTED, GRID = "#F5F0E6", "#1D1B18", "#6B655B", "#DDD5C5"
BRICK, TEAL = "#B3283C", "#0B939E"
SOURCE = "Source: MovieLens 32M ratings; Academy Awards Database (via Kaggle). Window: ceremony year to ceremony year + 5."

plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "font.family": "Avenir", "font.size": 10.5, "text.color": INK,
    "axes.edgecolor": MUTED, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
})


def title_block(fig, title, subtitle):
    fig.text(0.06, 0.945, title, fontsize=19, fontfamily="Georgia", fontweight="bold", ha="left", va="top")
    fig.text(0.06, 0.875, subtitle, fontsize=10.5, color=MUTED, ha="left", va="top")


def footer(fig, note):
    fig.text(0.06, 0.035, note + "\n" + SOURCE, fontsize=8, color=MUTED, ha="left", va="bottom", linespacing=1.5)


# ---------- data ----------
table = pd.read_csv(INPUT_FILE)
films = table[["movieId", "title", "ceremony_year", "is_winner"]].drop_duplicates()

# Slope of the yearly average rating for each film (weighted by the number of ratings)
slopes = []
for movie_id, rows in table.groupby("movieId"):
    X = sm.add_constant(rows["years_since_ceremony"])
    fit = sm.WLS(rows["avg_rating"], X, weights=rows["nb_ratings"]).fit()
    slopes.append({"movieId": movie_id, "slope": fit.params["years_since_ceremony"]})
slopes = films.merge(pd.DataFrame(slopes), on="movieId")

# One difference per ceremony: slope of the winner minus mean slope of the other nominees
differences = []
for ceremony, group in slopes.groupby("ceremony_year"):
    winner = group[group["is_winner"]].iloc[0]
    others = group[~group["is_winner"]]
    differences.append({"ceremony_year": ceremony, "title": winner["title"],
                        "difference": winner["slope"] - others["slope"].mean()})
differences = pd.DataFrame(differences)

# Normalised rank of every nominee in every year (1 = best rated of its ceremony, 0 = worst)
group = table.groupby(["ceremony_year", "years_since_ceremony"])
table["rank"] = group["avg_rating"].rank(ascending=False, method="average")
table["n_nominees"] = group["title"].transform("count")
table["normalised_rank"] = (table["n_nominees"] - table["rank"]) / (table["n_nominees"] - 1)
winner_ranks = table[table["is_winner"]].pivot(index="ceremony_year", columns="years_since_ceremony", values="normalised_rank")

# Numbers quoted in the figures: they must match the notebook
mean_difference = differences["difference"].mean()
test = stats.ttest_1samp(differences["difference"], 0)
ci_low, ci_high = test.confidence_interval(confidence_level=0.95)
n_below = int((differences["difference"] < 0).sum())
assert abs(mean_difference - (-0.0137)) < 0.0001, mean_difference
assert abs(winner_ranks[0].mean() - 0.738) < 0.001 and abs(winner_ranks[5].mean() - 0.643) < 0.001


# ---------- figure 1: one difference per ceremony ----------
fig, ax = plt.subplots(figsize=(10.5, 6.6))
fig.subplots_adjust(left=0.07, right=0.97, top=0.76, bottom=0.2)
title_block(fig, "Winners did not hold their ratings better than their fellow nominees",
            "Slope of the winner's average rating minus the mean slope of the other nominees, one dot per ceremony (rating points per year)")

x, y = differences["ceremony_year"], differences["difference"]
colours = [BRICK if v < 0 else TEAL for v in y]
ax.axhline(0, color=INK, linewidth=1.2, zorder=1)
ax.vlines(x, 0, y, colors=colours, linewidth=2, zorder=2)
ax.scatter(x, y, s=75, c=colours, edgecolors=PAPER, linewidths=2, zorder=3)
ax.hlines(mean_difference, 1995.4, 2017.5, colors=INK, linewidth=1, linestyles=(0, (4, 3)), zorder=1)
ax.text(2017.7, mean_difference, f"mean\n{mean_difference:+.3f}", ha="left", va="center", fontsize=9.5, color=INK)

# label the most extreme ceremonies: the text runs along the stem, to the right of it
for _, row in differences.iterrows():
    if abs(row["difference"]) > 0.03:
        if row["difference"] < 0:
            ax.text(row["ceremony_year"] + 0.15, row["difference"] + 0.003, row["title"], rotation=90,
                    ha="left", va="bottom", fontsize=9, color=MUTED)
        else:
            ax.text(row["ceremony_year"], row["difference"] + 0.004, row["title"],
                    ha="center", va="bottom", fontsize=9, color=MUTED)

ax.text(1995.6, 0.043, "above zero: the winner held up better", fontsize=10.5, color=TEAL, va="center")
ax.text(1995.6, -0.103, "below zero: the winner's rating fell faster", fontsize=10.5, color=BRICK, va="center")
ax.set_xlim(1995.4, 2019.2)
ax.set_ylim(-0.11, 0.05)
ax.set_xticks(range(1996, 2018, 2))
ax.set_yticks([-0.1, -0.05, 0, 0.05])
ax.yaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.set_xlabel("Year of the ceremony")
footer(fig, f"Mean difference {mean_difference:+.3f} per year (95% interval {ci_low:+.3f} to {ci_high:+.3f}); the winner is below its co-nominees in {n_below} of 22 ceremonies. "
            "No clear evidence of an effect.")
fig.savefig(FIGURE_1, dpi=200)
plt.close(fig)

# ---------- figure 2: rank of the winner, year by year ----------
fig, ax = plt.subplots(figsize=(10.5, 6.6))
fig.subplots_adjust(left=0.08, right=0.8, top=0.79, bottom=0.2)
title_block(fig, "Winners start high in their ceremony, then settle closer to the middle",
            "Normalised rank of the winner among the nominees of its ceremony (1 = best rated, 0 = worst, 0.5 = middle), by years since the ceremony")

years = list(range(6))
for _, trajectory in winner_ranks.iterrows():
    ax.plot(years, trajectory.values, color=MUTED, alpha=0.11, linewidth=1, zorder=1)

means = winner_ranks.mean()
sem = winner_ranks.sem()
margin = stats.t.ppf(0.975, len(winner_ranks) - 1) * sem
ax.fill_between(years, means - margin, means + margin, color=BRICK, alpha=0.12, linewidth=0, zorder=2)
ax.plot(years, means, color=BRICK, linewidth=2.5, zorder=3)
ax.scatter(years, means, s=70, color=BRICK, edgecolors=PAPER, linewidths=2, zorder=4)
ax.hlines(0.5, -0.35, 5.1, colors=INK, linewidth=1, linestyles=(0, (4, 3)), zorder=1)

ax.text(5.15, means[5], f"winners, mean\n{means[5]:.2f}", color=BRICK, fontsize=10, fontweight="bold", va="center")
ax.text(5.15, 0.5, "middle of the ceremony\n(chance level)", color=INK, fontsize=9.5, va="center")
ax.text(5.15, 0.17, "each grey line =\none ceremony's winner", color=MUTED, fontsize=9, va="center")
ax.annotate(f"{means[0]:.2f}", (0, means[0]), xytext=(-6, 10), textcoords="offset points", ha="right", fontsize=10, color=BRICK, fontweight="bold")
ax.set_xlim(-0.35, 5.2)
ax.set_ylim(-0.02, 1.04)
ax.set_xticks(years)
ax.set_xticklabels(["ceremony\nyear"] + [f"+{i}" for i in range(1, 6)])
ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
ax.yaxis.grid(True, color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
ax.set_xlabel("Years since the ceremony")
footer(fig, f"Mean rank {means[0]:.2f} in the ceremony year and {means[5]:.2f} five years later; the shaded band is the 95% interval of the mean. "
            "Most of the drop happens in the first year after the ceremony.")
fig.savefig(FIGURE_2, dpi=200)
plt.close(fig)

print(f"Figures written to {FIGURE_1} and {FIGURE_2}")
