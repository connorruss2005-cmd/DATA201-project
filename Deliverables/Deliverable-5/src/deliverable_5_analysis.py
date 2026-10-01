from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURATION & AUTOMATED REPOSITORY SEARCH
# ==============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[2]  # C:\Users\liang\Data201_project\DATA201-project
FILENAME = "christchurch_listings_with_rental_bonds_area_only.csv"

# Search recursively within the project folder for the dataset
found_files = list(REPO_ROOT.rglob(FILENAME))

if not found_files:
    # Case-insensitive fallback check in case the file extension or name has different casing
    found_files = [p for p in REPO_ROOT.rglob("*.csv") if "christchurch_listings" in p.name.lower()]

if found_files:
    INPUT_PATH = found_files[0]
else:
    raise FileNotFoundError(
        f"Could not locate '{FILENAME}' anywhere inside the project folder ({REPO_ROOT}). "
        "Please check if Deliverable 5's output CSV was generated or moved."
    )

OUTPUT_DIR = INPUT_PATH.parent

# ==============================================================================
# SANITY CHECK & DATA LOADING
# ==============================================================================
def load_and_validate_data(file_path: Path) -> pd.DataFrame:
    """Loads input CSV, cleans numeric types, filters invalid rows, and runs sanity assertions."""
    assert file_path.exists(), f"Error: Input file does not exist at {file_path}"
    
    df = pd.read_csv(file_path)
    
    # 1. Non-empty check
    assert not df.empty, "Error: Loaded dataset is empty."
    
    # 2. Required columns check
    required_cols = {'price', 'median_rent', 'area_code'}
    assert required_cols.issubset(df.columns), f"Error: Missing required columns. Needed: {required_cols}"
    
    # Clean price column if formatted as currency string
    if df['price'].dtype == object:
        df['price'] = df['price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False).astype(float)

    # Sanity Check & Data Filtering for Non-Positive Prices
    initial_count = len(df)
    df = df[(df['price'] > 0) & (df['median_rent'] > 0)].copy()
    dropped_count = initial_count - len(df)
    
    if dropped_count > 0:
        print(f"⚠️ Sanity Audit: Dropped {dropped_count} row(s) with non-positive or zero prices.")

    # 3. Post-filtering assertion check
    assert (df['price'] > 0).all(), "Error: Dataset still contains non-positive values in 'price'."
    assert (df['median_rent'] > 0).all(), "Error: Dataset still contains non-positive values in 'median_rent'."

    # Feature Engineering
    df['bond_daily_rent'] = df['median_rent'] / 7
    df['price_gap'] = df['price'] - df['bond_daily_rent']
    
    print(f"✓ Sanity Check Passed: Data successfully loaded and validated ({len(df)} valid records).")
    return df

# ==============================================================================
# REUSABLE PLOTTING HELPER FUNCTIONS
# ==============================================================================
def plot_price_gap(df: pd.DataFrame, title_suffix: str, output_path: Path, top_n: int = None) -> None:
    """Generates and saves a bar chart representing median nightly price gap per SA2 area."""
    if top_n:
        top_areas = df['area_code'].value_counts().head(top_n).index
        df = df[df['area_code'].isin(top_areas)]
        
    gap_df = (
        df.groupby('area_code')['price_gap']
        .median()
        .reset_index()
        .sort_values(by='price_gap', ascending=False)
    )

    labels = [f"Area {int(a)}" if top_n else str(int(a)) for a in gap_df['area_code']]
    
    plt.figure(figsize=(12 if top_n else 16, 6))
    plt.bar(labels, gap_df['price_gap'], color='#2b5c8f', edgecolor='black', alpha=0.85)
    plt.title(f'Median Nightly Price Gap (AirBnB Rate - Long-Term Rent) - {title_suffix}', fontsize=12, fontweight='bold')
    plt.xlabel('Location ID (SA2 Area Code)', fontsize=10)
    plt.ylabel('Median Price Gap ($ / Night)', fontsize=10)
    plt.xticks(rotation=45 if top_n else 90, ha='right' if top_n else 'center', fontsize=8)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved plot: {output_path.name}")


def plot_listing_volumes(df: pd.DataFrame, title_suffix: str, output_path: Path, top_n: int = None) -> None:
    """Generates and saves a grouped bar chart comparing AirBnB counts vs Active Bonds."""
    if top_n:
        top_areas = df['area_code'].value_counts().head(top_n).index
        df = df[df['area_code'].isin(top_areas)]

    counts = df.groupby('area_code').agg(
        airbnb_count=('id', 'nunique') if 'id' in df.columns else ('price', 'count'),
        active_bonds=('active_bonds', 'first')
    ).reset_index()

    fig, ax = plt.subplots(figsize=(12 if top_n else 16, 6))
    x_coords = range(len(counts))
    width = 0.35

    ax.bar([i - width/2 for i in x_coords], counts['airbnb_count'], width=width, label='AirBnB Listings', color='#ff5a5f')
    ax.bar([i + width/2 for i in x_coords], counts['active_bonds'], width=width, label='Active Rental Bonds', color='#00a699')

    labels = [f"Area {int(a)}" if top_n else str(int(a)) for a in counts['area_code']]
    ax.set_xticks(x_coords)
    ax.set_xticklabels(labels, rotation=45 if top_n else 90, ha='right' if top_n else 'center', fontsize=8)
    ax.set_ylabel('Property Count', fontsize=10)
    ax.set_xlabel('Location ID (SA2 Area Code)', fontsize=10)
    ax.set_title(f'Listing Volume: AirBnBs vs. Long-Term Rental Bonds ({title_suffix})', fontweight='bold')
    ax.legend()
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Saved plot: {output_path.name}")

# ==============================================================================
# MAIN EXECUTION PIPELINE
# ==============================================================================
if __name__ == "__main__":
    df = load_and_validate_data(INPUT_PATH)

    # Question 1: Christchurch Central Median Price
    central_df = df[df['area_code'] == 326600]
    median_central_price = central_df['price'].median()
    print("\n--- QUESTION 1 RESULTS ---")
    print(f"Median AirBnB Price in Christchurch Central (326600): ${median_central_price:.2f}\n")

    # Question 2: Price Gap Visualizations
    plot_price_gap(df, "All Christchurch Areas", OUTPUT_DIR / 'bar_price_gap_all_areas.png')
    plot_price_gap(df, "Top 15 Areas", OUTPUT_DIR / 'bar_price_gap_top15.png', top_n=15)

    # Question 3: Listing Volume Visualizations
    plot_listing_volumes(df, "All Christchurch Areas", OUTPUT_DIR / 'property_counts_all_areas.png')
    plot_listing_volumes(df, "Top 15 Areas", OUTPUT_DIR / 'property_counts_top15.png', top_n=15)