# Preprocess Inside Airbnb listing snapshots for Christchurch.
# Discover new monthly files automatically and run from the command line:
#   python Deliverable-3.py
#
# Also be sure the listings CSV files are in Deliverable-3/Data/.

# This is a new and improved version of the old Deliverable-3.py script, which was a bit messy and hard to read. This new version is more modular, with functions for each step of the process, and it uses argparse to allow the user to specify the data and output directories. 
# It also handles older numbered snapshots (listings1.csv ... listings9.csv) and newer dated snapshots (listings-13th-July-2026.csv) automatically.
# Any new listing.csv file must be in the Deliverable-3/Data/ directory, and the script will automatically detect it and process it. The output will be saved in Deliverable-3/Output/Updated_listings/ and Deliverable-3/Output/combined_listings_for_Christchurch/.
# The function that handles the processing is preprocess_new_months(), which is called at the end of the script. It will discover all the listings files, preprocess them, and combine them into one dataset. It will also print some summary statistics about the combined dataset.

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
DELIVERABLE_DIR = SCRIPT_DIR.parent
DEFAULT_DATA_DIR = DELIVERABLE_DIR / "Data"
DEFAULT_OUTPUT_DIR = DELIVERABLE_DIR / "Output"
UPDATED_DIR_NAME = "Updated_listings"
COMBINED_DIR_NAME = "combined_listings_for_Christchurch"
COMBINED_FILENAME = "combined_Christchurch_listings.csv"

# Older snapshots were named listings1.csv ... listings9.csv
NUMBERED_SNAPSHOT_MONTHS = {
    1: "October 2025",
    2: "November 2025",
    3: "December 2025",
    4: "January 2026",
    5: "February 2026",
    6: "March 2026",
    7: "April 2026",
    8: "May 2026",
    9: "June 2026",
}

MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
MONTH_PATTERN = "|".join(MONTH_NAMES)

# listings-13th-August-2026.csv, listings_July_2026.csv, listings August 2026.csv
DATED_FILENAME_RE = re.compile(
    rf"(?:(\d{{1,2}})(?:st|nd|rd|th)[-_ ]?)?({MONTH_PATTERN})[-_ ](\d{{4}})",
    re.IGNORECASE,
)
# compile a regex to match older numbered snapshots (listings1.csv ... listings9.csv)
NUMBERED_FILENAME_RE = re.compile(r"^listings[-_]?(\d+)$", re.IGNORECASE)


def parse_scrape_month(path: Path) -> str | None:
    """Return a scrape month label such as 'July 2026' from a listings filename."""
    stem = path.stem.strip()
    # Try to parse a month and year from the filename using regexes.
    dated_match = DATED_FILENAME_RE.search(stem.replace(" ", "-"))
    if dated_match:
        month_name = dated_match.group(2).capitalize()
        year = dated_match.group(3)
        return f"{month_name} {year}"
    # Older numbered snapshots (listings1.csv ... listings9.csv) don't have a month in the filename, so we have to map them to a month manually.
    numbered_match = NUMBERED_FILENAME_RE.fullmatch(stem)
    if numbered_match:
        snapshot_number = int(numbered_match.group(1))
        return NUMBERED_SNAPSHOT_MONTHS.get(snapshot_number)

    return None


def discover_listing_files(data_dir: Path) -> list[tuple[Path, str]]:
    """Find listings CSV files and attach a scrape month parsed from each filename."""
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    # Find all listings*.csv files in the data directory and sort them by filename.
    discovered: list[tuple[Path, str]] = []
    for path in sorted(data_dir.glob("listings*.csv")):
        scrape_month = parse_scrape_month(path)
        if scrape_month is None:
            print(
                f"Skipping {path.name}: could not detect a scrape month from the filename."
            )
            continue
        discovered.append((path, scrape_month))
    # If no files were found, raise an error.
    if not discovered:
        raise FileNotFoundError(
            f"No dated listings CSV files found in {data_dir}. "
            "Expected names such as listings-13th-July-2026.csv."
        )

    return discovered


def preprocess_listing_file(path: Path, scrape_month: str) -> pd.DataFrame:
    """Filter to Christchurch City and tag rows with the snapshot scrape month."""
    required_columns = {"neighbourhood_group", "last_review"}
    df = pd.read_csv(path, encoding="latin1")
    # Check that the required columns are present in the dataframe.
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"{path.name} is missing required columns: {sorted(missing_columns)}")
    # Filter to Christchurch City and tag rows with the snapshot scrape month.
    df = df[df["neighbourhood_group"] == "Christchurch City"].copy()
    df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")
    df["month_year"] = scrape_month
    df["source_file"] = path.name
    return df

# Helper function to create a slug for the month
def _month_slug(scrape_month: str) -> str:
    return scrape_month.lower().replace(" ", "_")

# Helper function to normalise the 'id' column
def _normalise_id(df: pd.DataFrame) -> pd.DataFrame:
    if "id" not in df.columns:
        return df
    df = df.copy()
    df["id"] = (
        df["id"]
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
    )
    return df

# Helper function to combine listings from multiple months
def combine_listings(data_sets: list[pd.DataFrame], existing_combined: Path | None) -> pd.DataFrame:
    new_months = _normalise_id(pd.concat(data_sets, ignore_index=True))
    new_months = new_months.drop_duplicates(subset=["id", "month_year"])

    # If there is no existing combined dataset, or if it doesn't exist on disk, return the new months as the combined dataset.
    if existing_combined is None or not existing_combined.exists():
        return new_months.reset_index(drop=True)
    # If there is an existing combined dataset, load it and remove any rows that have the same month_year as the new months, then concatenate the new months to the existing dataset.
    existing = _normalise_id(pd.read_csv(existing_combined))
    months_being_refreshed = set(new_months["month_year"].dropna().unique())
    existing = existing[~existing["month_year"].isin(months_being_refreshed)]
    combined = pd.concat([existing, new_months], ignore_index=True)
    return combined.reset_index(drop=True)

# Helper function to print summary statistics for numeric columns
def print_column_summaries(df: pd.DataFrame) -> None:
    numeric_summary = df.select_dtypes(include="number").describe().T
    numeric_summary["missing"] = df[numeric_summary.index].isna().sum()
    print("\nNUMERIC COLUMNS")
    print(numeric_summary)

def preprocess_new_months(data_dir: Path | None = None, output_dir: Path | None = None,) -> Path:
    """Discover every dated listings file and preprocess them in one call."""
    data_dir = Path(data_dir) if data_dir is not None else DEFAULT_DATA_DIR
    output_dir = Path(output_dir) if output_dir is not None else DEFAULT_OUTPUT_DIR
    updated_dir = output_dir / UPDATED_DIR_NAME
    combined_dir = output_dir / COMBINED_DIR_NAME
    updated_dir.mkdir(parents=True, exist_ok=True)
    combined_dir.mkdir(parents=True, exist_ok=True)

    # Discover and preprocess new monthly listings files
    discovered = discover_listing_files(data_dir)
    print("Detected listing snapshots:")
    for path, scrape_month in discovered:
        print(f"  {path.name} -> {scrape_month}")

    # Preprocess each discovered file and save the filtered Christchurch rows to the updated directory.
    processed = []
    for path, scrape_month in discovered:
        df = preprocess_listing_file(path, scrape_month)
        updated_path = updated_dir / f"listings_{_month_slug(scrape_month)}_updated.csv"
        df.to_csv(updated_path, index=False)
        print(f"Saved {len(df)} Christchurch rows to {updated_path.name}")
        processed.append(df)
    
    # Combine all the processed monthly datasets into one combined dataset and save it to the combined directory.
    combined_path = combined_dir / COMBINED_FILENAME
    combined = combine_listings(processed, combined_path)
    combined.to_csv(combined_path, index=False)
    print(f"\nCombined dataset saved to {combined_path}")
    print(combined["month_year"].value_counts(dropna=False).sort_index())
    print_column_summaries(combined)
    return combined_path


def parse_args() -> argparse.Namespace:
    # Parse command line arguments for the script.
    parser = argparse.ArgumentParser(
        description="Auto-detect and preprocess new monthly Airbnb listings files."
    ) 
    # Add arguments for data directory and output directory with default values.
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Folder containing listings*.csv files (default: Deliverable-3/Data).",
    )
    # Add argument for output directory with default value.
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Folder for updated and combined CSV outputs.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    preprocess_new_months(data_dir=args.data_dir, output_dir=args.output_dir)
