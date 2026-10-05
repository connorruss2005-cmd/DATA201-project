from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURATION & REPOSITORY FILE SEARCH
# ==============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2] if len(SCRIPT_DIR.parents) >= 3 else SCRIPT_DIR
FILENAME = "listings_1_updated.csv"

# Locate dataset dynamically anywhere in the project tree
found_files = list(REPO_ROOT.rglob(FILENAME)) if REPO_ROOT.exists() else []
if not found_files:
    found_files = list(SCRIPT_DIR.rglob(FILENAME)) + list(Path.cwd().rglob(FILENAME))

INPUT_PATH = found_files[0] if found_files else SCRIPT_DIR / FILENAME
OUTPUT_DIR = INPUT_PATH.parent

# ==============================================================================
# DATA LOADING & SANITY CHECKS
# ==============================================================================
def load_and_validate_listings(file_path: Path) -> pd.DataFrame:
    """Loads raw listings dataset and validates required columns and numeric integrity."""
    assert file_path.exists(), f"Error: Dataset not found at {file_path}"
    
    df = pd.read_csv(file_path, encoding='latin1')
    
    # 1. Non-empty check
    assert not df.empty, "Error: Loaded dataset is empty."
    
    # 2. Required columns check
    required_cols = {'price', 'neighbourhood_group', 'last_review', 'number_of_reviews'}
    assert required_cols.issubset(df.columns), f"Error: Missing columns. Required: {required_cols}"
    
    # Clean price column if formatted as string currency
    if df['price'].dtype == object:
        df['price'] = df['price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)

    # 3. Non-negative values assertions
    assert (df['price'].dropna() >= 0).all(), "Error: Negative price values found."
    assert (df['number_of_reviews'].dropna() >= 0).all(), "Error: Negative review counts found."

    print(f"✓ Sanity Check Passed: Successfully loaded {len(df)} rows from {file_path.name}")
    return df

# ==============================================================================
# ANALYSIS & PLOTTING FUNCTIONS
# ==============================================================================
def plot_price_distributions(df: pd.DataFrame, output_dir: Path) -> None:
    """Generates price distribution histograms for All NZ vs Christchurch City."""
    price_all = df['price'].dropna()
    price_chch = df.loc[df['neighbourhood_group'] == 'Christchurch City', 'price'].dropna()

    print(f"\nAll NZ price: n={len(price_all)}, median={price_all.median():.0f}, mean={price_all.mean():.0f}")
    print(f"Christchurch price: n={len(price_chch)}, median={price_chch.median():.0f}, mean={price_chch.mean():.0f}")

    # Capped at 99th percentile to prevent extreme outliers from compressing the plots
    upper_cutoff = price_all.quantile(0.99)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Left: All NZ
    axes[0].hist(price_all[price_all <= upper_cutoff], bins=50, color='#2b6cb0', edgecolor='white')
    axes[0].set_title(f'Price Distribution — All New Zealand\n(n={len(price_all)}, capped at 99th pct = ${upper_cutoff:.0f})')
    axes[0].set_xlabel('Price (NZD per night)')
    axes[0].set_ylabel('Number of listings')

    # Right: Christchurch City
    axes[1].hist(price_chch[price_chch <= upper_cutoff], bins=50, color='#c05621', edgecolor='white')
    axes[1].set_title(f'Price Distribution — Christchurch City\n(n={len(price_chch)}, capped at ${upper_cutoff:.0f})')
    axes[1].set_xlabel('Price (NZD per night)')
    axes[1].set_ylabel('Number of listings')

    plt.tight_layout()
    out_path = output_dir / 'price_distribution.png'
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved plot: {out_path.name}")


def plot_review_recency(df: pd.DataFrame, output_dir: Path) -> None:
    """Calculates days since last review relative to the reference date and plots recency."""
    df['last_review_dt'] = pd.to_datetime(df['last_review'], errors='coerce')
    reference_date = df['last_review_dt'].max()
    
    if pd.isna(reference_date):
        reference_date = pd.Timestamp.today()

    print(f"\nReference date used for 'days ago' calc: {reference_date.date()}")

    df['days_since_last_review'] = (reference_date - df['last_review_dt']).dt.days
    days_since = df['days_since_last_review'].dropna()

    print(f"Listings with a review date: {len(days_since)} / {len(df)}")
    print(f"Median days since last review: {days_since.median():.0f}")

    plt.figure(figsize=(9, 5.5))
    plt.hist(days_since, bins=60, color='#2f855a', edgecolor='white')
    plt.title(f'Days Since Last Review (n={len(days_since)} listings with a review)')
    plt.xlabel('Days since last review')
    plt.ylabel('Number of listings')
    plt.tight_layout()
    
    out_path = output_dir / 'days_since_last_review.png'
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"Saved plot: {out_path.name}")


def export_top_reviewed(df: pd.DataFrame, output_dir: Path) -> None:
    """Identifies top 10% most-reviewed listings and exports them to CSV."""
    threshold = df['number_of_reviews'].quantile(0.90)
    top10 = df[df['number_of_reviews'] >= threshold].sort_values('number_of_reviews', ascending=False)

    print(f"\nTop 10% cutoff: number_of_reviews >= {threshold:.0f}")
    print(f"Number of listings in top 10%: {len(top10)}")

    cols_to_show = ['id', 'name', 'neighbourhood_group', 'neighbourhood', 'room_type', 'price', 'number_of_reviews']
    available_cols = [c for c in cols_to_show if c in top10.columns]
    
    top10_out = top10[available_cols]
    csv_path = output_dir / 'top_10_percent_reviewed_listings.csv'
    top10_out.to_csv(csv_path, index=False)
    
    print(f"Saved top-reviewed listings to {csv_path.name}")
    print("\nTop 15 most-reviewed listings preview:")
    print(top10_out.head(15).to_string(index=False))

# ==============================================================================
# MAIN PIPELINE EXECUTION
# ==============================================================================
if __name__ == '__main__':
    df = load_and_validate_listings(INPUT_PATH)
    plot_price_distributions(df, OUTPUT_DIR)
    plot_review_recency(df, OUTPUT_DIR)
    export_top_reviewed(df, OUTPUT_DIR)