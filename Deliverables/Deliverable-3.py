# Packages we are using, please install them if you don't have them yet.
# Also be sure you have all the listings.csv files downloaded.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

listings_df = pd.read_csv('listings.csv')

print(listings_df.head())