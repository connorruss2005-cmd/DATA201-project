# DATA201 Project – Deliverable 4

## Christchurch Rental Data Cleaning and Preparation

### 1. Project Overview

Deliverable 4 prepares two datasets for the next stage of the project:

1. Christchurch Airbnb listing data from Inside Airbnb.
2. New Zealand rental bond data from Tenancy Services.

The purpose of the cleaning is to remove unnecessary information, standardise data types and formatting, retain useful variables, and prepare both datasets for comparison.

The datasets will later be used to compare rental prices and rental activity across Christchurch.

---

## 2. Datasets

### 2.1 Christchurch Airbnb Dataset

The Airbnb dataset contains Christchurch listings collected from Inside Airbnb.

The combined dataset covers:

* October 2025
* November 2025
* December 2025
* January 2026
* February 2026
* March 2026
* April 2026
* May 2026
* June 2026

The original combined Christchurch dataset contained approximately 28,795 listing records.

Important variables retained for later analysis include:

* `id` – unique listing identifier
* `name` – listing name
* `host_id` – host identifier
* `neighbourhood` – Christchurch neighbourhood
* `latitude` – listing latitude
* `longitude` – listing longitude
* `room_type` – type of accommodation
* `price` – nightly listing price
* `minimum_nights` – minimum required stay
* `number_of_reviews` – number of reviews
* `last_review` – date of the most recent review
* `reviews_per_month` – average monthly reviews
* `calculated_host_listings_count` – number of listings associated with the host

Latitude and longitude were deliberately retained because geographic information will be important for later analysis.

---

### 2.2 Tenancy Services Rental Bond Dataset

The second dataset comes from Tenancy Services' Detailed Quarterly Rental Bond Report.

The dataset contains quarterly rental bond information by location and dwelling characteristics.

Important variables retained include:

| Column                | Purpose                                           |
| --------------------- | ------------------------------------------------- |
| `TimeFrame`           | Identifies the quarter                            |
| `Location ID`         | Geographic identifier used for matching locations |
| `Dwelling Type`       | Type of dwelling                                  |
| `Total Bonds`         | Total number of bonds recorded                    |
| `Active Bonds`        | Number of active bonds                            |
| `Closed Bonds`        | Number of closed bonds                            |
| `Median Rent`         | Median weekly rent                                |
| `Geometric Mean Rent` | Geometric mean weekly rent                        |

`Location ID` and `TimeFrame` were retained because they are required for geographic and temporal alignment in the next stage of the project.

---

## 3. Airbnb Data Cleaning

The Airbnb cleaning script is:

```text
Deliverables/Deliverable-4/Deliverable-4.py
```

The following cleaning decisions were made.

### 3.1 Removed unnecessary columns

The following columns were removed:

* `neighbourhood_group`
* `license`
* `month/year`

`license` was removed because it was completely missing in the dataset.

`neighbourhood_group` contained only one distinct value, Christchurch City, so it provided little additional information because the dataset had already been restricted to Christchurch.

`month/year` was removed because it was not a reliable original scrape-date field and was treated as a temporary processing column.

### 3.2 Data type standardisation

The following columns were converted to integer types:

* `host_id`
* `calculated_host_listings_count`

`minimum_nights` was converted to pandas nullable integer type because some values were missing.

`last_review` was converted to a datetime format. Invalid date values are converted to missing datetime values rather than causing the script to fail.

### 3.3 Duplicate records

Exact duplicate rows were removed.

This prevents identical records from being counted more than once in later calculations.

A possible consequence is that a duplicate record could theoretically represent a legitimate repeated observation, but only exact duplicates were removed.

### 3.4 Text cleaning

Whitespace was removed from the following text columns:

* `name`
* `host_name`
* `neighbourhood`
* `room_type`

This improves consistency when filtering or grouping the data.

### 3.5 Missing values

Columns such as `price`, `last_review`, `reviews_per_month`, `minimum_nights`, and `host_name` contain some missing values.

These values were not automatically imputed.

This avoids creating artificial values that could affect later statistics. However, analyses using these columns must account for missing values.

---

## 4. Rental Bond Data Cleaning

The rental bond cleaning script is:

```text
Deliverables/Deliverable-4/clean_bond_data.py
```

### 4.1 Column selection

The final cleaned bond dataset contains eight columns:

```text
TimeFrame
Location ID
Dwelling Type
Total Bonds
Active Bonds
Closed Bonds
Median Rent
Geometric Mean Rent
```

The following variables were not retained because they were not required for the main rental price and volume comparison:

* `Log Std Dev Weekly Rent`
* `Upper Quantile Rent`
* `Lower Quantile Rent`

Removing these variables reduces unnecessary data while retaining the main measures required for the project.

### 4.2 String cleaning

Whitespace was removed from relevant string fields.

Column names were also stripped of unnecessary whitespace.

### 4.3 Numeric cleaning

Rental and bond-count fields were converted to numeric values.

Currency formatting such as `$` and commas was removed before numeric conversion where required.

### 4.4 Timeframe filtering

The cleaned dataset contains quarterly records from:

```text
January 2020
April 2020
July 2020
October 2020
...
October 2025
January 2026
April 2026
```

The current cleaned bond dataset contains **225,286 rows** across these quarterly periods.

---

## 5. Timeframe Alignment

The Airbnb dataset covers October 2025 to June 2026.

The rental bond dataset is quarterly, so the periods that overlap with the Airbnb dataset are:

* October 2025
* January 2026
* April 2026

The number of bond records in these overlapping periods is:

| TimeFrame    |       Rows |
| ------------ | ---------: |
| October 2025 |      9,427 |
| January 2026 |      9,222 |
| April 2026   |      8,469 |
| **Total**    | **27,118** |

Therefore, the common comparison period for the next stage is **October 2025 to April 2026**.

May and June 2026 Airbnb data do not have corresponding quarterly bond periods in the current bond dataset, so they should not be treated as directly matched periods.

---

## 6. Cleaning Consequences

The main consequences of the cleaning decisions are:

* Removing `license` loses no useful information because the column was completely missing.
* Removing `neighbourhood_group` removes a redundant city-level field because the dataset is already restricted to Christchurch.
* Removing `month/year` removes a temporary/non-reliable date field.
* Removing exact duplicate rows prevents duplicate records from affecting counts and statistics.
* Keeping missing values instead of imputing them avoids introducing fabricated information.
* Keeping latitude and longitude preserves the geographic information required for later analysis.
* Removing unnecessary bond columns reduces the dataset while retaining the main rental price and rental-volume measures.

---

## 7. Reproducibility

The cleaning code is stored in this directory:

```text
Deliverables/Deliverable-4/
```

Main scripts:

```text
Deliverable-4.py
clean_bond_data.py
```

The rental bond cleaned dataset is:

```text
cleaned_rental_bond_data.csv
```

The scripts use pandas for data processing.

The Python environment used during development contains pandas 3.0.5.

### Airbnb input data

The Airbnb cleaning script expects the combined Christchurch input dataset at:

```text
Deliverables/combined_listings_for_Christchurch/combined_Christchurch_listings.csv
```
After running this we will get the cleaned data.
---

## 8. Project Structure

The relevant Deliverable 4 files are:

```text
Deliverables/
└── Deliverable-4/
    ├── README.md
    ├── Deliverable-4.py
    ├── clean_bond_data.py
    ├── cleaned_rental_bond_data.csv
    ├── Deliverable-4.txt
    └── dropped_columns.txt
└── combined_Christchurch_listings_cleaned.csv

```

---

## 9. Team Contributions

### Connor – Airbnb Dataset Cleaning

* Cleaned the Christchurch Airbnb dataset.
* Reviewed unnecessary and missing columns.
* Standardised data types and text fields.
* Removed exact duplicate records.
* Preserved latitude and longitude.

### Johan – Rental Bond Dataset Cleaning

* Obtained and reviewed the Tenancy Services rental bond dataset.
* Selected relevant columns.
* Cleaned numeric and string fields.
* Prepared the cleaned rental bond dataset.

### Kaz – Dataset Integration

* Responsible for checking compatibility between the Airbnb and rental bond datasets.
* Checks timeframe and geographic compatibility.
* Prepares the datasets for the next-stage comparison.
* I suggested we keep "month_year" column not "last leview" column because the latter indicates only the date of the most recent review, not the dataset month.
* We may also need "month_year" column to align the Airbnb data with the quarterly bond data, which may be useful for the next week's work.
* I also suggested that we drop the "TimeFrame" column from 2020-01-01 to 2025-07-01 as these ranges of data will not be useful when we combine two datasets.

### Kayal – Documentation and Quality Assurance

* Prepared the Deliverable 4 README.
* Documented dataset sources and cleaning decisions.
* Recorded consequences of cleaning decisions.
* Checked timeframe compatibility.
* Checked reproducibility of the cleaning scripts.
* Reviewed GitHub/project organisation.
* Maintained project management documentation and Trello updates.
* Performed final quality checks before submission.

---

## 10. Next Stage

The next stage will combine the cleaned datasets where appropriate and compare:

* rental prices
* rental activity/volume
* geographic patterns
* changes across the common timeframe

Care must be taken when comparing Airbnb nightly prices with Tenancy Services rental figures because the two datasets measure different types of rental activity and use different time structures.
