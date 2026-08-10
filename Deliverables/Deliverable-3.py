# Packages we are using, please install them if you don't have them yet.
# Also be sure you have all the listings.csv files downloaded.
import numpy as np
import matplotlib.pyplot as plt # Not sure if we need this
import pandas as pd

df = pd.read_csv('listings.csv')
pd.set_option('display.max_columns', None)

# Convert last_review to datetime format
df['last_review'] = pd.to_datetime(df['last_review'])

# Create month + year column
df['month/year'] = df['last_review'].dt.strftime('%B %Y')

# Saves updated csv
df.to_csv('listings.csv', index=False)

print(df.head())