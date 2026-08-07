# DATA201-DATA422 project

Project Description
- This repository is used for our DATA201 and DATA422 group project.

Team members
- Connor 
- Kayal 
- Kazushi (exchange student)
- Johan 

Team Rules
- Nothing right now
- Let's all discuss and help each other
- 

How to interact with each other
- We will comunicate through WhatsApp group and meet in person when necessary.


## Dataset

### Source and provenance

This project uses the June 2026 New Zealand `listings.csv` dataset
provided by Inside Airbnb.

Inside Airbnb collects publicly available Airbnb listing information
from the Airbnb website. The dataset contains information about listings,
hosts, locations, prices, availability, and reviews.

- Data provider: Inside Airbnb
- Geographic coverage: New Zealand
- Dataset period: June 2026
- File used: `listings.csv`
- Collection method: Web-scraped Airbnb listing data
- Access date: 04/08/2026
- Original source: https://insideairbnb.com/get-the-data/
Due to its large size and the conditions associated with external data,
the dataset is stored locally in the `data` folder and is not included
in this GitHub repository. The `data` folder is listed in `.gitignore`.

### Dataset structure

Each row represents one Airbnb listing in New Zealand.

Each column represents a characteristic of the listing, host, location,
availability, or review history.

### Data dictionary

| Column | Description | Variable type | Expected values or format |
|---|---|---|---|
| id | Unique identifier for the Airbnb listing | Integer / Identifier | Positive integer |
| name | Name or title of the listing | Text | Free text |
| host_id | Unique identifier for the host | Integer / Identifier | Positive integer |
| host_name | Name of the host | Text | Free text or missing |
| neighbourhood_group | Larger geographical grouping, when available | Categorical text | Area name or missing |
| neighbourhood | Area in which the listing is located | Categorical text | Area name |
| latitude | Latitude coordinate of the listing | Float | Geographic coordinate |
| longitude | Longitude coordinate of the listing | Float | Geographic coordinate |
| room_type | Type of accommodation offered | Categorical text | Entire home/apt, Private room, Shared room, or Hotel room |
| price | Listed accommodation price | Numeric / Currency | Non-negative monetary value |
| minimum_nights | Minimum number of nights required for a booking | Integer | 1 or greater |
| number_of_reviews | Total number of reviews received | Integer | 0 or greater |
| last_review | Date of the most recent review | Date | Date value or missing |
| reviews_per_month | Average number of reviews received per month | Float | 0 or greater, or missing |
| calculated_host_listings_count | Number of listings associated with the host | Integer | 1 or greater |
| availability_365 | Number of available days during the next 365 days | Integer | 0–365 |
| number_of_reviews_ltm | Number of reviews received in the last 12 months | Integer | 0 or greater |
| license | Licence or registration information for the listing | Text | Licence value or missing |

### Missing values

Some columns may contain missing values. For example, listings that have
not received any reviews may have missing values in `last_review` and
`reviews_per_month`.

### Licence and repository handling

The dataset is treated as external data. The original CSV file and any
large derivative datasets are not uploaded to GitHub unless redistribution
is explicitly permitted by the dataset licence.

Team members should download the dataset directly from Inside Airbnb and
store it locally in:

`data/listings.csv`
