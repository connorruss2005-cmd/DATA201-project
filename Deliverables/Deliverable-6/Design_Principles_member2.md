# Design Principles

## 1. Inputs

* Cleaned Airbnb Christchurch dataset
* Airbnb latitude and longitude
* Koordinates API
* Rental bond dataset

## 2. Outputs

* Airbnb dataset with an `area_code` column
* Merged Airbnb and rental bond dataset
* Graphs and analysis results

## 3. Main Steps

1. Clean the Airbnb data.
2. Get unique Airbnb latitude and longitude coordinates.
3. Use the Koordinates API to find the SA2 area code for each coordinate.
4. Add the area codes to the Airbnb data.
5. Join the Airbnb data with the rental bond data.
6. Analyse the combined data.
7. Create graphs and results.

## 4. Coding and Software Strategies

* Use functions for repeated tasks.
* Use clear variable names.
* Keep API keys outside the code.
* Use error handling and retries for API requests.
* Check the data after important steps.
* Check that the number of rows has not changed unexpectedly.
* Check for missing values.
* Validate data merges to make sure they work as expected.

## AI Used

ChatGPT (Kayal)
