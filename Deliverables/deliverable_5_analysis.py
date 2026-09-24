import os
import pandas as pd
import matplotlib.pyplot as plt

# ===== 1. Locate and Load Dataset =====
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(SCRIPT_DIR, "christchurch_listings_with_rental_bonds_area_only.csv")

if not os.path.exists(INPUT_PATH):
    INPUT_PATH = os.path.join(SCRIPT_DIR, "Deliverable-5", "christchurch_listings_with_rental_bonds_area_only.csv")

df = pd.read_csv(INPUT_PATH)

# Clean price column if formatted as currency string
if df['price'].dtype == object:
    df['price'] = df['price'].astype(str).str.replace('$', '').str.replace(',', '').astype(float)

# Convert weekly bond rent to daily rate
df['bond_daily_rent'] = df['median_rent'] / 7

# Compute daily price difference ($/night)
df['price_gap'] = df['price'] - df['bond_daily_rent']

# Focus on Top 15 areas by listing count for zoomed views
top_areas = df['area_code'].value_counts().head(15).index
filtered_df = df[df['area_code'].isin(top_areas)].copy()


# ==============================================================================
# QUESTION 1: Median AirBnB Price in Christchurch Central (326600)
# ==============================================================================
central_df = df[df['area_code'] == 326600]
median_central_price = central_df['price'].median()

print("\n--- QUESTION 1 RESULTS ---")
print(f"Median AirBnB Price in Christchurch Central (326600): ${median_central_price:.2f}")


# ==============================================================================
# QUESTION 2A / GRAPH 1A: Price Gap (ALL 50+ SA2 Area Codes)
# ==============================================================================
gap_all = (
    df.groupby('area_code')['price_gap']
    .median()
    .reset_index()
    .sort_values(by='price_gap', ascending=False)
)

plt.figure(figsize=(16, 6))
plt.bar(
    [str(int(a)) for a in gap_all['area_code']], 
    gap_all['price_gap'], 
    color='#2b5c8f', 
    edgecolor='black', 
    alpha=0.85
)

plt.title('Median Nightly Price Gap (AirBnB Rate - Long-Term Rent) - All Christchurch Areas', fontsize=12, fontweight='bold')
plt.xlabel('Location ID (SA2 Area Code)', fontsize=10)
plt.ylabel('Median Price Gap ($ / Night)', fontsize=10)
plt.xticks(rotation=90, fontsize=8)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

plot1_all_path = os.path.join(SCRIPT_DIR, 'bar_price_gap_all_areas.png')
plt.savefig(plot1_all_path, dpi=300)
plt.close()
print(f"Saved: {plot1_all_path}")


# ==============================================================================
# QUESTION 2B / GRAPH 1B: Price Gap (Top 15 Area Codes)
# ==============================================================================
gap_top15 = (
    filtered_df.groupby('area_code')['price_gap']
    .median()
    .reset_index()
    .sort_values(by='price_gap', ascending=False)
)

plt.figure(figsize=(12, 5))
plt.bar(
    [f"Area {int(a)}" for a in gap_top15['area_code']], 
    gap_top15['price_gap'], 
    color='#2b5c8f', 
    edgecolor='black', 
    alpha=0.85
)

plt.title('Median Nightly Price Gap (AirBnB Rate - Long-Term Rent) - Top 15 Areas', fontsize=12, fontweight='bold')
plt.xlabel('Location ID (SA2 Area Code)', fontsize=10)
plt.ylabel('Median Price Gap ($ / Night)', fontsize=10)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.tight_layout()

plot1_top15_path = os.path.join(SCRIPT_DIR, 'bar_price_gap_top15.png')
plt.savefig(plot1_top15_path, dpi=300)
plt.close()
print(f"Saved: {plot1_top15_path}")


# ==============================================================================
# QUESTION 3A / GRAPH 2A: Listing Volume (ALL 50+ SA2 Area Codes)
# ==============================================================================
counts_all = df.groupby('area_code').agg(
    airbnb_count=('id', 'nunique') if 'id' in df.columns else ('price', 'count'),
    active_bonds=('active_bonds', 'first')
).reset_index()

fig, ax = plt.subplots(figsize=(16, 6))
x_all = range(len(counts_all))
width = 0.35

ax.bar([i - width/2 for i in x_all], counts_all['airbnb_count'], width=width, label='AirBnB Listings', color='#ff5a5f')
ax.bar([i + width/2 for i in x_all], counts_all['active_bonds'], width=width, label='Active Rental Bonds', color='#00a699')

ax.set_xticks(x_all)
ax.set_xticklabels([str(int(a)) for a in counts_all['area_code']], rotation=90, fontsize=8)
ax.set_ylabel('Property Count', fontsize=10)
ax.set_xlabel('Location ID (SA2 Area Code)', fontsize=10)
ax.set_title('Listing Volume: AirBnBs vs. Long-Term Rental Bonds (All Christchurch Areas)', fontweight='bold')
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plot2_all_path = os.path.join(SCRIPT_DIR, 'property_counts_all_areas.png')
plt.savefig(plot2_all_path, dpi=300)
plt.close()
print(f"Saved: {plot2_all_path}")


# ==============================================================================
# QUESTION 3B / GRAPH 2B: Listing Volume (Top 15 Area Codes)
# ==============================================================================
counts_top15 = filtered_df.groupby('area_code').agg(
    airbnb_count=('id', 'nunique') if 'id' in filtered_df.columns else ('price', 'count'),
    active_bonds=('active_bonds', 'first')
).reset_index()

fig, ax = plt.subplots(figsize=(12, 5))
x_top = range(len(counts_top15))

ax.bar([i - width/2 for i in x_top], counts_top15['airbnb_count'], width=width, label='AirBnB Listings', color='#ff5a5f')
ax.bar([i + width/2 for i in x_top], counts_top15['active_bonds'], width=width, label='Active Rental Bonds', color='#00a699')

ax.set_xticks(x_top)
ax.set_xticklabels([f"Area {int(a)}" for a in counts_top15['area_code']], rotation=45, ha='right')
ax.set_ylabel('Property Count', fontsize=10)
ax.set_xlabel('Location ID (SA2 Area Code)', fontsize=10)
ax.set_title('Listing Volume: AirBnBs vs. Long-Term Rental Bonds (Top 15 Areas)', fontweight='bold')
ax.legend()
ax.grid(axis='y', linestyle='--', alpha=0.5)

plt.tight_layout()
plot2_top15_path = os.path.join(SCRIPT_DIR, 'property_counts_top15.png')
plt.savefig(plot2_top15_path, dpi=300)
plt.close()
print(f"Saved: {plot2_top15_path}")

print("\nAll 4 charts successfully generated and saved!")