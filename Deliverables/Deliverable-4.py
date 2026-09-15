import pandas as pd

#Clean the Christchurch listing dataset you have created in Deliverable 3. It is up to you to decide what makes sense here. 
#You are welcome to drop columns if you think they are useless. Please keep latitude and longitude.
#Document your decisions, the reasons behind your decisions, and the consequences (e.g., number of rows lost due to missing value handling)

df = pd.read_csv('Deliverables/combined_listings_for_Christchurch/combined_Christchurch_listings.csv')
pd.set_option("display.max_columns", None)

#=====1. Dropped unnecessary columns: 'neighbourhood_group', 'license', and 'month/year'.=====
df.drop(columns=['neighbourhood_group', 
                 'license', 
                 'month/year'
                 ], inplace=True)

#=====2. Converted the following columns to integer type.=====
df[['host_id', 
    'calculated_host_listings_count'
    ]] = df[['host_id', 
             'calculated_host_listings_count'
             ]].astype('int64')

df['minimum_nights'] = df['minimum_nights'].astype('Int64') 
#Has a few NA's so convert to nullable integer type.

#=====3. Drop exact duplicate rows.=====
df.drop_duplicates(inplace=True)

#=====4. Clean up the text columns by stripping any whitespace.=====
text_columns = ['name', 'host_name', 'neighbourhood', 'room_type']
for col in text_columns:
    df[col] = df[col].str.strip()

#=====5. Convert 'last_review' column to datetime format handle errors by coercing invalid dates.=====
df['last_review'] = pd.to_datetime(df['last_review'], errors='coerce')

#=====6. Tidy up row order / index.=====
df = df.sort_values(['id', 'last_review'], na_position='last').reset_index(drop=True)

df.to_csv('Deliverables/combined_Christchurch_listings_cleaned.csv', index=False)