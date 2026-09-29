# DATA201 Project - Design Principles

AI tool used: ???? I used ChatGPT(Kazushi).

## 1. Inputs

- Christchurch Airbnb listing data
- Rental Bond data
- Stats NZ SA2 data accessed through the Koordinates API

## 2. Outputs

- Cleaned Airbnb dataset
- Cleaned Rental Bond dataset
- Airbnb dataset with SA2 area codes
- Joined Airbnb and Rental Bond dataset
- Analysis results and visualisations

## 3. Main Pipeline Steps

1. Clean and standardise the Airbnb and Rental Bond datasets.
2. Convert Airbnb latitude and longitude into SA2 area codes using the Koordinates API.
3. Merge the SA2 area codes back into the Airbnb dataset.
4. Join Airbnb data with Rental Bond data using area codes.
5. Analyse rental prices and property counts.
6. Create visualisations for the results.

## 4. Coding and Software Strategies

- Use pathlib.Path for reliable file handling.
- Validate required columns before processing.
- Standardise data types before joining datasets.
- Remove duplicate records where appropriate.
- Use sanity checks to validate important outputs.
- Handle API errors and retry failed requests.
- Save intermediate mapping results to avoid unnecessary repeated API calls.