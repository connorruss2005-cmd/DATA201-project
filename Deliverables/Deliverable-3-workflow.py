import pandas as pd
import matplotlib.pyplot as plt


# Load data
###I loaded the dataset and checked the number of rows and columns.
df = pd.read_csv('listings1.csv', encoding='latin1')
print("Rows, cols:", df.shape)


# 1. Price distribution histograms
### Then, I created two price distributions. One shows prices for all New Zealand listings, and the other shows only Christchurch City listings. Because there are some very large price outliers, I used the 99th percentile as an upper limit so that the main distribution is easier to see.
# Drop missing prices, and clip extreme outliers for a readable plot
price_all = df['price'].dropna()
# Filter for Christchurch City listings
price_chch = df.loc[df['neighbourhood_group'] == 'Christchurch City', 'price'].dropna()

# Print some quick summary stats to the console so we have numbers to sanity check
# the plots against (median is more robust to outliers than mean here).
print(f"\nAll NZ price: n={len(price_all)}, median={price_all.median():.0f}, mean={price_all.mean():.0f}")
print(f"Christchurch price: n={len(price_chch)}, median={price_chch.median():.0f}, mean={price_chch.mean():.0f}")

# Use a sensible upper cutoff (99th percentile of all-NZ prices) so extreme
# outliers don't crush the histogram bars
upper_cutoff = price_all.quantile(0.99)

# Create a figure with two side-by-side plots (1 row, 2 columns)
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left plot is for all of New Zealand listings
axes[0].hist(price_all[price_all <= upper_cutoff], bins=50, color='#2b6cb0', edgecolor='white')
axes[0].set_title(f'Price Distribution — All of New Zealand\n(n={len(price_all)}, capped at 99th pct = ${upper_cutoff:.0f})')
axes[0].set_xlabel('Price (NZD per night)')
axes[0].set_ylabel('Number of listings')

# Right plot is for Christchurch City listings only
axes[1].hist(price_chch[price_chch <= upper_cutoff], bins=50, color='#c05621', edgecolor='white')
axes[1].set_title(f'Price Distribution — Christchurch City\n(n={len(price_chch)}, capped at ${upper_cutoff:.0f})')
axes[1].set_xlabel('Price (NZD per night)')
axes[1].set_ylabel('Number of listings')

# Avoid titles/labels overlapping with each other
plt.tight_layout()
plt.savefig('price_distribution.png', dpi=150)
# Freeing up memory for the next plot
plt.close()
print("Saved price_distribution.png")

# ---------------------------------------------------------
# 2. Days since last review
# ---------------------------------------------------------
### Next, I analysed the number of days since the last review. I converted the last_review column into a date format and calculated the difference between the reference date and each listing's last review date. Then, I created a histogram to show the distribution.
# Convert last_review to datetime, coercing errors to NaT (missing)
df['last_review_dt'] = pd.to_datetime(df['last_review'], errors='coerce')

# "Today" = the most recent date found in the dataset (proxy for scrape date),
# falls back to today's real date if that fails
reference_date = df['last_review_dt'].max()
if pd.isna(reference_date):
    reference_date = pd.Timestamp.today()
print(f"\nReference date used for 'days ago' calc: {reference_date.date()}")

# Subtract each listing's last review date from the reference date.
# .dt.days converts the resulting Timedelta into a plain integer number of days.
df['days_since_last_review'] = (reference_date - df['last_review_dt']).dt.days

# Drop listings that never received a review (their date was NaT, so this
# calculation is NaN) — there's nothing to plot for those.
days_since = df['days_since_last_review'].dropna()
print(f"Listings with a review date: {len(days_since)} / {len(df)}")
print(f"Median days since last review: {days_since.median():.0f}")

# Plot the distribution: most listings should cluster at lower values 
plt.figure(figsize=(9, 5.5))
plt.hist(days_since, bins=60, color='#2f855a', edgecolor='white')
plt.title(f'Days Since Last Review (n={len(days_since)} listings with a review)')
plt.xlabel('Days since last review')
plt.ylabel('Number of listings')
plt.tight_layout()
plt.savefig('days_since_last_review.png', dpi=150)
plt.close()
print("Saved days_since_last_review.png")


# 3. Top 10% of properties by number of reviews
### Finally, I identified the top 10 percent of properties based on the number of reviews. I calculated the 90th percentile as the cutoff and selected listings with review counts equal to or higher than that value. I also saved these listings into a new CSV file for further analysis.

# quantile(0.90) finds the review-count value BELOW which 90% of listings fall
threshold = df['number_of_reviews'].quantile(0.90)
top10 = df[df['number_of_reviews'] >= threshold].sort_values('number_of_reviews', ascending=False)

print(f"\nTop 10% cutoff: number_of_reviews >= {threshold:.0f}")
print(f"Number of listings in top 10%: {len(top10)}")

# shows columns of intrest in the output CSV, and in the console printout
cols_to_show = ['id', 'name', 'neighbourhood_group', 'neighbourhood',
                 'room_type', 'price', 'number_of_reviews']
top10_out = top10[cols_to_show]

# Save the full top-10% list to CSV so it can be explored outside Python
top10_out.to_csv('top_10pct_most_reviewed.csv', index=False)
print("Saved top_10pct_most_reviewed.csv")

# Also print just the top 15 to the console as a quick preview.
print("\nTop 15 most-reviewed listings in NZ:")
print(top10_out.head(15).to_string(index=False))